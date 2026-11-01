"""Verify that lanej.io is serving the bundle just deployed without a browser."""
import argparse
import hashlib
import io
import json
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image


def get(url):
    request = Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'lanej-deploy-smoke'})
    with urlopen(request, timeout=15) as response:
        assert 200 <= response.status < 300, f'{url}: HTTP {response.status}'
        return response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='https://lanej.io/')
    parser.add_argument('--root', default='public')
    parser.add_argument('--manifest', default='build.json')
    parser.add_argument('--bundle-only', action='store_true', help='Verify an independently built project without Hugo-specific assertions.')
    args = parser.parse_args()

    manifest = json.loads((Path(args.root) / args.manifest).read_text())
    expected = manifest['revision']
    base = args.url.rstrip('/')

    for attempt in range(18):
        try:
            live = json.loads(get(f'{base}/{args.manifest}?revision={expected}'))
            if live.get('revision') == expected:
                break
        except Exception:
            pass
        time.sleep(5)
    else:
        raise AssertionError(f'lanej.io did not reach revision {expected}')

    for path, digest in manifest['files'].items():
        for attempt in range(18):
            try:
                content = get(f'{base}{path}?revision={expected}')
                if hashlib.sha256(content).hexdigest() == digest:
                    break
            except Exception:
                pass
            time.sleep(5)
        else:
            raise AssertionError(f'{path}: bytes differ from the tested build')
        if path.endswith(('.jpg', '.jpeg', '.webp', '.png', '.gif', '.ico')):
            with Image.open(io.BytesIO(content)) as image:
                image.load()

    if args.bundle_only:
        print(json.dumps({'status': 'passed', 'revision': expected, 'hashed_files': len(manifest['files'])}))
        return

    home = get(f'{base}/').decode()
    writing = get(f'{base}/writing/').decode()
    article = get(f'{base}/writing/close-the-loop/').decode()

    assert not re.search(r'<time\b', writing, re.I), 'Writing index exposes publication dates'
    assert not re.search(r'<time\b', article, re.I), 'Article header exposes publication dates'
    assert re.search(r'\d+ min read', home), 'Homepage reading time missing'
    assert re.search(r'\d+ min read', article), 'Article reading time missing'
    print(json.dumps({'status': 'passed', 'revision': expected, 'hashed_files': len(manifest['files'])}))


if __name__ == '__main__':
    main()
