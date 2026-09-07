"""Verify the approved Socrates composition, locally and on the public domain."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urljoin
from PIL import Image
from playwright.sync_api import sync_playwright

WIDTHS = (320, 360, 375, 390, 430, 640, 700, 768, 900, 960, 961, 1024, 1280, 1440, 1920)
ART_BLOB = 'def8c8450d68cd02a6f7ce38522c94b3e597b1ac'
MEASURE = r'''() => {
    const failures = [];
    const box = el => {const r=el.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height}};
    const visible = el => el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden';
    const within = (a,b,t=2) => a.x>=b.x-t && a.y>=b.y-t && a.right<=b.right+t && a.bottom<=b.bottom+t;
    const overlap = (a,b) => Math.min(a.right,b.right)-Math.max(a.x,b.x)>2 && Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y)>2;
    if (document.documentElement.scrollWidth>innerWidth+1) failures.push('Page overflow');
    const root = document.querySelector('.sc-article');
    if(!root) return {failures:['Missing Socrates article']};
    for(const el of root.querySelectorAll('[data-node],.sc-layer-description,.sc-step-detail,.sc-figure-title,.sc-caption,.sc-deck,h1,h2,.sc-section-copy')) {
        if(!visible(el)) continue;
        const b=box(el);
        if(el.scrollWidth>el.clientWidth+2) failures.push('Horizontal overflow: '+el.textContent.trim().slice(0,80));
        if(el.scrollHeight>el.clientHeight+2) failures.push('Vertical clipping: '+el.textContent.trim().slice(0,80));
        const walk=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
        while(walk.nextNode()) {
            const node=walk.currentNode;
            if(!node.textContent.trim() || !visible(node.parentElement)) continue;
            const range=document.createRange();range.selectNodeContents(node);
            for(const r of range.getClientRects()) {
                if(!within({x:r.x,y:r.y,right:r.right,bottom:r.bottom},b,3)) failures.push('Text outside box: '+node.textContent.trim().slice(0,60));
            }
        }
    }
    const panels=[...root.querySelectorAll('.sc-figure')];
    if(panels.length!==4) failures.push('Expected four diagrams');
    const measures=panels.map(panel=>{
        const bounds=box(panel);
        if(bounds.x<0 || bounds.right>innerWidth+1) failures.push('Figure outside screen');
        const nodes=[...panel.querySelectorAll('[data-node]')];
        nodes.forEach((el,i)=>{
            if(!within(box(el),bounds)) failures.push('Node outside figure');
            nodes.slice(i+1).forEach(other=>{if(overlap(box(el),box(other))) failures.push('Overlapping diagram nodes')});
        });
        if(!within(box(panel.querySelector('figcaption')),bounds)) failures.push('Caption outside figure');
        return {id:panel.id,...bounds,nodes:nodes.length};
    });
    for(const m of measures.slice(1)) if(Math.abs(m.x-measures[0].x)>2 || Math.abs(m.right-measures[0].right)>2) failures.push('Diagram columns not aligned');
    const paths=[...root.querySelectorAll('.sc-path')];
    if(Math.abs(box(paths[0]).y-box(paths[1]).y)<2) {
        const a=[...paths[0].querySelectorAll('[data-node]')], b=[...paths[1].querySelectorAll('[data-node]')];
        if(Math.abs(box(a[0]).y-box(b[0]).y)>2 || Math.abs(box(a.at(-1)).bottom-box(b.at(-1)).bottom)>2) failures.push('Comparison start/end rails not aligned');
    }
    const steps=[...root.querySelectorAll('.sc-step')];
    const connectors=[...root.querySelectorAll('.sc-workflow-connector')];
    const horizontal=Math.abs(box(steps[0]).y-box(steps.at(-1)).y)<2;
    if(horizontal) {
        const r=box(root.querySelector('.sc-return-path'));
        const first=box(steps[0]), last=box(steps.at(-1));
        if(Math.abs(r.x-(first.x+first.width/2))>3 || Math.abs(r.right-(last.x+last.width/2))>3) failures.push('Return path endpoints misaligned');
        connectors.forEach((el,i)=>{const c=box(el),s=box(steps[i]);if(Math.abs(c.y+c.height/2-(s.y+s.height/2))>2) failures.push('Horizontal connector off center')});
    } else {
        connectors.forEach((el,i)=>{const c=box(el),s=box(steps[i]);if(Math.abs(c.x+c.width/2-(s.x+s.width/2))>2) failures.push('Vertical connector off center')});
    }
    if(!horizontal) {
        const ret=root.querySelector('.sc-return-path'), label=ret.querySelector('.sc-return-label');
        const marker=getComputedStyle(ret,'::before');
        if(box(label).x-box(ret).x < parseFloat(marker.fontSize)*.9) failures.push('Return marker collides with label');
    }
    for(const c of root.querySelectorAll('.sc-cycle-connector,.sc-flow-connector,.sc-workflow-connector')) {
        if(!visible(c)) continue;
        for(const n of c.closest('.sc-figure').querySelectorAll('[data-node]')) if(overlap(box(c),box(n))) failures.push('Connector crosses a node');
    }
    for(const img of root.querySelectorAll('img')) if(!img.complete || img.naturalWidth===0) failures.push('Undecoded art');
    return {failures:[...new Set(failures)],width:innerWidth,rootFont:parseFloat(getComputedStyle(document.documentElement).fontSize),panels:measures,workflow:horizontal?'horizontal':'vertical'};
}'''


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--url',default='http://127.0.0.1:8765/')
    parser.add_argument('--root',default='public')
    parser.add_argument('--output',default='artifacts/local/socrates')
    parser.add_argument('--engines',default='chromium,webkit')
    args=parser.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((Path(args.root)/'build.json').read_text())
    report={'url':urljoin(args.url,'writing/socrates/'),'revision':manifest['revision'],'checks':[],'status':'running'}
    try:
        with sync_playwright() as pw:
            request=pw.request.new_context()
            response=request.get(urljoin(args.url,'writing/socrates/socrates-bust.webp'))
            assert response.ok, 'Published illustration unavailable'
            art=response.body()
            assert hashlib.sha1(f'blob {len(art)}\0'.encode()+art).hexdigest()==ART_BLOB, 'Illustration bytes changed during transfer'
            with Image.open(io.BytesIO(art)) as im:
                im.load();assert im.size==(270,322)
            report['art_bytes_verified']=len(art)
            request.dispose()
            for engine in args.engines.split(','):
                browser=getattr(pw,engine).launch()
                for width in WIDTHS:
                    context=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,color_scheme='dark')
                    page=context.new_page()
                    response=page.goto(report['url'],wait_until='networkidle')
                    assert response and response.ok
                    assert page.locator('meta[name="site-revision"]').get_attribute('content')==manifest['revision'], 'Wrong live revision'
                    assert page.locator('.sc-section').count()==4
                    assert page.locator('h1').count()==1
                    page.locator('img').evaluate_all('imgs=>Promise.all(imgs.map(i=>i.decode()))')
                    for scale in (100,200):
                        page.evaluate('(v)=>{document.documentElement.style.fontSize=v+"%";window.scrollTo(0,0)}',scale)
                        metrics=page.evaluate(MEASURE)
                        report['checks'].append({'engine':engine,'text_scale':scale,**metrics})
                        assert metrics['rootFont']>=(32 if scale==200 else 16)
                        if (width in (390,1440) and scale==100) or (width==320 and scale==200):
                            stem=f'{engine}-{width}-text{scale}'
                            page.screenshot(path=str(out/f'{stem}-opening.png'),scale='css')
                            page.screenshot(path=str(out/f'{stem}-full.png'),full_page=True,scale='css')
                            for panel in page.locator('.sc-figure').all():
                                panel.screenshot(path=str(out/f'{stem}-{panel.get_attribute("id")}.png'),scale='css')
                        assert not metrics['failures'], f'{engine} {width} {scale}%: {metrics["failures"]}'
                    context.close()
                browser.close()
        report['status']='passed'
    except Exception as error:
        report['status']='failed';report['error']=str(error)
        raise
    finally:
        (out/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'status':report['status'],'url':report['url'],'cases':len(report['checks']),'revision':report['revision']}))

if __name__=='__main__':main()
