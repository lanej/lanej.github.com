"""Adapt the production Hugo output to the pinned Viewrule CLI; no browser rules here."""
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / '.tools/viewrule/node_modules/.bin/viewrule'


class PageInfo(HTMLParser):
    """Use Hugo's article metadata, so archive pagination is not treated as an essay."""
    article = False

    def handle_starttag(self, tag, attrs):
        if tag == 'meta' and dict(attrs).get('property') == 'article:published_time':
            self.article = True


def environment():
    # Reproducible project checks must not inherit a developer's dashboard rules.
    return dict(os.environ, VIEWRULE_CONFIG_DIR=str(ROOT / '.tools/viewrule-global'))


def prepare():
    public = ROOT / 'public'
    if not (public / 'build.json').is_file():
        raise ValueError('Build and validate public/ with bash scripts/build.sh first.')
    config = json.loads((ROOT / '.ui-review/site.json').read_text())
    pages = []
    for path in sorted(public.rglob('index.html')):
        relative = path.parent.relative_to(public).as_posix()
        route = '/' if relative == '.' else '/' + relative + '/'
        document = PageInfo()
        document.feed(path.read_text())
        essay = document.article
        page = {'name': 'home' if route == '/' else relative, 'path': route,
                'ready': '.sc-article .sc-section' if essay else 'main h1'}
        if not essay:
            page['viewports'] = ['mobile', 'desktop', '4k']
        pages.append(page)
        if relative in ('writing/socrates', 'writing/close-the-loop',
                        'writing/how-you-do-it-is-part-of-the-decision'):
            pages.extend([
                dict(page, name=relative + '-print', media='print', viewports=['desktop']),
                dict(page, name=relative + '-enlarged', textScale=2, viewports=['desktop']),
            ])
    if not any(page['name'] == 'home' for page in pages):
        raise ValueError('The production build has no homepage.')
    if (public / '404.html').is_file():
        pages.append({'name': '404', 'path': '/404.html', 'ready': 'main h1', 'viewports': ['mobile', 'desktop']})
    config['pages'] = pages
    (ROOT / '.ui-review/config.json').write_text(json.dumps(config, indent=2) + '\n')
    return config


def run(arguments, project=ROOT):
    return subprocess.run([str(CLI), *arguments, '--project', str(project)],
                          cwd=ROOT, env=environment(), check=False)


def main():
    arguments = sys.argv[1:] or ['check']
    if not CLI.is_file():
        raise ValueError('Install Node 22+ and run bash scripts/install-viewrule.sh first.')
    # Feedback refers to an exact prior report, so do not rebuild its contract.
    if arguments[0] in ('check', 'contract', 'hook', 'add-rule', 'learn'):
        prepare()
    return run(arguments).returncode


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError) as error:
        print(f'Viewrule setup: {error}', file=sys.stderr)
        sys.exit(2)
