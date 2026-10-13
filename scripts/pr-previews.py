"""Capture rendered changes from a PR, excluding unchanged verification pages."""
import argparse
import base64
import html
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from urllib.parse import unquote, urlsplit

from affected_pages import affected_routes, changed_paths, change_base

START = '<!-- page-previews:start -->'
END = '<!-- page-previews:end -->'


class PageAssets(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.paths = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        urls = []
        if tag in ('img', 'script', 'source', 'video', 'audio'):
            urls.extend(attrs.get(name, '') for name in ('src', 'poster'))
            urls.extend(item.strip().split()[0] for item in attrs.get('srcset', '').split(',') if item.strip())
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'icon', 'apple-touch-icon'):
            urls.append(attrs.get('href', ''))
        for url in urls:
            parsed = urlsplit(url)
            if not parsed.scheme and not parsed.netloc and parsed.path:
                self.paths.add(unquote(parsed.path))


def rendered_changes(routes, current, baseline):
    """Do not mistake verification scope or unchanged asset URLs for page changes."""
    selected = []
    for route in routes:
        relative = route.lstrip('/') + 'index.html' if route.endswith('/') else route.lstrip('/')
        new, old = current / relative, baseline / relative
        if not new.is_file():
            continue
        if not old.is_file() or new.read_bytes() != old.read_bytes():
            selected.append(route)
            continue
        for asset in PageAssets(new.read_text()).paths:
            relative_asset = asset.lstrip('/') if asset.startswith('/') else str(Path(relative).parent / asset)
            new_asset, old_asset = current / relative_asset, baseline / relative_asset
            if new_asset.is_file() and (not old_asset.is_file() or new_asset.read_bytes() != old_asset.read_bytes()):
                selected.append(route)
                break
    return selected


def changed_preview_routes(root, base, available):
    paths = changed_paths(root, base, committed_only=True)
    candidates = affected_routes(paths, available, root=root, base=base)
    if not candidates:
        return []
    with tempfile.TemporaryDirectory(prefix='pr-preview-base-') as temporary:
        source = Path(temporary) / 'source'
        subprocess.run(['git', 'worktree', 'add', '--detach', str(source), base], cwd=root, check=True)
        try:
            # CI refreshes activity for deployment; it is not an authored PR change.
            activity = 'data/github_activity.json'
            if activity not in paths and (root / activity).is_file():
                shutil.copyfile(root / activity, source / activity)
            public = Path(temporary) / 'public'
            hugo = Path(os.environ.get('HUGO_BIN', str(root / '.tools/hugo'))).resolve()
            subprocess.run([str(hugo), '--source', str(source), '--destination', str(public),
                            '--gc', '--minify', '--cleanDestinationDir', '--panicOnWarning'],
                           cwd=root, env=dict(os.environ, HUGO_PARAMS_REVISION=os.environ['GITHUB_SHA']), check=True)
            return rendered_changes(candidates, root / 'public', public)
        finally:
            subprocess.run(['git', 'worktree', 'remove', '--force', str(source)], cwd=root, check=True)


def available_routes(public):
    # App previews are added after Hugo's validated manifest and have their own CI.
    files = json.loads((public / 'build.json').read_text())['files']
    routes = {name.removesuffix('index.html') for name in files if name.endswith('/index.html')}
    if '/404.html' in files:
        routes.add('/404.html')
    return routes


def replace_section(body, section):
    if START in body and END in body:
        before, rest = body.split(START, 1)
        _, after = rest.split(END, 1)
        return before + section + after
    if not section:
        return body
    return body.rstrip() + '\n\n' + section + '\n'


def capture(args):
    from playwright.sync_api import sync_playwright

    available = available_routes(Path('public'))
    root = Path.cwd()
    base = change_base(root, args.base)
    routes = changed_preview_routes(root, base, available)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {'head_sha': os.environ['PR_HEAD_SHA'],
                'build_sha': os.environ['GITHUB_SHA'], 'pages': []}
    if not routes:
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        print('No affected pages; skipping browser preview capture.')
        return
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=args.chromium_path or None)
        for route in routes:
            slug = route.strip('/').replace('/', '-') or 'home'
            item = {'route': route, 'images': {}}
            for label, width, height in [('mobile', 390, 844), ('desktop', 1440, 1000)]:
                page = browser.new_page(viewport={'width': width, 'height': height},
                                        device_scale_factor=1, color_scheme='dark',
                                        reduced_motion='reduce')
                response = page.goto('http://127.0.0.1:8765' + route, wait_until='networkidle')
                assert response and response.ok, route
                page.evaluate('document.fonts.ready')
                if route in ('/record/', '/open-source/'):
                    page.locator('.work-logo img').evaluate_all(
                        '(images) => Promise.all(images.map(image => image.decode()))')
                    assert page.locator('.project-logo img').count() == page.locator('.contribution').count(), 'Every project needs a GitHub avatar'
                    assert page.locator('.event-logo img').count() == page.locator('.speaking-engagement').count(), 'Every speaking engagement needs its event logo'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), route
                assert page.locator('meta[name="site-revision"]').get_attribute('content') == manifest['build_sha']
                item['title'] = page.locator('h1').inner_text()
                filenames = {'viewport': f'{slug}-{label}.png', 'full': f'{slug}-{label}-full.png'}
                page.screenshot(path=str(out / filenames['viewport']), animations='disabled')
                page.screenshot(path=str(out / filenames['full']), full_page=True, animations='disabled')
                if route == '/record/':
                    filenames['detail'] = f'{slug}-{label}-companies.png'
                    page.locator('.career-company[data-company="easypost"]').screenshot(
                        path=str(out / filenames['detail']), animations='disabled')
                    if page.locator('.speaking-engagement').count():
                        filenames['speaking'] = f'{slug}-{label}-speaking.png'
                        page.locator('.speaking-engagement').screenshot(
                            path=str(out / filenames['speaking']), animations='disabled')
                if route == '/open-source/':
                    filenames['projects'] = f'{slug}-{label}-projects.png'
                    page.locator('.contributions').screenshot(
                        path=str(out / filenames['projects']), animations='disabled')
                item['images'][label] = filenames
                page.close()
            manifest['pages'].append(item)
        browser.close()
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(f'Captured {len(routes)} affected pages at mobile and desktop sizes.')


def preview_section(manifest, image_root, run_url):
    lines = [START, '## Changed pages',
             f'PR revision `{manifest["head_sha"][:12]}` · [CI build]({run_url})', '']
    if not manifest['pages']:
        lines.append('No rendered page changes detected.')
    for page in manifest['pages']:
        title = html.escape(page['title'])
        lines += [f'<details><summary>{title} — {html.escape(page["route"])}</summary>', '',
                  '| Mobile · 390px | Desktop · 1440px |', '| --- | --- |']
        cells = []
        for label, width in [('mobile', 240), ('desktop', 600)]:
            images = page['images'][label]
            src = image_root + '/' + images['viewport']
            full = image_root + '/' + images['full']
            cells.append(f'<a href="{full}"><img src="{src}" width="{width}" alt="{title}: {label} preview"></a>')
        lines += ['| ' + ' | '.join(cells) + ' |', '',
                  'Select an image to open the full-page screenshot.', '']
        for key, heading, alt in (('detail', 'EasyPost: roles and descriptions', 'EasyPost career details'),
                                  ('projects', 'Open-source projects', 'Open-source projects'),
                                  ('speaking', 'Speaking engagements', 'Speaking engagement')):
            if not all(key in page['images'][label] for label in ('mobile', 'desktop')):
                continue
            lines += [f'**{heading}**', '',
                      '| Mobile | Desktop |', '| --- | --- |']
            details = []
            for label, width in [('mobile', 240), ('desktop', 600)]:
                src = image_root + '/' + page['images'][label][key]
                details.append(f'<img src="{src}" width="{width}" alt="{alt}: {label}">')
            lines += ['| ' + ' | '.join(details) + ' |', '']
        lines += ['</details>', '']
    lines.append(END)
    return '\n'.join(lines)


def publish(args):
    repo = os.environ['GITHUB_REPOSITORY']
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    pr_number = event['pull_request']['number']
    expected = event['pull_request']['head']['sha']
    assert event['pull_request']['head']['repo']['full_name'] == repo, 'Forks are artifact-only.'
    out = Path(args.output)
    manifest = json.loads((out / 'manifest.json').read_text())
    assert manifest['head_sha'] == expected
    assert manifest['build_sha'] == os.environ['GITHUB_SHA']

    def api(path, data=None, method=None):
        request = Request('https://api.github.com/repos/' + repo + '/' + path,
                          data=json.dumps(data).encode() if data is not None else None,
                          method=method or ('POST' if data is not None else 'GET'),
                          headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                                   'Accept': 'application/vnd.github+json',
                                   'Content-Type': 'application/json',
                                   'X-GitHub-Api-Version': '2022-11-28'})
        with urlopen(request) as response:
            return json.load(response)

    current = api(f'pulls/{pr_number}')
    if current['head']['sha'] != expected or current['state'] != 'open':
        print('Skipping superseded or closed PR.')
        return
    if not manifest['pages']:
        body = current.get('body') or ''
        updated = replace_section(body, '')
        if updated != body:
            api(f'pulls/{pr_number}', {'body': updated}, 'PATCH')
        print(f'PR #{pr_number} has no changed pages; removed stale previews.')
        return
    # Separate per-PR branches keep screenshots out of the website source/build.
    branch = f'pr-previews/{pr_number}'
    parent = None
    try:
        parent = api('git/ref/heads/' + branch)['object']['sha']
    except HTTPError as error:
        if error.code != 404:
            raise
    entries = []
    for path in sorted(out.glob('*.png')):
        blob = api('git/blobs', {'content': base64.b64encode(path.read_bytes()).decode(), 'encoding': 'base64'})
        entries.append({'path': path.name, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    entries.append({'path': 'manifest.json', 'mode': '100644', 'type': 'blob',
                    'content': json.dumps(manifest, indent=2)})
    tree = api('git/trees', {'tree': entries})
    commit = api('git/commits', {'message': f'PR #{pr_number} previews for {expected}',
                               'tree': tree['sha'], 'parents': [parent] if parent else []})
    if parent:
        api('git/refs/heads/' + branch, {'sha': commit['sha']}, 'PATCH')
    else:
        api('git/refs', {'ref': 'refs/heads/' + branch, 'sha': commit['sha']})
    # Read the latest body to retain human edits and reject stale captures.
    current = api(f'pulls/{pr_number}')
    if current['head']['sha'] != expected or current['state'] != 'open':
        print('Skipping superseded or closed PR body update.')
        return
    image_root = f'https://raw.githubusercontent.com/{repo}/{commit["sha"]}'
    run_url = f'https://github.com/{repo}/actions/runs/{os.environ["GITHUB_RUN_ID"]}'
    section = preview_section(manifest, image_root, run_url)
    api(f'pulls/{pr_number}', {'body': replace_section(current.get('body') or '', section)}, 'PATCH')
    print(f'Updated PR #{pr_number} with {len(manifest["pages"])} page previews.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['capture', 'publish'])
    parser.add_argument('--output', default='artifacts/pr-previews')
    parser.add_argument('--base')
    parser.add_argument('--chromium-path', default='')
    arguments = parser.parse_args()
    if arguments.command == 'capture' and not arguments.base:
        parser.error('capture requires --base')
    {'capture': capture, 'publish': publish}[arguments.command](arguments)
