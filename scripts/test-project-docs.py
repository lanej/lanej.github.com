"""Exercise the shared mount validator with an independently authored site."""
import hashlib
import json
from pathlib import Path
import tempfile

from project_docs import validate


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / 'pagefind').mkdir()
        (root / 'pagefind/pagefind-entry.json').write_text('{}')
        (root / 'reference').mkdir()
        (root / 'reference/index.html').write_text('<link rel="canonical" href="https://lanej.io/example/reference/"><h1 id="api">API</h1>')
        original = '<link rel="canonical" href="https://lanej.io/example/"><a href="/example/reference/#api">API</a>'
        (root / 'index.html').write_text(original)
        validate(root, '/example/', 'a' * 40, ('reference/index.html',))
        manifest = json.loads((root / 'build.json').read_text())
        assert manifest['revision'] == 'a' * 40
        assert manifest['files']['/example/index.html'] == hashlib.sha256(original.encode()).hexdigest()
        for broken in ('/example/missing/', '/example/reference/#missing', '/escape/'):
            (root / 'index.html').write_text(original.replace('/example/reference/#api', broken))
            try:
                validate(root, '/example/', 'a' * 40)
            except AssertionError:
                continue
            raise AssertionError(f'Broken mount was accepted: {broken}')
        print('PASS: project mount hashes valid output and rejects missing routes, anchors and base-path escapes.')


if __name__ == '__main__':
    main()
