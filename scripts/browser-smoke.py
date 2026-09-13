"""Small browser smoke suite for layout behavior that static checks cannot cover."""
import argparse
import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright
from header_checks import verify_header


ROUTES = (('/', 'home'), ('/writing/', 'writing'), ('/labs/', 'labs'), ('/open-source/', 'open-source'), ('/record/', 'work'), ('/about/', 'about')) + tuple(
    (f'/writing/{path.parent.name}/', path.parent.name)
    for path in sorted(Path('public/writing').glob('*/index.html'))
)
VIEWPORTS = ((320, 480), (390, 664), (768, 900), (961, 900), (1100, 900), (1440, 900))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8765/')
    parser.add_argument('--output', default='artifacts/smoke')
    parser.add_argument('--chromium-path', default='')
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    checks = []

    with sync_playwright() as pw:
        launch = {'executable_path': args.chromium_path, 'args': ['--no-sandbox']} if args.chromium_path else {}
        browser = pw.chromium.launch(**launch)
        for width, height in VIEWPORTS:
            context = browser.new_context(
                viewport={'width': width, 'height': height},
                has_touch=width <= 700,
                is_mobile=width <= 700,
                color_scheme='dark',
            )
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))

            for route, label in ROUTES:
                response = page.goto(urljoin(args.url, route), wait_until='networkidle')
                assert response and response.ok, f'{route}: navigation failed'
                assert page.locator('h1').count() == 1, f'{route}: expected one h1'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{route}: horizontal overflow at {width}px'
                assert not errors, f'{route}: browser errors: {errors}'

                verify_header(page, width)
                page.evaluate('document.activeElement?.blur()')
                page.keyboard.press('Tab')
                assert page.locator('.skip-link').evaluate('(a) => a === document.activeElement'), f'{route}: skip link not first focus target'

                page.locator('.skip-link').evaluate('(a) => a.blur()')
                nav_heights = page.locator('.site-header nav a').evaluate_all(
                    '(items) => items.map(a => a.getBoundingClientRect().height)'
                )
                assert all(height >= 44 for height in nav_heights), f'{route}: small navigation target'

                if route == '/':
                    assert not page.locator('.home-writing time').count(), 'Homepage exposes publication dates'
                    assert page.locator('.home-writing .writing-item').count() >= 1, 'Homepage writing missing'
                    assert page.locator('.home-discovery > section').evaluate_all('(items) => items.map(el => el.id)') == ['writing', 'labs'], 'Homepage destination order changed'
                    labs = page.locator('.home-labs .lab-item')
                    assert labs.count() >= 1, 'Homepage labs missing'
                    for lab in labs.all():
                        assert lab.locator('.lab-meta').inner_text().startswith('Interactive'), 'Lab status missing'
                        assert lab.locator('h3 a').get_attribute('href').startswith('/labs/#'), 'Lab link must open its explanatory section'
                    assert page.locator('.home-labs a[href="/labs/"]').count() == 1, 'All labs link missing'
                elif route == '/writing/':
                    assert not page.locator('.writing-item time').count(), 'Writing index exposes publication dates'
                elif route.startswith('/writing/'):
                    assert not page.locator('.article-header time, .sc-meta time').count(), f'{route}: article exposes publication dates'
                    meta_text = ' '.join(page.locator('.article-meta, .sc-meta').all_text_contents())
                    assert 'min read' in meta_text, f'{route}: article missing reading time'
                    assert page.locator('.sc-section-no').all_text_contents() == [
                        f'{n:02}' for n in range(1, page.locator('.sc-section').count() + 1)
                    ], f'{route}: chapter numbering drift'
                    fonts = page.locator('h1, .sc-deck, .sc-section h2, .sc-section-copy > p').evaluate_all(
                        '(items) => items.map(el => getComputedStyle(el).fontFamily)'
                    )
                    site_font = page.locator('body').evaluate('(el) => getComputedStyle(el).fontFamily')
                    assert fonts and all(font == site_font for font in fonts), f'{route}: essay font differs from site'
                    assert page.locator('.sc-section-visuals [data-essay-diagram]').count() == page.locator('[data-essay-diagram]').count(), f'{route}: misplaced diagram'

                    assert page.locator('.sc-hero-art').count() == 1, f'{route}: missing opening visual'
                    assert page.locator('.sc-hero-copy > .sc-accent').count() == 1, f'{route}: missing opening callout'
                    if label == 'close-the-loop':
                        assert page.locator('.sc-section-copy table').count() == 0, 'Table remains in the prose column'
                        assert page.locator('.sc-section-visuals table').count() >= 1, 'Missing supporting table'
                        page.locator('.sc-section').filter(has=page.locator('table')).first.screenshot(path=str(out / f'chapter-table-{width}.png'))
                        page.locator('.sc-section-text-only').first.screenshot(path=str(out / f'chapter-centered-column-{width}.png'))
                    if label == 'socrates':
                        handoff = page.locator('#preserve-intent')
                        assert handoff.locator('[data-essay-diagram]').count() == 2, 'Handoff needs two diagrams'
                        handoff.screenshot(path=str(out / f'chapter-handoff-{width}.png'))
                    page.locator('.sc-hero').screenshot(path=str(out / f'{label}-intro-{width}.png'))

                    for index, panel in enumerate(page.locator('[data-essay-diagram]').all()):
                        panel.screenshot(path=str(out / f'{label}-{width}-diagram-{index + 1}.png'))
                    if page.locator('.footnotes').count():
                        page.locator('.footnotes').screenshot(path=str(out / f'{label}-citations-{width}.png'))
                    if width == 1440 and label in ('how-you-do-it-is-part-of-the-decision', 'socrates', 'close-the-loop'):
                        page.evaluate("document.documentElement.style.fontSize = '200%'")
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{route}: enlarged-text overflow'
                        page.locator('.sc-section').first.screenshot(path=str(out / f'{label}-enlarged-text.png'))
                        page.evaluate("document.documentElement.style.fontSize = ''")
                    page.evaluate('window.scrollTo(0, 0)')

                if route == '/labs/':
                    assert page.locator('.live-demo iframe').get_attribute('src') is None
                    if width in (390, 1440):
                        page.route('https://lanej.io/delivery-time-estimate-viz/', lambda route: route.fulfill(path='scripts/fixtures/embedded-demo.html', content_type='text/html'))
                        page.locator('.live-demo summary').click()
                        page.frame_locator('.live-demo iframe').get_by_role('heading', name='Demo fixture').wait_for()
                        page.locator('.live-demo summary').click()
                        page.wait_for_function("!document.querySelector('.live-demo iframe').hasAttribute('src')")
                        page.unroute('https://lanej.io/delivery-time-estimate-viz/')
                        page.evaluate('window.scrollTo(0, 0)')
                    assert page.locator('#delivery-time, #design-constraints').count() == 2
                    assert page.get_by_role('link', name='Open the experiment', exact=True).get_attribute('href') == 'https://lanej.io/delivery-time-estimate-viz/'
                if route == '/open-source/':
                    assert page.locator('.contributions .contribution').count() > 0
                    assert page.locator('#dotfiles, #viewrule, .github-activity').count() == 3
                    days = page.locator('.activity-calendar:visible rect').count()
                    assert 85 <= days <= 91 if width <= 700 else 365 <= days <= 371
                    page.locator('.activity-counts summary').click()
                    assert page.locator('.activity-counts table').is_visible()
                    page.locator('.activity-counts summary').click()
                if route == '/record/':
                    assert page.locator('.contributions').count() == 0
                if route == '/labs/' and width in (320, 1440):
                    page.evaluate("document.documentElement.style.fontSize = '200%'")
                    verify_header(page, width, allow_wrap=True)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    page.evaluate("document.documentElement.style.fontSize = ''")

                page.locator('.skip-link').evaluate('(a) => a.blur()')
                page.evaluate('window.scrollTo(0, 0)')
                page.screenshot(path=str(out / f'{label}-{width}.png'), full_page=False)
                checks.append({'route': route, 'width': width})

            context.close()
        browser.close()

    (out / 'report.json').write_text(json.dumps({'status': 'passed', 'checks': checks}, indent=2))
    print(json.dumps({'status': 'passed', 'browser_checks': len(checks)}))


if __name__ == '__main__':
    main()
