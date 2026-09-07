"""Citation interaction and progressive-enhancement checks for every writing page."""
import json
from pathlib import Path
from playwright.sync_api import expect

_FIXTURE_ENGINES = set()


def visible_card(page):
    return page.locator('.citation-popover:popover-open')


def assert_card_fits(page):
    # Positioning runs before the next paint, after native popover activation.
    page.wait_for_function("""() => {
        const el=document.querySelector('.citation-popover:popover-open');
        if(!el || el.dataset.positioned!=='true') return false;const r=el.getBoundingClientRect();
        return r.x>=0 && r.y>=0 && r.right<=innerWidth+1 && r.bottom<=innerHeight+1;
    }""")
    box = visible_card(page).bounding_box()
    view = page.evaluate('({width:innerWidth,height:innerHeight})')
    assert box and box['x'] >= 0 and box['y'] >= 0, box
    assert box['x'] + box['width'] <= view['width'] + 1, box
    assert box['y'] + box['height'] <= view['height'] + 1, box
    assert visible_card(page).evaluate('(el)=>el.scrollWidth<=el.clientWidth+1'), 'Citation overflows horizontally'
    assert visible_card(page).locator('.citation-close').bounding_box()['height'] >= 44
    return box


def fallback_check(browser, url, mode):
    context = browser.new_context(viewport={'width':390,'height':664}, java_script_enabled=mode != 'no-js')
    if mode == 'no-css':
        context.route('**/css/citations*.css', lambda route: route.abort())
    if mode == 'unsupported':
        context.add_init_script("Object.defineProperty(HTMLElement.prototype,'showPopover',{value:undefined,configurable:true})")
    try:
        page = context.new_page()
        page.goto(url, wait_until='networkidle')
        assert page.locator('.citation-toggle').count() == 0
        link = page.locator('.article-body a.footnote-ref').first
        expect(link).to_be_visible()
        destination = link.get_attribute('href')
        link.click()
        expect(page).to_have_url(url.split('#')[0] + destination)
        target = page.locator(f'[id="{destination[1:]}"]')
        expect(target).to_be_visible()
        back = target.locator('a.footnote-backref').first
        return_to = back.get_attribute('href')
        back.click()
        expect(page).to_have_url(url.split('#')[0] + return_to)
        return 'passed'
    finally:
        context.close()


def fixture_check(browser, engine, out):
    """Exercise future notes without publishing a fake article or requiring metadata."""
    root = Path(__file__).resolve().parent.parent
    css = (root/'assets/css/citations.css').read_text()
    js = (root/'assets/js/citations.js').read_text()
    context = browser.new_context(viewport={'width':390,'height':664})
    try:
        page = context.new_page()
        page.set_content('''<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
<style>:root{--text:#eef1ee;--muted:#afbbb4;--accent:#acc8b7;--line:#2b3a34}body{padding:20px;background:#0d1513;color:#eef1ee;font:17px/1.65 sans-serif}</style>
<article class="article-body"><p>Future article <sup><a href="#fn:1" class="footnote-ref" id="fnref:1">1</a></sup>
 and repeated citation <sup><a href="#fn:1" class="footnote-ref" id="fnref1:1">1</a></sup>.
 Plain note <sup><a href="#fn:2" class="footnote-ref" id="fnref:2">2</a></sup>.
 Long note <sup><a href="#fn:3" class="footnote-ref" id="fnref:3">3</a></sup>.
 Missing target <sup><a href="#missing" class="footnote-ref" id="fnref:4">4</a></sup>.</p>
<div style="height:600px"></div><div class="footnotes"><ol>
<li id="fn:1"><p><strong><a href="https://example.com/paper">A source title</a></strong><br>Author Name · 2026</p><p>A qualification. <a href="https://example.com/other">Second source</a>.</p><a href="#fnref:1" class="footnote-backref">Back</a><a href="#fnref1:1" class="footnote-backref">Back</a></li>
<li id="fn:2"><p>A plain note with no link or bibliographic metadata.<a href="#fnref:2" class="footnote-backref">Back</a></p></li>
<li id="fn:3"><p><em>Long source</em> <a href="https://example.com/long">Read</a>.</p><p>LONG_TEXT</p><p id="note-detail">Details</p><a href="#note-detail">Detail anchor</a><a href="#fnref:3" class="footnote-backref">Back</a></li></ol></div></article>'''.replace('LONG_TEXT', 'A long qualification and source discussion. ' * 160))
        page.add_style_tag(content=css)
        page.add_script_tag(content=js)
        assert page.locator('.citation-toggle').count() == 4
        assert page.locator('.citation-popover').count() == 3
        assert page.locator('a[id="fnref:4"]').count() == 1, 'Broken references must not become broken buttons'
        page.locator('button[id="fnref:1"]').click()
        expect(visible_card(page).locator('.citation-title')).to_have_text('A source title')
        expect(visible_card(page).locator('.citation-metadata')).to_have_text('Author Name · 2026')
        expect(visible_card(page).locator('.citation-content')).to_contain_text('A qualification.')
        assert visible_card(page).locator('a[href="https://example.com/other"]').count() == 1
        page.keyboard.press('Escape')
        page.locator('button[id="fnref1:1"]').focus()
        page.keyboard.press('Space')
        expect(visible_card(page)).to_have_count(1)
        page.keyboard.press('Escape')
        expect(page.locator('button[id="fnref1:1"]')).to_be_focused()
        page.locator('button[id="fnref:2"]').click()
        expect(visible_card(page).locator('.citation-title')).to_have_text('Note 2')
        page.keyboard.press('Escape')
        page.locator('button[id="fnref:3"]').click()
        assert_card_fits(page)
        assert visible_card(page).evaluate('(el)=>el.scrollHeight>el.clientHeight'), 'Long citation should scroll inside the card'
        assert page.locator('[id="note-detail"]').count() == 1, 'Cloning duplicated IDs'
        assert page.locator('[id="citation-preview-3-note-detail"]').count() == 1
        assert visible_card(page).locator('a[href="#citation-preview-3-note-detail"]').count() == 1
        page.keyboard.press('Escape')
        page.add_script_tag(content=js)
        assert page.locator('.citation-toggle').count() == 4, 'Enhancement is not idempotent'
        (out/f'{engine}-citation-fixtures.json').write_text(json.dumps({'status':'passed','checks':['structured-title-author-year','multiple-sources','plain-note','repeated-reference','long-note-scroll','unique-ids','preserved-fragments','missing-target-fallback','idempotence']}))
    finally:
        context.close()


def verify_citations(page, width, route, out, engine, label):
    refs = page.locator('.article-body a.footnote-ref')
    if not refs.count():
        assert page.locator('.citation-toggle').count() == 0
        assert page.locator('script[data-citation-previews]').count() == 0
        return {'references':0}
    try:
        expect(page.locator('.article-body')).to_have_attribute('data-citations-ready','true')
    except AssertionError:
        diagnostic = page.evaluate('''() => ({
            showPopover:typeof HTMLElement.prototype.showPopover,
            invoker:'popoverTargetElement' in HTMLButtonElement.prototype,
            css:getComputedStyle(document.querySelector('.article-body')).getPropertyValue('--citation-previews'),
            scripts:[...document.querySelectorAll('script[data-citation-previews]')].map(s=>({src:s.src,integrity:s.integrity})),
            cards:document.querySelectorAll('.citation-popover').length,
            buttons:document.querySelectorAll('.citation-toggle').length
        })''')
        diagnostic['page_errors'] = [str(error) for error in page.page_errors()]
        (out/f'{engine}-{width}-{label}-citation-failure.json').write_text(json.dumps(diagnostic,indent=2))
        raise AssertionError(f'Citation initialization failed: {engine} {route}: {diagnostic}') from None
    triggers = page.locator('.article-body .citation-toggle')
    assert triggers.count() == refs.count(), 'Not every footnote got a preview'
    notes = page.locator('.footnotes > ol > li')
    assert page.locator('.citation-popover').count() == notes.count(), 'Must reuse one card per note'
    ids = page.locator('[id]').evaluate_all('(els)=>els.map(e=>e.id)')
    assert len(ids) == len(set(ids)), 'Duplicate IDs after citation enhancement'
    for index in range(triggers.count()):
        trigger = triggers.nth(index)
        assert trigger.get_attribute('aria-haspopup') == 'dialog'
        assert trigger.get_attribute('aria-label').startswith('Read source note ')
        target = trigger.get_attribute('popovertarget')
        card = page.locator(f'[id="{target}"]')
        original = refs.nth(index).get_attribute('href')[1:]
        note = page.locator(f'[id="{original}"]')
        links = note.locator('a[href]:not(.footnote-backref)').evaluate_all('(els)=>els.map(a=>a.href)')
        card_links = card.locator('a[href]').evaluate_all('(els)=>els.map(a=>a.href)')
        assert all(link in card_links for link in links if not link.startswith(page.url.split('#')[0]+'#')), 'Source link lost from preview'
        for block in note.locator('p').all():
            # Complete qualifications must remain, not an automatically summarized excerpt.
            text = block.evaluate('(p)=>{const c=p.cloneNode(true);c.querySelectorAll(".footnote-backref").forEach(a=>a.remove());return c.textContent.trim()}')
            combined = card.inner_text() if card.is_visible() else card.text_content()
            assert ' '.join(text.split()) in ' '.join(combined.split()), 'Citation text was dropped'
    trigger = triggers.first
    trigger.scroll_into_view_if_needed()
    before = page.evaluate('({y:scrollY,hash:location.hash})')
    if width <= 700: trigger.tap()
    else: trigger.click()
    expect(visible_card(page)).to_have_count(1)
    box = assert_card_fits(page)
    after = page.evaluate('({y:scrollY,hash:location.hash})')
    assert abs(after['y'] - before['y']) <= 2 and after['hash'] == before['hash'], 'Opening citation moved the reading position'
    if width in (390,1440):
        page.screenshot(path=str(out/f'{engine}-{width}-{label}-citation.png'),full_page=False)
        visible_card(page).screenshot(path=str(out/f'{engine}-{width}-{label}-citation-card.png'))
    # Native keyboard dismissal and accessible return to the invoking passage.
    page.keyboard.press('Escape')
    expect(visible_card(page)).to_have_count(0)
    trigger.focus();page.keyboard.press('Enter')
    expect(visible_card(page)).to_have_count(1)
    expect(visible_card(page).locator('.citation-close')).to_be_focused()
    page.keyboard.press('Tab')
    assert visible_card(page).evaluate('(p)=>p.contains(document.activeElement)'), 'Source card is not keyboard reachable'
    page.keyboard.press('Escape')
    expect(trigger).to_be_focused()
    page.keyboard.press('Space')
    expect(visible_card(page)).to_have_count(1)
    visible_card(page).locator('.citation-close').click()
    expect(trigger).to_be_focused()
    expect(visible_card(page)).to_have_count(0)
    trigger.click()
    page.mouse.click(1,1)
    expect(visible_card(page)).to_have_count(0)
    # Repeated markers reuse the note, but must return to the actual invoker.
    repeated = triggers.evaluate_all('''els => {
        const seen=new Set();for(let i=0;i<els.length;i++){
            const id=els[i].getAttribute('popovertarget');
            if(seen.has(id)) return i;seen.add(id);
        }return -1;
    }''')
    if repeated >= 0:
        again = triggers.nth(repeated)
        again.focus();page.keyboard.press('Enter')
        expect(visible_card(page)).to_have_count(1)
        page.keyboard.press('Escape')
        expect(again).to_be_focused()
    result = {'references':refs.count(),'unique_notes':notes.count(),'open_without_scroll':True,'keyboard_and_dismissal':'passed','card':box}
    if width in (390,1440):
        # Print must show the source list and original markers, not duplicate cards.
        page.emulate_media(media='print')
        expect(refs.first).to_be_visible()
        expect(triggers.first).not_to_be_visible()
        expect(page.locator('.footnotes')).to_be_visible()
        page.emulate_media(media='screen')
        page.evaluate("document.documentElement.style.fontSize='200%'")
        trigger.scroll_into_view_if_needed();trigger.click()
        assert_card_fits(page)
        page.keyboard.press('Escape')
        page.evaluate("document.documentElement.style.removeProperty('font-size')")
        result['print_and_200_percent_text']='passed'
    if width == 390:
        browser = page.context.browser
        result['no_javascript'] = fallback_check(browser,page.url,'no-js')
        result['unsupported_popover'] = fallback_check(browser,page.url,'unsupported')
        result['blocked_stylesheet'] = fallback_check(browser,page.url,'no-css')
        if engine not in _FIXTURE_ENGINES:
            fixture_check(browser,engine,out)
            _FIXTURE_ENGINES.add(engine)
    page.evaluate('document.activeElement?.blur();window.scrollTo(0,0)')
    return result
