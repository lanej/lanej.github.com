"""Local Hugo page inventory, including unlisted essays without public discovery."""
import json
from html.parser import HTMLParser


class Article(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.is_article = False
        self.has_revision = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and 'sc-article' in attrs.get('class', '').split():
            self.is_article = True
        if tag == 'meta' and attrs.get('name') == 'site-revision':
            self.has_revision = True


def html_pages(public):
    paths = {name for name in json.loads((public / 'build.json').read_text())['files']
             if name.endswith('/index.html') or name == '/404.html'}
    # The public manifest intentionally omits unlisted content. Inspect only
    # rendered Hugo essay bundles; embedded app previews remain independent.
    for path in (public / 'writing').glob('*/index.html'):
        article = Article(path.read_text())
        if article.is_article and article.has_revision:
            paths.add('/' + path.relative_to(public).as_posix())
    return sorted(paths)
