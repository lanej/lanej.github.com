"""Exercise authoring and article rendering in a disposable site, never production."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from PIL import Image
from writing import ROOT, create_draft, prepare_post, hugo_binary
from check import Document


def verify_invalid_share_images(binary, root, origin, env):
    """Give each invalid input its own bundle and explicit publication metadata."""
    cases = (
        ('missing-resource', 'missing.png', 'A test diagram', 'Missing social_image'),
        ('missing-alt', 'diagram.png', '', 'social_image_alt is required'),
    )
    outcomes = []
    for slug, image, alt, expected in cases:
        bundle = root/'content/writing'/('invalid-media-'+slug)
        bundle.mkdir()
        try:
            # These are fresh, explicitly published past-date fixtures, not text
            # substitutions in the file modified by the authoring-workflow test.
            bundle.joinpath('index.md').write_text(
                '+++\ntitle="Invalid media fixture"\n'
                'description="An isolated validation test"\n'
                'date="2020-01-01T00:00:00Z"\ndraft=false\n'
                f'social_image={json.dumps(image)}\n'
                f'social_image_alt={json.dumps(alt)}\n+++\n'
                'This fixture must fail the build and is never published.\n'
            )
            Image.new('RGB',(900,450),(40,60,50)).save(bundle/'diagram.png')
            failed = subprocess.run(
                [binary,'--source',str(root),'--destination',str(root/('invalid-output-'+slug)),
                 '--baseURL',origin], capture_output=True,text=True,env=env,
            )
            output = failed.stdout + failed.stderr
            assert failed.returncode != 0 and expected in output, (
                f'{slug}: expected a build failure containing {expected!r}; '
                f'got exit {failed.returncode}\n{output}'
            )
            outcomes.append({'case':slug,'status':'rejected','exit_code':failed.returncode})
        finally:
            shutil.rmtree(bundle)
    return outcomes


def main():
    binary=hugo_binary(ROOT)
    out=ROOT/'artifacts/writing'; out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='lanej-writing-') as tmp:
        root=Path(tmp)
        for folder in ('assets','content','layouts','data','static','archetypes','scripts'):
            shutil.copytree(ROOT/folder, root/folder)
        for name in ('hugo.toml','hugo.preview.toml','CNAME'):
            shutil.copy2(ROOT/name, root/name)
        path=create_draft(root,'preview-check','Article layout verification')
        try:
            create_draft(root,'preview-check','Must not overwrite')
            raise AssertionError('Duplicate draft was accepted')
        except FileExistsError: pass
        try:
            create_draft(root,'../escape','Must not traverse')
            raise AssertionError('Unsafe slug was accepted')
        except ValueError: pass
        try:
            prepare_post(root,'preview-check')
            raise AssertionError('Empty draft was accepted')
        except ValueError: pass
        body='''
An isolated layout fixture, not an essay or a statement by Josh.

## A section heading

Body copy with **emphasis**, a [link](/about/), and a footnote.[^check]

> A block quotation with enough text to wrap across a narrow screen.

```go
func example() string { return "a-long-code-line-that-must-scroll-within-the-code-block-not-the-document-01234567890123456789012345678901234567890123456789" }
```

| First column | Second column | Third column | Fourth column |
| --- | --- | --- | --- |
| Test | A wide table | Scrolls locally | Without page overflow |

![Non-square diagram fixture](diagram.png "A visible diagram caption, separate from its alt text.")

[^check]: Footnotes should remain readable and link back correctly.
'''
        path.write_text(path.read_text().replace('description = ""','description = "An isolated reading-layout test."').replace('toc = false','toc = true\nsocial_image = "diagram.png"\nsocial_image_alt = "A non-square test diagram"')+body)
        Image.new('RGB',(900,450),(40,60,50)).save(path.parent/'diagram.png')
        hidden=create_draft(root,'private-sentinel','Private sentinel')
        hidden.write_text(hidden.read_text()+'PRIVATE_DRAFT_SENTINEL_NOT_FOR_PRODUCTION')
        subprocess.run([binary,'--source',str(root),'--config','hugo.toml,hugo.preview.toml','--buildDrafts','--buildFuture'],check=True)
        preview=(root/'.preview/writing/preview-check/index.html').read_text()
        assert 'Draft — local preview only' in preview and 'noindex' in preview
        prepared=prepare_post(root,'preview-check')
        assert prepared.exists() and not path.exists()
        future=root/'content/writing/future-sentinel'; future.mkdir(parents=True)
        future.joinpath('index.md').write_text('+++\ntitle="Future sentinel"\ndescription="Not published"\ndate="2099-01-01T00:00:00Z"\ndraft=false\n+++\nFUTURE_SENTINEL_NOT_FOR_PRODUCTION\n')
        existing=root/'content/writing/existing-writing-fixture'; existing.mkdir(parents=True)
        existing.joinpath('index.md').write_text('+++\ntitle="Existing article fixture"\ndescription="A second published entry for feed tests."\ndate="2020-01-01T00:00:00Z"\ndraft=false\n+++\nAn isolated fixture for feed and chronology checks.\n')
        public=root/'public'
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(public)))
        origin=f'http://127.0.0.1:{server.server_port}/'
        thread=Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            env={**os.environ,'HUGO_PARAMS_REVISION':'writing-fixture'}
            invalid_media=verify_invalid_share_images(binary,root,origin,env)
            subprocess.run([binary,'--source',str(root),'--destination',str(public),'--baseURL',origin,'--panicOnWarning'],check=True,env=env)
            subprocess.run([sys.executable,str(root/'scripts/check.py'),str(public)],cwd=root,check=True,env=env)
            assert not (public/'writing/private-sentinel').exists()
            assert not (public/'writing/future-sentinel').exists()
            assert not (public/'drafts').exists()
            for file in public.rglob('*'):
                if file.is_file() and file.suffix in ('.html','.xml','.json'):
                    text=file.read_text()
                    assert 'PRIVATE_DRAFT_SENTINEL_NOT_FOR_PRODUCTION' not in text
                    assert 'FUTURE_SENTINEL_NOT_FOR_PRODUCTION' not in text
                    assert 'invalid-media-' not in text
            article=(public/'writing/preview-check/index.html').read_text()
            assert 'BlogPosting' in article and 'article:published_time' in article and 'min read' in article
            assert 'On this page' in article and 'width="900" height="450"' in article
            assert '<figcaption>A visible diagram caption, separate from its alt text.</figcaption>' in article
            document=Document(article)
            social_url=origin+'writing/preview-check/diagram.png'
            assert document.select('meta',property='og:image')[0]['content']==social_url
            assert document.select('meta',property='og:image:width')[0]['content']=='900'
            assert document.select('meta',property='og:image:height')[0]['content']=='450'
            assert document.select('meta',property='og:image:alt')[0]['content']=='A non-square test diagram'
            assert document.select('meta',name='twitter:card')[0]['content']=='summary_large_image'
            fallback=Document((public/'writing/existing-writing-fixture/index.html').read_text())
            assert 'josh-lane' in fallback.select('meta',property='og:image')[0]['content']
            assert fallback.select('meta',name='twitter:card')[0]['content']=='summary'
            feed=ET.parse(public/'index.xml').getroot()
            items=feed.findall('channel/item')
            matching=[item for item in items if item.findtext('link')==origin+'writing/preview-check/']
            assert len(matching)==1 and len(items)>=2
            assert matching[0].findtext('title')=='Article layout verification'
            content=matching[0].findtext('{http://purl.org/rss/1.0/modules/content/}encoded')
            assert 'A section heading' in content and '<figcaption>' in content
            ordered=[item.findtext('link') for item in items]
            assert ordered.index(origin+'writing/preview-check/') < ordered.index(origin+'writing/existing-writing-fixture/')
            subprocess.run([sys.executable,str(ROOT/'scripts/verify.py'),'--url',origin,'--root',str(public),'--output',str(out),'--engines','chromium,webkit'],check=True)
        finally:
            server.shutdown(); server.server_close(); thread.join()
        (out/'authoring.json').write_text(json.dumps({'status':'passed','checks':['invalid slug rejected','duplicate draft rejected','empty draft rejected','local preview includes drafts and noindex','promotion preserves assets','production excludes local drafts and future posts','RSS contains only published essays with full text and captions','multiple articles and chronology supported','article metadata, footnotes, tables, code and non-square images rendered','visible captions separate from alt text','article share image, dimensions, and alt override verified','portrait fallback and Person metadata preserved','missing share image and alt text rejected','200% text and navigation tested in both browser engines'],'invalid_media':invalid_media,'fixture_published_to_live_site':False},indent=2))
    print('Writing workflow verified in a disposable directory; no sample content published.')

if __name__=='__main__':main()
