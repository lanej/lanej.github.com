"""Verify that lanej.io is serving the bundle just deployed without a browser."""
import argparse
import json
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen


def get(url):
    request = Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'lanej-deploy-smoke'})
    with urlopen(request, timeout=15) as response:
        assert 200 <= response.status < 300, f'{url}: HTTP {response.status}'
        return response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='https://lanej.io/')
    parser.add_argument('--root', default='public')
    args = parser.parse_args()

    expected = json.loads((Path(args.root) / 'build.json').read_text())['revision']
    base = args.url.rstrip('/')

    for attempt in range(18):
        try:
            live = json.loads(get(f'{base}/build.json?revision={expected}'))
            if live.get('revision') == expected:
                break
        except Exception:
            pass
        time.sleep(5)
    else:
        raise AssertionError(f'lanej.io did not reach revision {expected}')

    home = get(f'{base}/').decode()
    writing = get(f'{base}/writing/').decode()
    article = get(f'{base}/writing/close-the-loop/').decode()

    assert not re.search(r'<time\b', writing, re.I), 'Writing index exposes publication dates'
    assert not re.search(r'<time\b', article, re.I), 'Article header exposes publication dates'
    assert re.search(r'\d+ min read', home), 'Homepage reading time missing'
    assert re.search(r'\d+ min read', article), 'Article reading time missing'
    print(json.dumps({'status': 'passed', 'revision': expected}))


if __name__ == '__main__':
    main()
