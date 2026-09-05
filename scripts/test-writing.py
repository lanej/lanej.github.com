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

![Non-square diagram fixture](diagram.png)

[^check]: Footnotes should remain readable and link back correctly.
'''
        path.write_text(path.read_text().replace('description = ""','description = "An isolated reading-layout test."').replace('toc = false','toc = true')+body)
        Image.new('RGB',(900,450),(40,60,50)).save(path.parent/'diagram.png')
        hidden=create_draft(root,'private-sentinel','Private sentinel')
        hidden.write_text(hidden.read_text()+'PRIVATE_DRAFT_SENTINEL_NOT_FOR_PRODUCTION')
        # Preview must include ignored local drafts and mark pages noindex.
        subprocess.run([binary,'--source',str(root),'--config','hugo.toml,hugo.preview.toml','--buildDrafts','--buildFuture'],check=True)
        preview=(root/'.preview/writing/preview-check/index.html').read_text()
        assert 'Draft — local preview only' in preview and 'noindex' in preview
        prepared=prepare_post(root,'preview-check')
        assert prepared.exists() and not path.exists()
        future=root/'content/writing/future-sentinel'; future.mkdir(parents=True)
        future.joinpath('index.md').write_text('+++\ntitle="Future sentinel"\ndescription="Not published"\ndate="2099-01-01T00:00:00Z"\ndraft=false\n+++\nFUTURE_SENTINEL_NOT_FOR_PRODUCTION\n')
        public=root/'public'
        env={**os.environ,'HUGO_PARAMS_REVISION':'writing-fixture'}
        subprocess.run([binary,'--source',str(root),'--destination',str(public),'--panicOnWarning'],check=True,env=env)
        subprocess.run([sys.executable,str(root/'scripts/check.py'),str(public)],cwd=root,check=True,env=env)
        assert not (public/'writing/private-sentinel').exists()
        assert not (public/'writing/future-sentinel').exists()
        assert not (public/'drafts').exists()
        for file in public.rglob('*'):
            if file.is_file() and file.suffix in ('.html','.xml','.json'):
                text=file.read_text()
                assert 'PRIVATE_DRAFT_SENTINEL_NOT_FOR_PRODUCTION' not in text
                assert 'FUTURE_SENTINEL_NOT_FOR_PRODUCTION' not in text
        article=(public/'writing/preview-check/index.html').read_text()
        assert 'BlogPosting' in article and 'article:published_time' in article and 'min read' in article
        assert 'On this page' in article and 'width="900" height="450"' in article
        feed=ET.parse(public/'index.xml').getroot()
        assert len(feed.findall('channel/item'))==1
        assert feed.findtext('channel/item/title')=='Article layout verification'
        assert 'A section heading' in feed.findtext('channel/item/{http://purl.org/rss/1.0/modules/content/}encoded')
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(public)))
        thread=Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            subprocess.run([sys.executable,str(ROOT/'scripts/verify.py'),'--url',f'http://127.0.0.1:{server.server_port}/','--root',str(public),'--output',str(out),'--engines','chromium,webkit'],check=True)
        finally:
            server.shutdown(); server.server_close(); thread.join()
        (out/'authoring.json').write_text(json.dumps({'status':'passed','checks':['invalid slug rejected','duplicate draft rejected','empty draft rejected','local preview includes drafts and noindex','promotion preserves assets','production excludes local drafts and future posts','RSS contains only published essays with full text','article metadata, footnotes, tables, code and non-square images rendered'],'fixture_published_to_live_site':False},indent=2))
    print('Writing workflow verified in a disposable directory; no sample content published.')

if __name__=='__main__':main()
