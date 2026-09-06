"""Verify browser rendering and response bytes on localhost or the live custom domain."""
import argparse
import hashlib
import io
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from PIL import Image
from playwright.sync_api import sync_playwright

# Phone heights represent usable content space with browser chrome, not full
# device screenshots. The 320x480 case guards the smallest first viewport.
PHONE_VIEWPORTS = [(320, 480), (375, 600), (390, 664), (430, 740)]


def verify_identity_labels(page):
    """Identify the owner once in shared page chrome, not above every title."""
    labels = page.locator(
        '.site-header .wordmark, .hero h1, .page-header .eyebrow, '
        '.article-meta > *, .site-footer'
    ).all_text_contents()
    count = sum(len(re.findall(r'\bJosh\s+Lane\b', label, re.IGNORECASE)) for label in labels)
    assert count == 1, f'Expected one identity label, found {count}: {labels}'
    return count


def verify_home_opening(page, width, height):
    """A complete identity and portrait must be visible before the first scroll."""
    opening = page.evaluate('''() => {
        const rect = selector => {
            const r = document.querySelector(selector).getBoundingClientRect();
            return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height};
        };
        return {
            nameCount: ((document.querySelector('.site-header').innerText + '\\n' +
                document.querySelector('.hero').innerText).match(/Josh Lane/g) || []).length,
            identity: rect('.hero-identity'), portrait: rect('.hero-portrait'),
            intro: rect('.hero .intro'), link: rect('.hero .text-link'),
            work: rect('.work-section')
        };
    }''')
    assert opening['nameCount'] == 1, 'Homepage repeats the name in its opening'
    assert page.locator('.site-header .wordmark').count() == 0, 'Duplicate homepage wordmark'
    if width <= 700:
        portrait = opening['portrait']
        identity = opening['identity']
        assert 80 <= portrait['width'] <= 120, 'Mobile portrait is not compact'
        assert portrait['top'] >= 0 and portrait['bottom'] <= height, 'Portrait cut off in first viewport'
        assert portrait['left'] >= 0 and portrait['right'] <= width, 'Portrait horizontally clipped'
        assert portrait['left'] >= identity['right'] + 8, 'Portrait should sit beside the identity'
        assert abs((portrait['top'] + portrait['bottom']) / 2 -
                   (identity['top'] + identity['bottom']) / 2) <= 2, 'Identity and portrait are misaligned'
        assert opening['intro']['top'] >= max(portrait['bottom'], identity['bottom']) + 12, 'Intro crowds identity'
        assert opening['link']['bottom'] <= height - 16, 'Primary link below first viewport'
        assert opening['work']['top'] <= 480, 'Mobile hero delays the actual work'
    else:
        assert opening['work']['top'] < 740, 'Desktop hero pushes work too far down'
    return opening


def verify_diagrams(page, width, out, engine, label):
    """Keep diagram text readable and capture each figure at native pixel density."""
    diagrams = page.locator('[data-essay-diagram]')
    results = []
    for index in range(diagrams.count()):
        diagram = diagrams.nth(index)
        metrics = diagram.evaluate('''el => {
            const r = el.getBoundingClientRect();
            return {name:el.dataset.essayDiagram,left:r.left,right:r.right,
                caption:el.querySelector('figcaption')?.textContent.trim(),
                nodes:[...el.querySelectorAll('.flow-node')].map(n=>({
                    text:n.textContent.trim(),fontSize:parseFloat(getComputedStyle(n).fontSize),
                    clientWidth:n.clientWidth,scrollWidth:n.scrollWidth}))};
        }''')
        assert metrics['left'] >= -1 and metrics['right'] <= width + 1, 'Diagram exceeds viewport'
        assert metrics['caption'], 'Diagram needs a caption'
        assert metrics['nodes'], 'Diagram has no readable nodes'
        for node in metrics['nodes']:
            assert node['fontSize'] >= 13, f'Diagram label too small: {node}'
            assert node['scrollWidth'] <= node['clientWidth'] + 1, f'Diagram label clipped: {node}'
        if width in (390, 1440):
            diagram.screenshot(path=str(out/f'{engine}-{width}-{label}-figure-{index+1}.png'))
        results.append(metrics)
    # Locator screenshots can scroll; preserve the independent keyboard test.
    if results:
        page.evaluate('window.scrollTo(0,0)')
    return results


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
            viewports = PHONE_VIEWPORTS + ([(700,700),(701,900),(768,900),(1024,900),(1440,900)] if engine=='chromium' else [(768,900),(1440,900)])
            for width,height in viewports:
                mobile=width<=700
                context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=3 if mobile else 1,has_touch=mobile,is_mobile=mobile,color_scheme='dark')
                page=context.new_page(); errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                for route,label in routes:
                    response=page.goto(urljoin(args.url,route),wait_until='networkidle')
                    assert response and (response.ok or (route=='/404.html' and response.status==404)), f'{engine} {route}: navigation failed'
                    page.locator('img').evaluate_all('(imgs)=>{for(const i of imgs)i.loading="eager";return Promise.all(imgs.map(i=>i.decode()))}')
                    # Preserve native-density first-screen captures. Long article
                    # overviews use CSS pixels to avoid WebKit's 32767px image
                    # limit; the browser itself still runs at phone DPR=3.
                    if route=='/' or width in (390,1440): page.screenshot(path=str(out/f'{engine}-{width}-{label}-viewport.png'),full_page=False)
                    if width in (390,1440): page.screenshot(path=str(out/f'{engine}-{width}-{label}.png'),full_page=True,scale='css')
                    assert page.locator('meta[name="site-revision"]').get_attribute('content')==manifest['revision'], f'{route}: wrong revision'
                    metrics=page.evaluate('''()=>({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,
                    nav:[...document.querySelectorAll('.site-header nav a')].map(a=>({text:a.textContent,height:a.getBoundingClientRect().height})),
                    images:[...document.images].map(i=>{const frame=i.closest('.hero-portrait,.header-portrait');return {src:i.currentSrc,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height,portrait:!!frame,radius:frame?getComputedStyle(frame).borderRadius:null}}),
                    workTop:document.querySelector('.work-section')?.getBoundingClientRect().top})''')
                    metrics['identity_label_count']=verify_identity_labels(page)
                    assert metrics['scrollWidth']<=width, f'{engine} {width} {route}: horizontal overflow'
                    assert all(a['height']>=44 for a in metrics['nav']), 'Small navigation tap targets'
                    assert page.locator('h1').count()==1
                    for image in metrics['images']:
                        if not image['portrait']: continue
                        assert abs(image['width']-image['height'])<2, 'Distorted portrait'
                        assert image['radius']=='50%', 'Portrait is not circular'
                        with Image.open(io.BytesIO(request.get(image['src']).body())) as actual:
                            actual.load()
                            assert actual.width>=image['width']*(2.8 if mobile else 1), 'Insufficient portrait resolution'
                    assert page.locator('.header-portrait').count()==(0 if route=='/' else 1), 'Interior portrait missing or duplicated'
                    assert not page.locator('.portrait-aside').count(), 'Obsolete large interior portrait'
                    if route=='/': metrics['opening']=verify_home_opening(page,width,height)
                    assert bool(page.locator('.site-header a[href="/writing/"]').count())==('/writing/index.html' in manifest['files']), 'Writing navigation state is wrong'
                    metrics['diagrams']=verify_diagrams(page,width,out,engine,label)
                    if route=='/writing/close-the-loop/':
                        assert len(metrics['diagrams'])==2, 'Close the Loop must contain both approved diagrams'
                    page.evaluate('document.activeElement?.blur()'); page.keyboard.press('Tab')
                    assert page.locator('.skip-link').evaluate('(a)=>a===document.activeElement'), 'Skip link not first keyboard target'
                    page.keyboard.press('Enter')
                    assert page.locator('main').evaluate('(m)=>m===document.activeElement'), 'Skip link does not focus main'
                    page.evaluate('window.scrollTo(0,0)'); page.locator('main').evaluate('(m)=>m.blur()')
                    report['checks'].append({'engine':engine,'width':width,'height':height,'page':route,**metrics})
                assert not errors, errors
                context.close()
            browser.close()
        request.dispose()
    report['status']='passed'
    (out/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'status':'passed','url':args.url,'revision':manifest['revision'],'browser_page_checks':len(report['checks']),'hashed_files':report['hashed_files_verified']}))

if __name__=='__main__':main()
