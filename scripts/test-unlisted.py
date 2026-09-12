"""One lifecycle regression: unlisted review copy -> public essay -> offline draft."""
import argparse
import functools
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from check import Document

ROOT = Path(__file__).resolve().parent.parent
SLUG = 'unlisted-review-fixture'
ROUTE = f'/writing/{SLUG}/'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hugo', default='.tools/hugo')
    parser.add_argument('--chromium-path', default=shutil.which('google-chrome') or shutil.which('google-chrome-stable'))
    args = parser.parse_args()
    hugo = str(Path(args.hugo).resolve())
    env = dict(os.environ, HUGO_PARAMS_REVISION=os.environ.get('GITHUB_SHA', 'local'))
    screenshots = ROOT / 'artifacts/smoke'

    with tempfile.TemporaryDirectory(prefix='lanej-unlisted-') as temporary:
        site = Path(temporary)
        for name in ('archetypes', 'assets', 'content', 'data', 'layouts', 'static'):
            shutil.copytree(ROOT / name, site / name)
        for name in ('hugo.toml', 'CNAME'):
            shutil.copy2(ROOT / name, site / name)
        subprocess.run([hugo, 'new', 'content', '--kind', 'unlisted', f'writing/{SLUG}/index.md'], cwd=site, env=env, check=True)
        source = site / f'content/writing/{SLUG}/index.md'
        frontmatter = source.read_text().split('+++')[1].rstrip()
        source.write_text('+++\n' + frontmatter + '\nessay_visual = "memory"\n+++\n\n'
                          '> A review copy should work before it is announced.\n\n'
                          'This disposable essay exercises the real publishing path.\n\n'
                          '## Review the argument\n\n'
                          'The same URL becomes public when the unlisted flag is removed.\n\n'
                          '[Supporting note](review-note.txt).\n')
        (source.parent / 'review-note.txt').write_text('A resource that must not appear in the public build manifest.\n')
        public = site / 'public'
        article = public / ROUTE.strip('/') / 'index.html'
        public_surfaces = ('index.html', 'writing/index.html', 'index.xml', 'writing/index.xml', 'sitemap.xml', 'robots.txt', 'build.json')

        def build():
            subprocess.run([hugo, '--minify', '--cleanDestinationDir', '--panicOnWarning'], cwd=site, env=env, check=True)
            subprocess.run([sys.executable, str(ROOT / 'scripts/check.py'), str(public)], cwd=site, env=env, check=True)

        build()
        doc = Document(article.read_text())
        assert doc.select('article', **{'data-visibility': 'unlisted'})
        assert 'noindex' in doc.select('meta', name='robots')[0]['content']
        assert doc.select('span', **{'class': 'sc-preview-state'}), 'Missing unlisted draft label'
        assert (article.parent / 'review-note.txt').exists(), 'Review resources must remain available'
        for name in public_surfaces:
            assert SLUG not in (public / name).read_text(), f'Unlisted URL exposed by {name}'

        if args.chromium_path:
            from playwright.sync_api import sync_playwright
            handler = functools.partial(SimpleHTTPRequestHandler, directory=str(public))
            server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                screenshots.mkdir(parents=True, exist_ok=True)
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(executable_path=args.chromium_path, args=['--no-sandbox'])
                    for width in (390, 1440):
                        page = browser.new_page(viewport={'width': width, 'height': 900}, color_scheme='dark')
                        response = page.goto(f'http://127.0.0.1:{server.server_port}{ROUTE}', wait_until='networkidle')
                        assert response and response.ok, 'Direct review URL failed'
                        assert page.locator('.sc-preview-state').inner_text().casefold().startswith('draft')
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Review layout overflows'
                        page.screenshot(path=str(screenshots / f'unlisted-draft-{width}.png'))
                        page.close()
                    browser.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

        source.write_text(source.read_text().replace('unlisted = true', 'unlisted = false'))
        build()
        doc = Document(article.read_text())
        assert not doc.select('meta', name='robots'), 'Publishing left the noindex directive behind'
        assert not doc.select('span', **{'class': 'sc-preview-state'}), 'Publishing left the draft label behind'
        for name in public_surfaces:
            if name != 'robots.txt':
                assert SLUG in (public / name).read_text(), f'Published essay missing from {name}'

        source.write_text(source.read_text().replace('draft = false', 'draft = true'))
        build()
        assert not article.exists(), 'Offline draft or stale published output was rendered'
        for name in public_surfaces:
            assert SLUG not in (public / name).read_text(), f'Offline draft exposed by {name}'
    print('Passed: unlisted URL, discovery exclusions, publication at the same URL, and offline draft removal.')


if __name__ == '__main__':
    main()
