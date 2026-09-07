"""Prove citation underlines stay short without changing prose or source links."""
import argparse
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent.parent

FIXTURE = '''<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
<style>:root{--text:#eef1ee;--muted:#afbbb4;--accent:#acc8b7;--line:#2b3a34}
body{max-width:680px;margin:32px auto;padding:0 20px;background:#0d1513;color:#afbbb4;font:18px/1.75 sans-serif}</style>
<article class="article-body">
<p id="example">Dan North's <em>Deliberate Discovery</em> makes this distinction useful for engineering. Identify the ignorance constraining progress, then deliberately reduce it enough to proceed.<sup><a class="footnote-ref" href="#fn:1" id="fnref:1">1</a></sup> Eric Ries's original account of the minimum viable product similarly centers validated learning, not merely shipping a smaller product.<sup><a class="footnote-ref" href="#fn:2" id="fnref:2">2</a></sup> Wes Kao applies minimum effective dose directly to doing enough work to obtain the insight needed for a business decision.<sup><a class="footnote-ref" href="#fn:3" id="fnref:3">3</a></sup></p>
<p id="plain">The next note supports a long passage without naming its source, but the underline must still be a short phrase.<sup><a class="footnote-ref" href="#fn:4" id="fnref:4">4</a></sup><sup><a class="footnote-ref" href="#fn:5" id="fnref:5">5</a></sup></p>
<p id="ordinary"><a href="https://example.com/ordinary">An ordinary link</a><sup><a class="footnote-ref" href="#fn:4" id="fnref1:4">4</a></sup></p>
<p>Return to <em>Deliberate Discovery</em> later without reusing the wrong invoker.<sup><a class="footnote-ref" href="#fn:1" id="fnref1:1">1</a></sup></p>
<div class="footnotes"><ol>
<li id="fn:1"><p><strong><a href="https://example.com/discovery">Introducing Deliberate Discovery</a></strong><br>Dan North · 2010</p><p>Specific ignorance constraining delivery. This qualification must remain intact.</p><a class="footnote-backref" href="#fnref:1">Back</a></li>
<li id="fn:2"><p><strong><a href="https://example.com/mvp">What Is an MVP?</a></strong><br>Eric Ries · Lean Startup Co.</p><p>Validated learning, not simply a smaller product.</p><a class="footnote-backref" href="#fnref:2">Back</a></li>
<li id="fn:3"><p><strong><a href="https://example.com/dose">Use the minimum effective dose</a></strong><br>Wes Kao · 2020</p><p>Enough insight to make a decision.</p><a class="footnote-backref" href="#fnref:3">Back</a></li>
<li id="fn:4"><p>An unstructured source note.<a class="footnote-backref" href="#fnref:4">Back</a></p></li>
<li id="fn:5"><p>A second source for the same claim.<a class="footnote-backref" href="#fnref:5">Back</a></p></li>
</ol></div></article>'''


def prose(page):
    return page.locator('.article-body').evaluate('''el => {
        const clone=el.cloneNode(true);
        clone.querySelectorAll('.footnotes,.footnote-ref,.citation-toggle').forEach(n=>n.remove());
        return clone.textContent.replace(/\\s+/g,' ').trim();
    }''')


def enhance(page, html, css, js):
    # This test isolates text selection. The existing browser suite navigates the
    # actual build and production URLs for rendering, keyboard, touch and fallbacks.
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S|re.I)
    html = re.sub(r'<link\b[^>]*>', '', html, flags=re.I)
    page.set_content(html, wait_until='domcontentloaded')
    before = prose(page)
    links = page.locator('.article-body a[href]:not(.footnote-ref)').evaluate_all('(els)=>els.map(a=>[a.getAttribute("href"),a.textContent])')
    page.add_style_tag(content=css)
    page.add_script_tag(content=js)
    expect(page.locator('.article-body')).to_have_attribute('data-citations-ready','true')
    assert prose(page) == before, 'Enhancement changed, dropped, duplicated, or reordered article text'
    after = page.locator('.article-body a[href]:not(.footnote-ref)').evaluate_all('(els)=>els.map(a=>[a.getAttribute("href"),a.textContent])')
    assert links == after, 'Enhancement changed an authored source or ordinary link'
    phrases = page.locator('.citation-related').all_text_contents()
    for phrase in phrases:
        phrase = ' '.join(phrase.split())
        assert 0 < len(phrase) <= 64 and len(phrase.split()) <= 6, f'Overlong citation underline: {phrase!r}'
    assert page.locator('.citation-related a,.citation-related button,.citation-related .citation-related').count()==0
    fallback = page.locator('.citation-text-fallback')
    for item in fallback.all():
        expect(item).to_have_text('source')
        expect(item).to_be_visible()
    assert page.locator('.citation-toggle').count() == page.locator('a.footnote-ref').count()
    return phrases


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--engines',default='chromium,webkit')
    parser.add_argument('--chromium-path',default='')
    parser.add_argument('--site',default=str(ROOT/'public'))
    parser.add_argument('--output',default=str(ROOT/'artifacts'/'local'/'citation-phrases.json'))
    args=parser.parse_args()
    css=(ROOT/'assets/css/citations.css').read_text()
    js=(ROOT/'assets/js/citations.js').read_text()
    results=[]
    with sync_playwright() as pw:
        for engine in args.engines.split(','):
            options={'executable_path':args.chromium_path,'args':['--no-sandbox']} if engine=='chromium' and args.chromium_path else {}
            browser=getattr(pw,engine).launch(**options)
            page=browser.new_page(viewport={'width':390,'height':664})
            phrases=enhance(page,FIXTURE,css,js)
            assert phrases[:3]==['Deliberate Discovery','Eric Ries','Wes Kao'], phrases
            assert page.locator('#example em .citation-related').inner_text()=='Deliberate Discovery', 'Lost italic title'
            assert page.locator('#ordinary .citation-related').count()==0, 'Hijacked an ordinary link'
            label=page.locator('#example .citation-related').first
            label.click()
            card=page.locator('.citation-popover:popover-open')
            expect(card).to_have_count(1)
            expect(card).to_contain_text('This qualification must remain intact.')
            page.keyboard.press('Escape')
            expect(card).to_have_count(0)
            repeat=page.locator('[id="fnref1:1"]')
            repeat.focus();page.keyboard.press('Space')
            expect(card).to_have_count(1)
            page.keyboard.press('Escape');expect(repeat).to_be_focused()
            page.add_script_tag(content=js)
            assert page.locator('.citation-related').count()==len(phrases), 'Selection was not idempotent'
            results.append({'engine':engine,'page':'future-fixture','labels':phrases})
            for path in sorted(Path(args.site).glob('writing/*/index.html')):
                html=path.read_text()
                if 'footnote-ref' not in html: continue
                labels=enhance(page,html,css,js)
                results.append({'engine':engine,'page':path.parent.name,'labels':labels})
            browser.close()
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({'status':'passed','checks':results},indent=2))
    print(json.dumps({'citation_phrase_checks':len(results),'status':'passed'}))

if __name__=='__main__':main()
