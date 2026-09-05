"""Verify browser rendering and response bytes on localhost or the live custom domain."""
import argparse
import hashlib
import io
import json
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
    routes=[('/','home'),('/about/','about'),('/record/','work'),('/404.html','404')]
    if '/writing/index.html' in manifest['files']:
        routes.append(('/writing/','writing'))
        articles=sorted(p for p in manifest['files'] if p.startswith('/writing/') and p.endswith('/index.html') and p!='/writing/index.html')
        routes.extend((p[:-10], 'article-'+p.split('/')[2]) for p in articles)
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
            for attempt in range(18 if live else 1):
                response=request.get(urljoin(args.url,path),timeout=20000)
                if response.ok and hashlib.sha256(response.body()).hexdigest()==digest: break
                if live: time.sleep(10)
            else: raise AssertionError(f'{path}: HTTP {response.status} or bytes differ from tested build')
            if path.endswith(('.jpg','.jpeg','.webp','.png','.gif')):
                with Image.open(io.BytesIO(response.body())) as image: image.load()
        report['hashed_files_verified']=len(manifest['files'])
        for engine in args.engines.split(','):
            launch={'executable_path':args.chromium_path,'args':['--no-sandbox']} if engine=='chromium' and args.chromium_path else {}
            browser=getattr(pw,engine).launch(**launch)
            widths=[320,390,768,1024,1440] if engine=='chromium' else [390,1440]
            for width in widths:
                context=browser.new_context(viewport={'width':width,'height':900 if width>700 else 844},device_scale_factor=3 if width<700 else 1,has_touch=width<700,is_mobile=width<700,color_scheme='dark')
                page=context.new_page(); errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                for route,label in routes:
                    response=page.goto(urljoin(args.url,route),wait_until='networkidle')
                    assert response and (response.ok or (route=='/404.html' and response.status==404)), f'{engine} {route}: navigation failed'
                    page.locator('img').evaluate_all('(imgs)=>{for(const i of imgs)i.loading="eager";return Promise.all(imgs.map(i=>i.decode()))}')
                    assert page.locator('meta[name="site-revision"]').get_attribute('content')==manifest['revision'], f'{route}: wrong revision'
                    metrics=page.evaluate('''()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
                    nav:[...document.querySelectorAll('.site-header nav a')].map(a=>({text:a.textContent,height:a.getBoundingClientRect().height})),
                    images:[...document.images].map(i=>{const frame=i.closest('.hero-portrait,.header-portrait');return {src:i.currentSrc,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height,portrait:!!frame,radius:frame?getComputedStyle(frame).borderRadius:null}}),
                    workTop:document.querySelector('.work-section')?.getBoundingClientRect().top})''')
                    assert metrics['scrollWidth']<=width, f'{engine} {width} {route}: horizontal overflow'
                    assert all(a['height']>=44 for a in metrics['nav']), 'Small navigation tap targets'
                    assert page.locator('h1').count()==1
                    for image in metrics['images']:
                        if not image['portrait']: continue
                        assert abs(image['width']-image['height'])<2, 'Distorted portrait'
                        assert image['radius']=='50%', 'Portrait is not circular'
                        with Image.open(io.BytesIO(request.get(image['src']).body())) as actual:
                            actual.load()
                            assert actual.width>=image['width']*(2.8 if width<700 else 1), 'Insufficient portrait resolution'
                    assert page.locator('.header-portrait').count()==(0 if route=='/' else 1), 'Interior portrait missing or duplicated'
                    assert not page.locator('.portrait-aside').count(), 'Obsolete large interior portrait'
                    if route=='/':
                        assert metrics['workTop']<(1000 if width<700 else 740), 'Hero pushes work too far down'
                    assert bool(page.locator('.site-header a[href="/writing/"]').count())==('/writing/index.html' in manifest['files']), 'Writing navigation state is wrong'
                    page.evaluate('document.activeElement?.blur()'); page.keyboard.press('Tab')
                    assert page.locator('.skip-link').evaluate('(a)=>a===document.activeElement'), 'Skip link not first keyboard target'
                    page.keyboard.press('Enter')
                    assert page.locator('main').evaluate('(m)=>m===document.activeElement'), 'Skip link does not focus main'
                    page.evaluate('window.scrollTo(0,0)'); page.locator('main').evaluate('(m)=>m.blur()')
                    if width in (390,1440): page.screenshot(path=str(out/f'{engine}-{width}-{label}.png'),full_page=True)
                    report['checks'].append({'engine':engine,'width':width,'page':route,**metrics})
                assert not errors, errors
                context.close()
            browser.close()
        request.dispose()
    report['status']='passed'
    (out/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'status':'passed','url':args.url,'revision':manifest['revision'],'browser_page_checks':len(report['checks']),'hashed_files':report['hashed_files_verified']}))

if __name__=='__main__':main()
