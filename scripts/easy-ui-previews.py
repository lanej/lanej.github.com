"""Build and verify revision-pinned Easy UI PR Storybooks under lanej.io."""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'lanej/easy-ui'


def read(url):
    request = Request(url, headers={'User-Agent': 'lanej-storybook-preview', 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=30) as response:
        return response.read()


def trusted_head(pr):
    assert pr['head']['repo'] and pr['head']['repo']['full_name'] == REPOSITORY, 'Unexpected fork'
    assert type(pr['number']) is int and pr['number'] > 0, 'Invalid PR number'
    sha = pr['head']['sha']
    assert re.fullmatch('[0-9a-f]{40}', sha), 'Invalid PR head SHA'
    return pr['number'], sha


def preview_heads():
    preserved = json.loads((ROOT / 'data/easy-ui-previews.json').read_text())
    assert all(type(number) is int and number > 0 for number in preserved)
    heads = {}
    page = 1
    while True:
        prs = json.loads(read(f'https://api.github.com/repos/{REPOSITORY}/pulls?state=open&per_page=100&page={page}'))
        for pr in prs:
            if pr['head']['repo'] and pr['head']['repo']['full_name'] == REPOSITORY:
                number, sha = trusted_head(pr)
                heads[number] = sha
        if len(prs) < 100:
            break
        page += 1
    for number in preserved:
        if number not in heads:
            pr = json.loads(read(f'https://api.github.com/repos/{REPOSITORY}/pulls/{number}'))
            actual, sha = trusted_head(pr)
            assert actual == number, 'Unexpected PR response'
            heads[number] = sha
    return sorted(heads.items())


def build(root):
    heads = preview_heads()
    destination = root / 'previews/easy-ui'
    destination.mkdir(parents=True, exist_ok=True)
    previews = []
    with tempfile.TemporaryDirectory(prefix='easy-ui-previews-') as temporary:
        checkout = Path(temporary) / 'easy-ui'
        subprocess.run(['git', 'clone', '--quiet', '--no-checkout', '--filter=blob:none',
                        f'https://github.com/{REPOSITORY}.git', str(checkout)], check=True)
        for number, sha in heads:
            subprocess.run(['git', '-C', str(checkout), 'fetch', '--quiet', '--depth=1', 'origin', sha], check=True)
            subprocess.run(['git', '-C', str(checkout), 'checkout', '--quiet', '--detach', sha], check=True)
            output = destination / f'pr-{number}'
            subprocess.run(['npm', 'ci', '--no-audit', '--no-fund'], cwd=checkout, check=True)
            # Docgen follows project references into dist; build declarations first.
            subprocess.run(['npm', 'run', 'build'], cwd=checkout, check=True)
            subprocess.run(['npm', 'run', 'build:storybook', '--', '--output-dir',
                            str(output / 'storybook')], cwd=checkout, check=True)
            files = ['index.html', 'iframe.html', 'index.json']
            digests = {name: hashlib.sha256((output / 'storybook' / name).read_bytes()).hexdigest()
                       for name in files}
            (output / 'revision.txt').write_text(sha + '\n')
            previews.append({'number': number, 'sha': sha, 'path': f'previews/easy-ui/pr-{number}/', 'files': digests})
            print(f'Built Easy UI PR #{number} at {sha}', flush=True)
    (destination / 'manifest.json').write_text(json.dumps({'previews': previews}, indent=2) + '\n')


def verify(root, base, output, chromium_path):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((root / 'previews/easy-ui/manifest.json').read_text())
    report = {'url': base, 'previews': []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(**({'executable_path': chromium_path, 'args': ['--no-sandbox']} if chromium_path else {}))
        try:
            for preview in manifest['previews']:
                url = urljoin(base.rstrip('/') + '/', preview['path'])
                for attempt in range(18):
                    try:
                        assert read(url + 'revision.txt').decode().strip() == preview['sha'], 'Stale preview revision'
                        for name, digest in preview['files'].items():
                            assert hashlib.sha256(read(url + 'storybook/' + name)).hexdigest() == digest, f'{name}: unexpected response bytes'
                        break
                    except Exception:
                        if attempt == 17:
                            raise
                        time.sleep(5)
                entries = json.loads(read(url + 'storybook/index.json'))['entries']
                story = next((name for name in ('components-linechart--default', 'components-chart--time-series') if name in entries), None)
                assert story, 'Missing chart story'
                for label, width in [('mobile', 390), ('desktop', 1440)]:
                    # Browser boot can race Pages/CDN propagation after the byte checks.
                    # Retry a fresh page; every successful attempt must pass all checks.
                    for attempt in range(3):
                        page = browser.new_page(viewport={'width': width, 'height': 900})
                        errors = []
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        try:
                            response = page.goto(
                                url + 'storybook/iframe.html?id=' + story +
                                '&viewMode=story&revision=' + preview['sha'],
                                wait_until='networkidle')
                            assert response and response.ok
                            page.locator('#storybook-root [data-chart-state="ready"] svg').first.wait_for(timeout=60000)
                            page.evaluate('document.fonts.ready')
                            assert not errors, errors
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Preview overflows horizontally'
                            assert not page.locator('.sb-errordisplay').is_visible(), 'Story failed'
                            page.screenshot(path=str(output / f'pr-{preview["number"]}-{label}.png'), full_page=True)
                            break
                        except Exception:
                            page.screenshot(path=str(output / f'pr-{preview["number"]}-{label}-attempt-{attempt + 1}.png'), full_page=True)
                            if attempt == 2:
                                raise
                            time.sleep(2)
                        finally:
                            page.close()
                report['previews'].append({'number': preview['number'], 'sha': preview['sha'], 'url': url + 'storybook/', 'story': story})
        finally:
            browser.close()
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['build', 'verify'])
    parser.add_argument('--root', type=Path, default=ROOT / 'public')
    parser.add_argument('--url', default='http://127.0.0.1:8765/')
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/easy-ui-previews')
    parser.add_argument('--chromium-path', default='')
    args = parser.parse_args()
    if args.command == 'build':
        build(args.root.resolve())
    else:
        verify(args.root.resolve(), args.url, args.output, args.chromium_path)


if __name__ == '__main__':
    main()
