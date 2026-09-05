"""Exercise publishing in a temporary copy. Never commit or deploy test articles."""
import argparse
import functools
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

SOURCE = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--engines', default='')
    parser.add_argument('--chromium-path', default='')
    args = parser.parse_args()
    binary = Path(os.environ.get('HUGO_BIN', '.tools/hugo'))
    if not binary.is_absolute():
        located = shutil.which(str(binary))
        binary = Path(located) if located else SOURCE / binary
    binary = binary.resolve()
    out = SOURCE / 'artifacts/local/writing-fixture'
    out.mkdir(parents=True, exist_ok=True)
    checks = []
    with tempfile.TemporaryDirectory(prefix='lanej-writing-') as directory:
        repo = Path(directory) / 'repo'
        shutil.copytree(SOURCE, repo, ignore=shutil.ignore_patterns('.git', '.tools', '.venv', 'public', 'resources', 'artifacts', '__pycache__', '.hugo_build.lock'))
        # Synthetic coverage is independent of any real writing in the repository.
        shutil.rmtree(repo / 'content/writing', ignore_errors=True)
        writing = repo / 'content/writing'
        env = {**os.environ, 'HUGO_BIN': str(binary), 'GITHUB_SHA': 'writing-fixture', 'HUGO_PARAMS_REVISION': 'writing-fixture'}

        def build(ok=True):
            result = subprocess.run(['bash', 'scripts/build.sh'], cwd=repo, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if ok and result.returncode:
                raise AssertionError(result.stdout)
            if not ok:
                assert result.returncode, 'Incomplete article unexpectedly published'
            return result

        def post(slug, date, draft, title):
            folder = writing / slug
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / 'index.md'
            path.write_text(f'---\ntitle: {title}\ndate: "{date}"\ndescription: A verification article, never production content.\ndraft: {str(draft).lower()}\ntoc: true\n---\n\nA useful introduction.\n\n## The decision\n\nA paragraph with a [local link](/about/), **emphasis**, and a footnote.[^1]\n\n```go\n// '+('long-line-' * 30)+'\nfunc main() {}\n```\n\n> A block quotation.\n\n| Choice | Result |\n| --- | --- |\n| Simple | Testable |\n\n[^1]: A source note.\n')
            return path

        draft = post('hidden-draft', '2020-01-01T00:00:00Z', True, 'UNPUBLISHED_DRAFT_SENTINEL')
        future = post('future-article', '2099-01-01T00:00:00Z', False, 'UNPUBLISHED_FUTURE_SENTINEL')
        build()
        assert not (repo / 'public/writing/index.html').exists()
        checks.append('Draft-only and future-only content does not create a public archive')

        subprocess.run([str(binary), 'new', 'content', '--kind', 'writing', 'writing/new-essay/index.md'], cwd=repo, check=True, capture_output=True)
        new = writing / 'new-essay/index.md'
        assert 'draft: true' in new.read_text()
        checks.append('New-article archetype defaults to draft')
        new.unlink()

        published = post('sample-essay', '2020-01-02T00:00:00Z', False, 'Writing verification sample')
        with published.open('a') as file:
            file.write('\n![A rectangular image used only in tests](diagram.png)\n')
        Image.new('RGB', (600, 180), '#acc8b7').save(published.parent / 'diagram.png')
        build()
        public = repo / 'public'
        html = (public / 'writing/sample-essay/index.html').read_text()
        archive = (public / 'writing/index.html').read_text()
        home = (public / 'index.html').read_text()
        assert 'Writing verification sample' in archive and '/writing/sample-essay/' in home
        assert 'BlogPosting' in html and 'article:published_time' in html
        assert 'id=the-decision' in html or 'id="the-decision"' in html
        assert 'header-portrait' in html and 'article-toc' in html
        rss = ET.parse(public / 'writing/index.xml')
        items = rss.findall('./channel/item')
        assert len(items) == 1 and items[0].findtext('title') == 'Writing verification sample'
        assert '<p>' in items[0].findtext('description') and 'A useful introduction.' in items[0].findtext('description')
        for page in public.rglob('*'):
            if page.is_file() and page.suffix in {'.html', '.xml', '.json'}:
                text = page.read_text()
                assert 'UNPUBLISHED_DRAFT_SENTINEL' not in text and 'UNPUBLISHED_FUTURE_SENTINEL' not in text
        assert not (public / 'writing/hidden-draft').exists()
        assert not (public / 'writing/future-article').exists()
        checks.append('Published page, archive, homepage discovery, full-content RSS, metadata, anchors, and media')
        checks.append('Draft and future text absent from pages, sitemap, RSS, and manifest')

        original = published.read_text()
        published.write_text(original.replace('description: A verification article, never production content.', "description: ''"))
        assert 'needs a description' in build(ok=False).stdout
        published.write_text(original.split('---', 2)[0] + '---' + original.split('---', 2)[1] + '---\n')
        assert 'is empty' in build(ok=False).stdout
        checks.append('Missing descriptions and empty published articles fail the build')

        published.write_text(original.replace('draft: false', 'draft: true'))
        build()
        assert not (public / 'writing/index.html').exists() and not (public / 'writing/sample-essay/index.html').exists()
        checks.append('Withdrawing the last article removes stale pages, archive, and feed')
        published.write_text(original)
        build()

        if args.engines:
            class QuietHandler(http.server.SimpleHTTPRequestHandler):
                def log_message(self, *args):
                    pass
            handler = functools.partial(QuietHandler, directory=str(public))
            server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            command = [sys.executable, str(SOURCE / 'scripts/verify.py'), '--root', str(public), '--url', f'http://127.0.0.1:{server.server_port}/', '--output', str(out), '--engines', args.engines]
            if args.chromium_path:
                command.extend(['--chromium-path', args.chromium_path])
            try:
                subprocess.run(command, cwd=repo, env=env, check=True)
            finally:
                server.shutdown()
                server.server_close()
        (out / 'publishing-tests.json').write_text(json.dumps({'status': 'passed', 'checks': checks, 'fixtures_deployed': False}, indent=2))
        print('Writing lifecycle tests passed:', len(checks))

if __name__ == '__main__':
    main()
