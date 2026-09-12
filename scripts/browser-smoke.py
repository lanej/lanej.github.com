"""Small browser smoke suite for layout behavior that static checks cannot cover."""
import argparse
import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


ROUTES = (('/', 'home'), ('/writing/', 'writing')) + tuple(
    (f'/writing/{path.parent.name}/', path.parent.name)
    for path in sorted(Path('public/writing').glob('*/index.html'))
)
VIEWPORTS = ((320, 480), (390, 664), (768, 900), (961, 900), (1100, 900), (1440, 900))


def chapter_layout_errors(page):
    """One shared detector for measure, column order, and supporting placement."""
    return page.locator('.sc-section').evaluate_all('''(chapters) => chapters.flatMap(chapter => {
        const copy = chapter.querySelector('.sc-section-copy');
        const text = chapter.querySelector('.sc-section-text').getBoundingClientRect();
        const header = chapter.querySelector('.sc-section-header').getBoundingClientRect();
        const visual = chapter.querySelector('.sc-section-visuals')?.getBoundingClientRect();
        const body = chapter.closest('.article-body').getBoundingClientRect();
        const rootSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
        const wide = !matchMedia('print').matches && body.width >= 64 * rootSize;
        const maxCopy = parseFloat(getComputedStyle(chapter).getPropertyValue('--copy'));
        const gap = parseFloat(getComputedStyle(chapter).columnGap);
        const measure = wide ? (body.width - gap) / 2 : Math.min(body.width, maxCopy);
        const name = chapter.querySelector('h2').textContent;
        const errors = [];
        if (header.bottom > text.top + 1 || (visual && header.bottom > visual.top + 1))
            errors.push('heading overlaps chapter content');
        if (visual) {
            if (Math.abs(text.width - measure) > 2 || Math.abs(visual.width - measure) > 2)
                errors.push('supporting tracks have inconsistent measure');
            if (wide) {
                if (Math.abs(visual.left - text.right - gap) > 2 ||
                    Math.abs((visual.top + visual.bottom - text.top - text.bottom) / 2) > 2)
                    errors.push('supporting column is not aligned');
            } else if (visual.top < text.bottom) errors.push('visual overlaps copy');
        } else {
            const columns = parseInt(getComputedStyle(copy).columnCount) || 1;
            if (columns !== (wide ? 2 : 1)) errors.push('incorrect prose column count');
            const bounds = copy.getBoundingClientRect();
            let previousColumn = 0;
            let previousTop = -Infinity;
            for (const paragraph of copy.querySelectorAll(':scope > p')) {
                for (const rect of paragraph.getClientRects()) {
                    if (!rect.width || !rect.height) continue;
                    if (Math.abs(rect.width - measure) > 2) errors.push('paragraph measure drift');
                    const column = wide ? Math.round((rect.left - bounds.left) / (measure + gap)) : 0;
                    if (column > 1 || column < previousColumn ||
                        (column === previousColumn && rect.top < previousTop - 1))
                        errors.push('prose is not ordered down each column');
                    previousColumn = column;
                    previousTop = rect.top;
                }
            }
        }
        return errors.map(error => name + ': ' + error);
    })''')


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

                nav_heights = page.locator('.site-header nav a').evaluate_all(
                    '(items) => items.map(a => a.getBoundingClientRect().height)'
                )
                assert all(height >= 44 for height in nav_heights), f'{route}: small navigation target'

                if route == '/':
                    assert not page.locator('.home-writing time').count(), 'Homepage exposes publication dates'
                    assert page.locator('.home-writing .writing-item').count() >= 1, 'Homepage writing missing'
                elif route == '/writing/':
                    assert not page.locator('.writing-item time').count(), 'Writing index exposes publication dates'
                else:
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

                    layout_errors = chapter_layout_errors(page)
                    assert not layout_errors, f'{route} at {width}px: {layout_errors}'
                    assert page.locator('.sc-hero-art').count() == 1, f'{route}: missing opening visual'
                    assert page.locator('.sc-hero-copy > .sc-accent').count() == 1, f'{route}: missing opening callout'
                    if label == 'close-the-loop':
                        assert page.locator('.sc-section-copy table').count() == 0, 'Table remains in the prose column'
                        assert page.locator('.sc-section-visuals table').count() >= 1, 'Missing supporting table'
                        page.locator('.sc-section').filter(has=page.locator('table')).first.screenshot(path=str(out / f'chapter-table-{width}.png'))
                        page.locator('.sc-section-text-only').first.screenshot(path=str(out / f'chapter-reading-columns-{width}.png'))
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
                        assert not chapter_layout_errors(page), f'{route}: enlarged-text chapter reflow failed'
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{route}: enlarged-text overflow'
                        page.locator('.sc-section').first.screenshot(path=str(out / f'{label}-enlarged-text.png'))
                        page.evaluate("document.documentElement.style.fontSize = ''")
                        page.emulate_media(media='print')
                        assert not chapter_layout_errors(page), f'{route}: print chapter order failed'
                        page.emulate_media(media='screen')
                    page.evaluate('window.scrollTo(0, 0)')

                page.evaluate('document.activeElement?.blur()')
                page.keyboard.press('Tab')
                assert page.locator('.skip-link').evaluate('(a) => a === document.activeElement'), f'{route}: skip link not first focus target'

                page.screenshot(path=str(out / f'{label}-{width}.png'), full_page=False)
                checks.append({'route': route, 'width': width})

            context.close()
        browser.close()

    (out / 'report.json').write_text(json.dumps({'status': 'passed', 'checks': checks}, indent=2))
    print(json.dumps({'status': 'passed', 'browser_checks': len(checks)}))


if __name__ == '__main__':
    main()
