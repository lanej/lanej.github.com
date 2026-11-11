"""Validate independently built Starlight mounts and record deployment bytes."""
import hashlib
import json
from urllib.parse import unquote, urlsplit

from check import Document


def validate(root, prefix, revision, required=()):
    root = root.resolve()
    pages = {path: Document(path.read_text()) for path in root.rglob('*.html')}
    assert root / 'index.html' in pages, 'Project documentation homepage is missing'
    assert (root / 'pagefind/pagefind-entry.json').is_file(), 'Project search index is missing'
    for route in required:
        assert (root / route).is_file(), f'Required documentation page is missing: {route}'
    for path, doc in pages.items():
        if path != root / '404.html':
            route = prefix + path.relative_to(root).as_posix().removesuffix('index.html')
            canonical = doc.select('link', rel='canonical')
            assert len(canonical) == 1 and canonical[0]['href'] == 'https://lanej.io' + route, f'{path}: incorrect canonical URL'
        for tag, attrs in doc.tags:
            for key in ('href', 'src'):
                raw = attrs.get(key, '')
                url = urlsplit(raw)
                if not raw or url.scheme or url.netloc or raw.startswith('#'):
                    continue
                if url.path.startswith('/'):
                    assert url.path.startswith(prefix), f'{path}: asset or link escapes {prefix}: {raw}'
                    target = root / unquote(url.path.removeprefix(prefix))
                else:
                    target = path.parent / unquote(url.path) if url.path else path
                target = target.resolve()
                assert target.is_relative_to(root), f'{path}: link escapes documentation: {raw}'
                if target.is_dir():
                    target /= 'index.html'
                assert target.is_file(), f'{path}: missing {raw}'
                if url.fragment and target in pages:
                    assert any(a.get('id') == unquote(url.fragment) for _, a in pages[target].tags), f'{path}: missing anchor {raw}'
    files = {prefix + path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in root.rglob('*') if path.is_file() and path.name != 'build.json'}
    (root / 'build.json').write_text(json.dumps({'revision': revision, 'files': files}, sort_keys=True) + '\n')
    print(f'{prefix}: validated {len(pages)} pages, canonical URLs, local assets, anchors, and {len(files)} file hashes.')

