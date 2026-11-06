"""Render owned website PRs, deploy through the existing Pages job, then link them."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'lanej/lanej.github.com'
DOMAIN = 'https://lanej.io'
START, END = '<!-- site-preview:start -->', '<!-- site-preview:end -->'
FAST_PATHS = {'AGENTS.md', 'docs/development.md', '.github/workflows/pages.yml',
              '.github/workflows/site-preview-refresh.yml',
              'scripts/site-pr-previews.py', 'scripts/test-site-pr-previews.py'}


def read(url, data=None, method=None):
    request = Request(url, data=json.dumps(data).encode() if data is not None else None,
                      method=method, headers={'User-Agent':'lanej-site-preview',
                                             'Cache-Control':'no-cache'})
    if urlsplit(url).netloc == 'api.github.com':
        token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
        if token:
            request.add_unredirected_header('Authorization', 'Bearer ' + token)
        request.add_header('Accept', 'application/vnd.github+json')
        request.add_header('Content-Type', 'application/json')
        request.add_header('X-GitHub-Api-Version', '2022-11-28')
    with urlopen(request, timeout=30) as response:
        return response.read()


def api(path, data=None, method=None):
    return json.loads(read(f'https://api.github.com/repos/{REPOSITORY}/{path}', data, method))


def trusted(pr):
    number, sha = pr['number'], pr['head']['sha']
    assert type(number) is int and number > 0, 'Invalid PR number'
    assert re.fullmatch('[0-9a-f]{40}', sha), 'Invalid PR revision'
    assert pr['head']['repo'] and pr['head']['repo']['full_name'] == REPOSITORY, 'Fork preview refused'
    return number, sha


def open_prs():
    result, page = [], 1
    while True:
        values = api(f'pulls?state=open&per_page=100&page={page}')
        result.extend(pr for pr in values if pr['head']['repo'] and
                      pr['head']['repo']['full_name'] == REPOSITORY)
        if len(values) < 100:
            return result
        page += 1


def production_artifact():
    runs = api('actions/workflows/pages.yml/runs?branch=master&status=success&per_page=20')
    for run in runs['workflow_runs']:
        artifacts = api(f'actions/runs/{run["id"]}/artifacts')['artifacts']
        for artifact in artifacts:
            if artifact['name'] == 'site-bundle' and not artifact['expired']:
                return artifact['id']
    return None


def fast_refresh(event, changed):
    if event.get('inputs', {}).get('preview_refresh') in (True, 'true'):
        return True
    return bool(changed) and all(path in FAST_PATHS for path in changed)


def mode():
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    changed = []
    if os.getenv('GITHUB_EVENT_NAME') == 'pull_request':
        pr = event['pull_request']
        if not pr['head']['repo'] or pr['head']['repo']['full_name'] != REPOSITORY:
            print('preview_refresh=false\nproduction_artifact=')
            return
        changed = subprocess.check_output(['git','diff','--name-only',pr['base']['sha'],
                                          pr['head']['sha']],text=True).splitlines()
    elif os.getenv('GITHUB_EVENT_NAME') == 'push' and event.get('before') != '0' * 40:
        changed = subprocess.check_output(['git', 'diff', '--name-only', event['before'],
                                          os.environ['GITHUB_SHA']], text=True).splitlines()
    artifact = production_artifact() if fast_refresh(event, changed) else None
    print('preview_refresh=' + ('true' if artifact else 'false'))
    print('production_artifact=' + str(artifact or ''))


def restore(root, artifact_id):
    live = json.loads(read(DOMAIN + '/build.json'))
    archive = read(f'https://api.github.com/repos/{REPOSITORY}/actions/artifacts/{artifact_id}/zip')
    root.mkdir(parents=True, exist_ok=True)
    with ZipFile(io.BytesIO(archive)) as zipped:
        for item in zipped.infolist():
            path = PurePosixPath(item.filename)
            assert not path.is_absolute() and '..' not in path.parts, 'Artifact path escapes output'
            assert (item.external_attr >> 16) & 0o170000 != 0o120000, 'Artifact contains a symlink'
        zipped.extractall(root)
    cached = json.loads((root / 'build.json').read_text())
    assert cached == live, 'Cached bundle is not the currently published production revision'
    for path, digest in cached['files'].items():
        assert hashlib.sha256((root / path.lstrip('/')).read_bytes()).hexdigest() == digest
    print('Restored the verified production bundle at ' + cached['revision'])


def build_environment(sha):
    allowed = {'PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL', 'SSL_CERT_FILE', 'SSL_CERT_DIR',
               'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY',
               'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy'}
    env = {key:value for key,value in os.environ.items() if key in allowed}
    env.update(HUGO_PARAMS_REVISION=sha, HUGO_PARAMS_PREVIEW='true', HUGO_RELATIVEURLS='true')
    return env


def entry_route(files, output):
    candidates = []
    for item in files:
        name = item['filename']
        if not name.startswith('content/') or not name.endswith('.md'):
            continue
        path = name.removeprefix('content/').removesuffix('.md')
        path = re.sub(r'(^|/)_?index$', '', path).strip('/')
        route = '/' + path + '/' if path else '/'
        if (output / (route.lstrip('/') + 'index.html')).is_file():
            candidates.append(route)
    return sorted(candidates, key=lambda route:(not route.startswith('/writing/'), route == '/writing/', route))[0] if candidates else '/'


def render(checkout, output, sha, hugo):
    subprocess.run([hugo,'--source',str(checkout),'--destination',str(output),
                    '--baseURL='+DOMAIN+'/', '--buildDrafts','--buildFuture',
                    '--minify','--cleanDestinationDir','--panicOnWarning'],
                   env=build_environment(sha), check=True)
    for page in output.rglob('*.html'):
        text = page.read_text()
        metadata = f'<meta name="preview-revision" content="{sha}"><meta name="robots" content="noindex, nofollow">'
        page.write_text(text.replace('<head>', '<head>'+metadata, 1))


def build(root, manifest_path):
    prs = open_prs()
    destination = root / 'previews/site'
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    manifest = {'previews':[], 'errors':[]}
    hugo = str(Path(os.getenv('HUGO_BIN', str(ROOT / '.tools/hugo'))).resolve())
    with tempfile.TemporaryDirectory(prefix='site-pr-previews-') as temporary:
        checkout = Path(temporary) / 'source'
        subprocess.run(['git','clone','--quiet','--no-checkout','--filter=blob:none',
                        f'https://github.com/{REPOSITORY}.git',str(checkout)],
                       env=build_environment(''), check=True)
        for pr in prs:
            number, sha = trusted(pr)
            output = destination / f'pr-{number}'
            try:
                env = build_environment(sha)
                subprocess.run(['git','-C',str(checkout),'fetch','--quiet','--depth=1','origin',sha], env=env, check=True)
                subprocess.run(['git','-C',str(checkout),'checkout','--quiet','--force','--detach',sha], env=env, check=True)
                subprocess.run(['git','-C',str(checkout),'clean','--quiet','-ffdx'], env=env, check=True)
                # Build only with the publisher's pinned Hugo, never PR scripts.
                # Root-relative source conditionals stay correct; relative URLs
                # make this complete snapshot portable under its preview prefix.
                render(checkout, output, sha, hugo)
                files = []
                page = 1
                while True:
                    values = api(f'pulls/{number}/files?per_page=100&page={page}')
                    files.extend(values)
                    if len(values) < 100:
                        break
                    page += 1
                entry = entry_route(files, output)
                assert (output / (entry.lstrip('/')+'index.html')).is_file()
                (output / 'revision.txt').write_text(sha+'\n')
                paths = [path for path in output.rglob('*') if path.is_file()]
                assert not any(path.is_symlink() for path in output.rglob('*')), 'Preview contains a symlink'
                hashes = {'/'+path.relative_to(root).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
                manifest['previews'].append({'number':number,'sha':sha,'entry':entry,
                    'prefix':f'/previews/site/pr-{number}/','files':hashes})
            except (OSError, ValueError, AssertionError, subprocess.CalledProcessError) as error:
                shutil.rmtree(output, ignore_errors=True)
                manifest['errors'].append({'number':number,'sha':sha,'error':str(error)})
                print(f'Preview #{number} could not build: {error}', flush=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Built {len(manifest["previews"])} website previews; {len(manifest["errors"])} isolated failures.')


def preview_section(body, record, base=DOMAIN):
    url = base.rstrip('/') + record['prefix'] + record['entry'].lstrip('/')
    section = f'{START}\n[Preview this PR]({url}) · revision `{record["sha"][:12]}`\n{END}'
    if START in body and END in body:
        before, rest = body.split(START, 1)
        _, after = rest.split(END, 1)
        return before + section + after
    self_link = f'[Open PR #{record["number"]} on GitHub](https://github.com/{REPOSITORY}/pull/{record["number"]})\n\n'
    return section+'\n\n'+body.removeprefix(self_link)


def verify_record(record, base, output, browser):
    from PIL import Image
    prefix, sha = record['prefix'], record['sha']
    for attempt in range(18):
        try:
            if read(base.rstrip('/')+prefix+'revision.txt?revision='+sha).decode().strip() == sha:
                break
        except Exception:
            pass
        time.sleep(5)
    else:
        raise AssertionError(f'Preview #{record["number"]} has not reached {sha}')
    def check(item):
        path, digest = item
        data = read(base.rstrip('/')+path+'?revision='+sha)
        assert hashlib.sha256(data).hexdigest() == digest, f'{path}: wrong deployed bytes'
        if path.lower().endswith(('.jpg','.jpeg','.webp','.png','.gif','.ico')):
            with Image.open(io.BytesIO(data)) as image:
                image.load()
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(check, record['files'].items()))
    url = base.rstrip('/')+prefix+record['entry'].lstrip('/')
    for label, width, height in [('mobile',390,844),('desktop',1440,1000)]:
        page = browser.new_page(viewport={'width':width,'height':height})
        try:
            response = page.goto(url+'?revision='+sha, wait_until='networkidle')
            assert response and response.ok
            assert page.locator('meta[name="preview-revision"]').get_attribute('content') == sha
            assert page.locator('h1').count() == 1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=str(output/f'pr-{record["number"]}-{label}.png'))
        finally:
            page.close()
    return {'number':record['number'],'sha':sha,'url':url,'files':len(record['files'])}


def verify(root, manifest_path, base, output, chromium_path, publish):
    from playwright.sync_api import sync_playwright
    manifest = json.loads(manifest_path.read_text())
    output.mkdir(parents=True, exist_ok=True)
    results, errors = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=chromium_path or None, args=['--no-sandbox'])
        for record in manifest['previews']:
            try:
                results.append(verify_record(record, base, output, browser))
            except Exception as error:
                errors.append({'number':record['number'],'sha':record['sha'],'error':str(error)})
                print(f'Preview #{record["number"]} failed verification: {error}', flush=True)
        browser.close()
    report = {'status':'partial' if errors else 'passed', 'previews':results, 'errors':errors}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if publish:
        current = {pr['number']:pr for pr in open_prs()}
        verified = {record['number'] for record in results}
        for record in manifest['previews']:
            if record['number'] not in verified:
                continue
            pr = current.get(record['number'])
            if not pr or trusted(pr)[1] != record['sha']:
                continue
            issue = api(f'issues/{record["number"]}')
            body = preview_section(issue.get('body') or '', record, base)
            api(f'issues/{record["number"]}', {'body':body}, 'PATCH')
    print(json.dumps(dict(report,published_links=publish)))
    if errors and not results:
        raise AssertionError('No website PR preview passed verification')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['mode','restore','build','verify'])
    parser.add_argument('--root', type=Path, default=ROOT/'public')
    parser.add_argument('--manifest', type=Path, default=ROOT/'artifacts/site-pr-previews.json')
    parser.add_argument('--artifact-id', type=int)
    parser.add_argument('--url', default=DOMAIN)
    parser.add_argument('--output', type=Path, default=ROOT/'artifacts/live/site-pr-previews')
    parser.add_argument('--chromium-path', default='')
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    if args.command == 'mode': mode()
    elif args.command == 'restore': restore(args.root, args.artifact_id)
    elif args.command == 'build': build(args.root.resolve(), args.manifest)
    else: verify(args.root, args.manifest, args.url, args.output, args.chromium_path, args.publish)


if __name__ == '__main__':
    main()
