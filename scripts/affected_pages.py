"""Select existing routes from source dependencies, CSS changes, and rule scopes.

This is change selection only. Viewrule remains responsible for browser geometry.
Unknown shared dependencies select all pages rather than silently dropping coverage.
"""
import difflib
import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path



class PageAnchors(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.anchors = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.anchors.update(('.' + name) for name in attrs.get('class', '').split())
        if attrs.get('id'):
            self.anchors.add('#' + attrs['id'])


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).removesuffix('\n')


def change_base(root, explicit=None):
    if explicit:
        return git(root, 'rev-parse', '--verify', explicit + '^{commit}')
    # Review the whole branch, plus staged/unstaged edits, rather than just HEAD~1.
    return git(root, 'merge-base', 'HEAD', 'origin/master')


def changed_paths(root, base):
    paths = git(root, 'diff', '--name-only', '--no-renames', '-z', base, '--').split('\0')
    paths += git(root, 'ls-files', '--others', '--exclude-standard', '-z').split('\0')
    return sorted(set(filter(None, paths)))


def previous_text(root, base, path):
    result = subprocess.run(['git', 'show', f'{base}:{path}'], cwd=root,
                            text=True, capture_output=True)
    return result.stdout if result.returncode == 0 else ''


def css_rules(text):
    """Keep order and grouping context; a moved rule can change the cascade."""
    import tinycss2

    result = []

    def visit(nodes, context=()):
        for node in nodes:
            if node.type == 'qualified-rule':
                result.append((context, tinycss2.serialize(node.prelude).strip(),
                               tinycss2.serialize(node.content).strip()))
            elif node.type == 'at-rule' and node.lower_at_keyword in ('media', 'supports', 'layer', 'container') and node.content is not None:
                group = (node.lower_at_keyword, tinycss2.serialize(node.prelude).strip())
                visit(tinycss2.parse_rule_list(node.content, skip_whitespace=True,
                                             skip_comments=True), context + (group,))
            elif node.type not in ('whitespace', 'comment'):
                # Imports, fonts, keyframes, parse errors, and unknown at-rules
                # can affect pages without any directly matching class.
                result.append((context, None, tinycss2.serialize([node]) if node.type != 'error' else str(node)))

    visit(tinycss2.parse_stylesheet(text, skip_whitespace=True, skip_comments=True))
    return result


def selector_anchors(selector):
    """Return necessary page anchors for each comma-separated selector.

    Use only top-level class/id tokens. Classes inside :not/:is/:has are not
    necessarily required. An unanchored selector (body, :root, attributes, etc.)
    is global. Matching any required anchor may overselect but never requires
    every ancestor/alternative to be present.
    """
    import tinycss2

    if selector is None:
        return None
    groups = [set()]
    tokens = tinycss2.parse_component_value_list(selector)
    for i, token in enumerate(tokens):
        if token.type == 'literal' and token.value == ',':
            groups.append(set())
        elif token.type == 'hash' and token.is_identifier:
            groups[-1].add('#' + token.value)
        elif token.type == 'literal' and token.value == '.' and i + 1 < len(tokens) and tokens[i + 1].type == 'ident':
            groups[-1].add('.' + tokens[i + 1].value)
    if any(not group for group in groups):
        return None
    return set.union(*groups)


def css_routes(before, after, documents):
    old, new = css_rules(before), css_rules(after)
    selected = set()
    for operation, a, b, c, d in difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes():
        if operation == 'equal':
            continue
        for _, selector, _ in old[a:b] + new[c:d]:
            anchors = selector_anchors(selector)
            if anchors is None:
                return set(documents)
            matches = {route for route, page in documents.items() if anchors & page.anchors}
            if not matches:
                return set(documents)  # A runtime-only class cannot be scoped from static HTML.
            selected.update(matches)
    return selected


def rule_routes(before, after, page_names, documents=None):
    old = {rule['id']: rule for rule in json.loads(before or '[]')}
    new = {rule['id']: rule for rule in json.loads(after or '[]')}
    selected = set()
    for key in old.keys() | new.keys():
        if old.get(key) == new.get(key):
            continue
        for rule in (old.get(key), new.get(key)):
            if rule is None:
                continue
            if not rule.get('pages'):
                # Optional checks cannot fail on pages where their selector is absent.
                # Required/global checks and uncertain selectors still select everything.
                anchors = selector_anchors(rule.get('selector')) if rule.get('optional') else None
                if anchors and documents is not None:
                    matches = {route for route, page in documents.items() if anchors & page.anchors}
                    if matches:
                        selected.update(matches)
                        continue
                return set(page_names.values())
            selected.update(page_names[name] for name in rule['pages'] if name in page_names)
    return selected


def route_names(available):
    names = {('home' if route == '/' else route.strip('/')): route for route in available}
    names.update({'404': '/404.html'} if '/404.html' in available else {})
    for name, route in list(names.items()):
        names[name + '-enlarged'] = route
        names[name + '-print'] = route
    return names


def affected_routes(paths, available, *, root=None, base=None, page_names=None):
    available = set(available)
    routes = set()
    essays = {r for r in available if r.startswith('/writing/') and r != '/writing/'}
    documents = None
    direct = {
        'layouts/home.html': {'/'}, 'assets/css/home.css': {'/'},
        'layouts/writing/list.html': {'/writing/'},
        'layouts/partials/item-visual.html': essays | {'/', '/writing/'},
        'layouts/partials/writing-item-visual.html': essays | {'/', '/writing/'},
        'layouts/partials/essay-visual.html': essays,
        'layouts/writing/single.html': essays,
        'layouts/partials/essay-content.html': essays,
        'assets/css/essays.css': essays, 'assets/css/diagrams.css': essays,
        'assets/css/citations.css': essays, 'assets/js/citations.js': essays,
        'layouts/labs.html': {'/labs/'}, 'assets/js/labs.js': {'/labs/'},
        'data/github_activity.json': {'/open-source/'},
        'layouts/partials/activity-calendar.html': {'/open-source/'},
        'assets/css/work.css': {'/record/', '/open-source/'},
    }
    for path in paths:
        if path == '.ui-review/.gitignore':
            continue
        if path == '.ui-review/site.json' and root is not None and base is not None:
            old = json.loads(previous_text(root, base, path) or '{}')
            new = json.loads((Path(root) / path).read_text())
            for key in ('sourcePaths', 'enforceOnStop'):
                old.pop(key, None)
                new.pop(key, None)
            if old != new:
                routes.update(available)
        elif path in direct:
            routes.update(direct[path])
        elif path in ('data/contributions.yaml', 'layouts/partials/contributions.html') or path.startswith('static/logos/projects/'):
            routes.add('/open-source/')
        elif path in ('data/career.yaml', 'layouts/shortcodes/career-timeline.html', 'layouts/shortcodes/work-role.html', 'layouts/shortcodes/speaking-engagement.html') or path.startswith(('static/logos/companies/', 'static/logos/events/', 'static/icons/heroicons/')):
            routes.add('/record/')
        elif path.startswith('assets/css/') and path.endswith('.css') and root is not None and base is not None:
            if documents is None:
                documents = {}
                for route in available:
                    file = Path(root) / 'public' / (route.lstrip('/') + 'index.html' if route.endswith('/') else route.lstrip('/'))
                    documents[route] = PageAnchors(file.read_text())
            current = Path(root) / path
            routes.update(css_routes(previous_text(root, base, path), current.read_text() if current.exists() else '', documents))
        elif path == '.ui-review/rules.json' and root is not None and base is not None:
            if documents is None:
                documents = {}
                for route in available:
                    file = Path(root) / 'public' / (route.lstrip('/') + 'index.html' if route.endswith('/') else route.lstrip('/'))
                    documents[route] = PageAnchors(file.read_text())
            current = Path(root) / path
            routes.update(rule_routes(previous_text(root, base, path), current.read_text(), page_names or route_names(available), documents))
        elif path.startswith('content/writing/') and not path.endswith('.md'):
            routes.update(essays | {'/', '/writing/'})
        elif path.startswith('content/') and path.endswith('.md'):
            relative = path.removeprefix('content/').removesuffix('.md')
            parts = relative.split('/')
            if parts[-1] in ('index', '_index'):
                parts.pop()
            route = '/' + '/'.join(parts) + '/' if parts else '/'
            routes.add(route)
            if route not in available and root is not None and (Path(root) / path).exists():
                routes.update(available)  # An unfamiliar permalink/layout needs a conservative check.
            if relative.startswith('writing/'):
                routes.update(('/', '/writing/'))
            if route == '/labs/':
                routes.add('/')  # Homepage featured experiments live in Labs front matter.
        elif path.startswith(('layouts/', 'assets/', 'static/', 'data/', '.ui-review/')) or path in ('hugo.toml', '.hugo-version', 'scripts/install-viewrule.sh'):
            routes.update(available)
    return sorted(routes & available)
