"""Validate generated HTML, feed, links and image bytes; write deployment manifest."""
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from PIL import Image

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)
    def handle_starttag(self, name, attrs):
        self.tags.append((name, dict(attrs)))
    def select(self, tag, **attrs):
        return [a for n,a in self.tags if n == tag and all(a.get(k) == v for k,v in attrs.items())]

def main(root):
    source = Path('assets/images/josh-lane.webp')
    assert hashlib.sha256(source.read_bytes()).hexdigest() == 'e1505b9e7535ac59efc634f4259fd37d581afaef1e187eae51442899c0313e47', 'Unexpected source photograph bytes'
    assert Path('CNAME').read_bytes() == Path('static/CNAME').read_bytes() == b'lanej.io\n', 'Domain marker mismatch'
    revision = os.getenv('HUGO_PARAMS_REVISION', 'local')
    documents = {}
    for path in root.rglob('*.html'):
        text = path.read_text()
        doc = Document(text)
        documents[path] = doc
        assert len(doc.select('h1')) == 1, f'{path}: expected one h1'
        assert doc.select('title'), f'{path}: missing title'
        for name in ('description', 'viewport', 'site-revision'):
            assert doc.select('meta', name=name), f'{path}: missing {name}'
        assert doc.select('meta', name='site-revision')[0]['content'] == revision
        for prop in ('og:title', 'og:description', 'og:image', 'og:url'):
            assert doc.select('meta', property=prop), f'{path}: missing {prop}'
        assert doc.select('link', rel='canonical')
        assert doc.select('main', id='main') and doc.select('a', href='#main'), f'{path}: missing skip link'
        assert doc.select('nav', **{'aria-label':'Primary navigation'})
        assert all(a.get('type') == 'application/ld+json' for a in doc.select('script')), 'Unexpected executable JavaScript'
        assert all(a.get('alt') for a in doc.select('img')), f'{path}: missing image description'
        for forbidden in ('New writing will appear here', 'Evidence over chronology', 'new-about-josh2.jpg', 'headshot-v4'):
            assert forbidden not in text, f'{path}: leftover placeholder or image'
    for path,doc in documents.items():
        for _,attrs in doc.tags:
            for key in ('href','src'):
                url=attrs.get(key,'')
                parts=urlparse(url)
                if not url or parts.scheme not in ('','https') or (parts.netloc and parts.netloc != 'lanej.io'):
                    continue
                target=root/unquote(parts.path.lstrip('/')) if parts.path.startswith('/') else path.parent/unquote(parts.path)
                if not parts.path: target=path
                if target.is_dir(): target=target/'index.html'
                target=target.resolve()
                assert target.is_relative_to(root), f'{path}: link escapes public output'
                assert target.exists(), f'{path}: broken {url}'
                if parts.fragment and target.suffix=='.html':
                    other=documents.get(target) or Document(target.read_text())
                    assert any(a.get('id')==parts.fragment for _,a in other.tags), f'Missing anchor {url}'
    for path in root.rglob('*'):
        if path.suffix.lower() in ('.jpg','.jpeg','.webp','.png','.gif'):
            with Image.open(path) as image:
                image.load()
                assert image.width>0 and image.height>0, f'Invalid image: {path}'
                if path.name.startswith('josh-lane'):
                    assert image.width==image.height and image.width>=48, f'Portrait dimensions: {path}'
    articles=[p for p in (root/'writing').glob('*/index.html')]
    assert not (root/'writing/index.html').exists() or articles, 'Empty writing section'
    feed=ET.parse(root/'index.xml').getroot()
    items=feed.findall('channel/item')
    assert len(items)==len(articles), 'RSS must include only published writing'
    for item in items:
        assert item.findtext('title') and item.findtext('pubDate')
        link=item.findtext('link')
        assert link and urlparse(link).path.startswith('/writing/')
        assert item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded'), 'RSS must include article text'
    hashes={'/'+str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and p.name not in {'build.json','CNAME','.nojekyll'}}
    (root/'build.json').write_text(json.dumps({'revision':revision,'files':hashes},sort_keys=True))
    print(f'Passed: {len(documents)} pages, {len(articles)} articles, valid RSS and {len(hashes)} hashed files.')

if __name__=='__main__':
    main(Path(sys.argv[1] if len(sys.argv)>1 else 'public').resolve())
