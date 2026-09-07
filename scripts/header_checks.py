"""Header contract: readable links at left, an accessible portrait home link at right."""


def verify_header(page, width, *, allow_wrap=False):
    header = page.locator('.site-header')
    home = header.evaluate('(el) => el.classList.contains("home-header")')
    # inner_text ignores attributes: an accessible name must not become visible chrome.
    assert 'Josh Lane' not in header.inner_text(), 'Visible name returned to the header'
    links = header.locator('nav a')
    expected = ['About', 'Work', 'Contact']
    if header.locator('a[href="/writing/"]').count():
        expected.insert(0, 'Writing')
    assert links.all_text_contents() == expected, 'Navigation labels/order changed'
    assert header.locator('.wordmark').count() == (0 if home else 1), 'Unexpected home-link count'
    if not home:
        avatar = header.get_by_role('link', name='Josh Lane — home', exact=True)
        assert avatar.count() == 1 and avatar.get_attribute('href') == '/', 'Portrait lost its accessible home link'
        assert avatar.locator('.header-portrait img').count() == 1
        assert avatar.evaluate('(a) => a.previousElementSibling?.tagName === "NAV"'), 'Keyboard order must follow navigation then portrait'
    metrics = header.evaluate('''el => {
        const box = n => {const r=n.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};};
        const visible = n => {const s=getComputedStyle(n);return s.display!=='none' && s.visibility==='visible' && +s.opacity>0;};
        const nav=el.querySelector('nav'), avatar=el.querySelector('.wordmark');
        return {frame:box(el),shell:box(el.querySelector('.nav-shell')),nav:box(nav),
            avatar:avatar?box(avatar):null,rootFont:parseFloat(getComputedStyle(document.documentElement).fontSize),
            links:[...nav.querySelectorAll('a')].map(a=>({text:a.textContent,...box(a),
                font:parseFloat(getComputedStyle(a).fontSize),visible:visible(a),
                clipped:a.scrollWidth>a.clientWidth+1 || a.scrollHeight>a.clientHeight+1}))};
    }''')
    frame, nav, avatar = metrics['frame'], metrics['nav'], metrics['avatar']
    assert frame['height'] > 0 and frame['left'] >= -1 and frame['right'] <= width + 1
    for item in metrics['links']:
        assert item['visible'] and not item['clipped'], f'Hidden or clipped navigation: {item}'
        assert item['width'] >= 44 and item['height'] >= 44, f'Navigation target below 44px: {item}'
        assert item['font'] >= (28 if allow_wrap else 14), 'Navigation text was shrunk to fit'
        assert item['left'] >= nav['left'] - 1 and item['right'] <= nav['right'] + 1
        assert item['top'] >= frame['top'] and item['bottom'] <= frame['bottom'], 'Navigation escapes header'
    if avatar:
        assert abs(avatar['width'] - 44) <= 1 and abs(avatar['height'] - 44) <= 1, 'Portrait home target must stay 44px'
        assert avatar['left'] >= nav['right'] + 8, 'Portrait must sit to the right, without overlap'
        assert abs(avatar['right'] - metrics['shell']['right']) <= 1, 'Portrait not aligned to right margin'
        assert avatar['top'] >= frame['top'] and avatar['bottom'] <= frame['bottom'], 'Portrait is clipped'
        assert abs((avatar['top']+avatar['bottom'])/2 - (nav['top']+nav['bottom'])/2) <= 1, 'Portrait and navigation are not aligned'
    if not allow_wrap:
        centers = [(item['top']+item['bottom'])/2 for item in metrics['links']]
        assert max(centers) - min(centers) <= 1, 'Navigation stacked at normal text size'
        assert nav['height'] <= 45, 'Navigation is not a single row'
        if width <= 700:
            assert frame['height'] <= 64, 'Mobile header regained an extra row'
    return metrics
