"""Browser checks against localhost or the actual production custom domain.

Production verification waits for the expected revision, then compares the
HTTP response bytes to the local build before taking browser screenshots.
This catches broken uploads and stale deployments, not just HTTP 200s.
"""
import argparse
import hashlib
import io
import json
import os
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from PIL import Image
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8765/')
    parser.add_argument('--output', default='artifacts/local')
    parser.add_argument('--root', default='public')
    parser.add_argument('--engines', default='chromium')
    parser.add_argument('--chromium-path', default='')
    args=parser.parse_args()
    out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((Path(args.root)/'build.json').read_text())
    live=urlparse(args.url).hostname=='lanej.io'
    report={'url':args.url,'revision':manifest['revision'],'live_custom_domain':live,'checks':[]}
    with sync_playwright() as pw:
        request=pw.request.new_context()
        for attempt in range(30 if live else 1):
            try:
                result=request.get(urljoin(args.url,'build.json')+'?revision='+manifest['revision'],timeout=15000)
                if result.ok and result.json().get('revision')==manifest['revision']: break
            except Exception:
                pass
            if not live: raise AssertionError('Local manifest unavailable')
            time.sleep(10)
        else: raise AssertionError('Expected revision not visible on lanej.io within five minutes')
        for path,digest in manifest['files'].items():
            # Check unversioned URLs too; CDN propagation may lag the manifest.
            for attempt in range(18 if live else 1):
                response=request.get(urljoin(args.url,path),timeout=20000)
                if response.ok and hashlib.sha256(response.body()).hexdigest()==digest:
                    break
                if live: time.sleep(10)
            else:
                raise AssertionError(f'{path}: HTTP {response.status} or bytes differ from tested build')
            if path.endswith(('.jpg','.webp')):
                with Image.open(io.BytesIO(response.body())) as image: image.load()
        report['hashed_files_verified']=len(manifest['files'])
        for engine in args.engines.split(','):
            browser_type=getattr(pw,engine)
            launch={'executable_path':args.chromium_path,'args':['--no-sandbox']} if engine=='chromium' and args.chromium_path else {}
            browser=browser_type.launch(**launch)
            widths=[320,390,768,1024,1440] if engine=='chromium' else [390,1440]
            for width in widths:
                context=browser.new_context(viewport={'width':width,'height':900 if width>700 else 844},device_scale_factor=3 if width<700 else 1,has_touch=width<700,is_mobile=width<700,color_scheme='dark')
                page=context.new_page()
                errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                for route,label in [('/','home'),('/about/','about'),('/record/','work')]:
                    response=page.goto(urljoin(args.url,route),wait_until='networkidle')
                    assert response and response.ok, f'{engine} {route}: failed navigation'
                    page.locator('img').evaluate_all('(imgs)=>Promise.all(imgs.map(i=>i.decode()))')
                    revision=page.locator('meta[name="site-revision"]').get_attribute('content')
                    assert revision==manifest['revision'], f'{route}: wrong live revision'
                    metrics=page.evaluate('''()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
                      nav:[...document.querySelectorAll('nav a')].map(a=>({text:a.textContent,height:a.getBoundingClientRect().height})),
                      images:[...document.images].map(i=>({src:i.currentSrc,naturalWidth:i.naturalWidth,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height})),
                      workTop:document.querySelector('.work-section')?.getBoundingClientRect().top})''')
                    assert metrics['scrollWidth']<=width, f'{engine} {width} {route}: horizontal overflow'
                    assert all(a['height']>=44 for a in metrics['nav']), 'Small navigation tap targets'
                    assert len(page.locator('h1').all())==1
                    for image in metrics['images']:
                        assert abs(image['width']-image['height'])<2, 'Distorted headshot'
                        data=request.get(image['src']).body()
                        with Image.open(io.BytesIO(data)) as actual:
                            actual.load()
                            assert actual.width>=image['width']*(2.8 if width<700 else 1), 'Insufficient headshot resolution'
                    if route=='/':
                        assert metrics['workTop']<(1000 if width<700 else 740), 'Hero pushes work too far down'
                        assert not page.locator('nav a[href="/writing/"]').count()
                    page.evaluate('document.activeElement?.blur()')
                    page.keyboard.press('Tab')
                    assert page.locator('.skip-link').evaluate('(a)=>a===document.activeElement'), 'Skip link not first keyboard target'
                    page.keyboard.press('Enter')
                    assert page.locator('main').evaluate('(m)=>m===document.activeElement'), 'Skip link does not focus main'
                    page.evaluate('window.scrollTo(0,0)')
                    page.locator('main').evaluate('(m)=>m.blur()')
                    if width in (390,1440):
                        page.screenshot(path=str(out/f'{engine}-{width}-{label}.png'),full_page=True)
                    report['checks'].append({'engine':engine,'width':width,'page':route,**metrics})
                assert not errors, errors
                context.close()
            browser.close()
        request.dispose()
    report['status']='passed'
    (out/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'status':'passed','url':args.url,'revision':manifest['revision'],'browser_page_checks':len(report['checks']),'hashed_files':report['hashed_files_verified']}))

if __name__=='__main__':main()
