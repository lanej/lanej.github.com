"""Adapt the production Hugo output to the pinned Viewrule CLI; no browser rules here."""
import argparse
import copy
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys

from affected_pages import affected_routes, change_base, changed_paths

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
        if not essay and relative not in ('.', 'writing'):
            page['viewports'] = ['mobile', 'desktop', '4k']
        pages.append(page)
        if relative == '.':
            pages.append(dict(page, name='home-enlarged', textScale=2,
                              viewports=['small', 'mobile', 'desktop']))
        if relative == 'writing':
            pages.append(dict(page, name='writing-enlarged', textScale=2,
                              viewports=['small', 'mobile', 'desktop']))
        if essay:
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


def scoped_rules(rules, pages):
    names = {page['name'] for page in pages}
    selected = []
    for original in rules:
        rule = copy.deepcopy(original)
        if 'pages' in rule:
            rule['pages'] = [name for name in rule['pages'] if name in names]
            if not rule['pages']:
                continue
        selected.append(rule)
    return selected


def scope(config, *, base=None, full=False, root=ROOT):
    available = {page['path'] for page in config['pages']}
    initial = bool(base) and set(base) == {'0'}
    baseline = None if full or initial else change_base(root, base)
    paths = [] if baseline is None else changed_paths(root, baseline)
    routes = sorted(available) if baseline is None else affected_routes(
        paths, available, root=root, base=baseline,
        page_names={page['name']: page['path'] for page in config['pages']})
    pages = [page for page in config['pages'] if page['path'] in routes]
    selection = {'mode': 'full' if baseline is None else 'affected',
                 'base': baseline, 'changed_files': paths, 'routes': routes,
                 'pages': [page['name'] for page in pages],
                 'viewport_states': sum(len(page.get('viewports', config['viewports'])) for page in pages),
                 'status': 'selected' if pages else 'no-visual-changes'}
    (root / '.ui-review/selection.json').write_text(json.dumps(selection, indent=2) + '\n')
    return pages, selection


def prepare_scoped_project(config, pages, root=ROOT):
    # Native Viewrule validates every page-scoped rule against its config. Keep
    # the canonical rule file intact; run a filtered copy against a source snapshot.
    project = root / '.ui-review/affected'
    (project / '.ui-review').mkdir(parents=True, exist_ok=True)
    for relative in config['sourcePaths']:
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts or relative == '.':
            raise ValueError('Affected checks need explicit source paths inside the project.')
        source, target = root / path, project / path
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
        if source.is_dir():
            shutil.copytree(source, target)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    scoped = dict(config, pages=pages)
    rules = json.loads((root / '.ui-review/rules.json').read_text())
    (project / '.ui-review/config.json').write_text(json.dumps(scoped, indent=2) + '\n')
    (project / '.ui-review/rules.json').write_text(json.dumps(scoped_rules(rules, pages), indent=2) + '\n')
    return project


def run(arguments, project=ROOT):
    env = environment()
    if project != ROOT:
        # Do not let the generated, ignored snapshot inherit the parent repo's
        # empty git file list. The native checker fingerprints its copied sources.
        env['GIT_CEILING_DIRECTORIES'] = str(project.parent)
    return subprocess.run([str(CLI), *arguments, '--project', str(project)],
                          cwd=ROOT, env=env, check=False)


def main():
    arguments = sys.argv[1:] or ['check']
    command = arguments[0]
    project = ROOT
    if command in ('check', 'select', 'contract'):
        parser = argparse.ArgumentParser(description=__doc__)
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--base', help='Compare this commit with the current checkout, including local edits.')
        group.add_argument('--all', action='store_true', help='Check every built page.')
        parser.add_argument('--url', help='Override the preview URL for this run.')
        options = parser.parse_args(arguments[1:])
        config = prepare()
        if not CLI.is_file():
            raise ValueError('Install Node 22+ and run bash scripts/install-viewrule.sh first.')
        # Validate the full contract before filtering: a typo in a scoped rule
        # must not disappear merely because its page name is unknown.
        validation = subprocess.run([str(CLI), 'contract', '--project', str(ROOT)],
                                    cwd=ROOT, env=environment(), text=True, capture_output=True)
        if validation.returncode:
            raise ValueError(validation.stderr.strip() or validation.stdout.strip())
        if options.url:
            config['baseURL'] = options.url
        # Contract/authoring keeps the complete canonical project by default.
        # CI supplies the PR base or pre-push commit; scheduled/manual runs use all.
        full = options.all or (command == 'contract' and options.base is None) or (
            options.base is None and os.environ.get('VIEWRULE_FULL', '').lower() == 'true')
        base = options.base or os.environ.get('VIEWRULE_BASE') or None
        pages, selection = scope(config, base=base, full=full)
        print(json.dumps({'visual_selection': selection}), flush=True)
        if command == 'select' or not pages:
            return 0
        if selection['mode'] == 'affected':
            project = prepare_scoped_project(config, pages)
        elif options.url:
            (ROOT / '.ui-review/config.json').write_text(json.dumps(config, indent=2) + '\n')
        arguments = [command]
    elif command in ('hook', 'add-rule', 'learn'):
        prepare()
    if not CLI.is_file():
        raise ValueError('Install Node 22+ and run bash scripts/install-viewrule.sh first.')
    return run(arguments, project).returncode


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'Viewrule setup: {error}', file=sys.stderr)
        sys.exit(2)
