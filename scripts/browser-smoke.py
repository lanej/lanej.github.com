"""Small browser smoke suite for layout behavior that static checks cannot cover."""
import argparse
import json
import math
import re
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


ROUTES = (('/', 'home'), ('/writing/', 'writing')) + tuple(
    (f'/writing/{path.parent.name}/', path.parent.name)
    for path in sorted(Path('public/writing').glob('*/index.html'))
)
VIEWPORTS = ((320, 480), (390, 664), (768, 900), (961, 900), (1100, 900), (1440, 900))


def read_essay_layout(path=Path(__file__).resolve().parent.parent / 'STYLE.md'):
    """Read the one explicit contract; prose elsewhere in the guide is not parsed."""
    source = path.read_text()
    marker = '```json essay-layout'
    blocks = re.findall(r'^```json essay-layout\n(.*?)\n```[ \t]*$', source, re.M | re.S)
    if source.count(marker) != 1 or len(blocks) != 1:
        raise ValueError('STYLE.md: expected exactly one closed json essay-layout block')

    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'STYLE.md: duplicate essay-layout key {key}')
            result[key] = value
        return result

    try:
        contract = json.loads(blocks[0], object_pairs_hook=unique_keys)
    except json.JSONDecodeError as error:
        raise ValueError(f'STYLE.md: invalid essay-layout JSON: {error.msg}') from error
    fields = {'max_width_px', 'centered', 'text_align', 'prose_columns',
              'content_order', 'geometry_tolerance_px'}
    if not isinstance(contract, dict) or set(contract) != fields:
        raise ValueError('STYLE.md: essay-layout has missing or unsupported keys')
    width = contract['max_width_px']
    tolerance = contract['geometry_tolerance_px']
    if type(width) is not int or width <= 0:
        raise ValueError('STYLE.md: max_width_px must be a positive integer')
    if type(tolerance) not in (int, float) or not math.isfinite(tolerance) or not 0 <= tolerance <= 4:
        raise ValueError('STYLE.md: geometry_tolerance_px must be between 0 and 4')
    if (contract['centered'] is not True or contract['text_align'] != 'left'
            or type(contract['prose_columns']) is not int or contract['prose_columns'] != 1
            or contract['content_order'] != ['heading', 'prose', 'visuals']):
        raise ValueError('STYLE.md: unsupported essay layout; detector supports centered, '
                         'left-aligned, single-column chapters ordered heading, prose, visuals')
    return contract


def chapter_layout_errors(page, contract):
    """One shared detector compares the rendered layout with STYLE.md."""
    return page.locator('.sc-article').evaluate_all('''(articles, contract) => articles.flatMap(article => {
        const bounds = article.getBoundingClientRect();
        const measure = Math.min(bounds.width, contract.max_width_px);
        const tolerance = contract.geometry_tolerance_px;
        const center = bounds.left + bounds.width / 2;
        const errors = [];
        for (const el of article.querySelectorAll('.sc-section, .sc-section-header, .sc-section-text, .sc-section-visuals, .footnotes, .article-footer')) {
            const rect = el.getBoundingClientRect();
            if (!rect.width || !rect.height) continue;
            if (Math.abs(rect.width - measure) > tolerance || (contract.centered && Math.abs(rect.left + rect.width / 2 - center) > tolerance))
                errors.push(el.className + ': expected centered ' + measure + 'px reading column (STYLE.md)');
        }
        for (const chapter of article.querySelectorAll('.sc-section')) {
            const copy = chapter.querySelector('.sc-section-copy');
            const boxes = {
                heading: chapter.querySelector('.sc-section-header').getBoundingClientRect(),
                prose: copy.getBoundingClientRect(),
                visuals: chapter.querySelector('.sc-section-visuals')?.getBoundingClientRect(),
            };
            const order = contract.content_order.map(key => boxes[key]).filter(Boolean);
            const name = chapter.querySelector('h2').textContent;
            if (order.some((rect, index) => index && order[index - 1].bottom > rect.top + tolerance))
                errors.push(name + ': expected ' + contract.content_order.join(', ') + ' order (STYLE.md)');
            if ((parseInt(getComputedStyle(copy).columnCount) || 1) !== contract.prose_columns)
                errors.push(name + ': prose is split into columns (STYLE.md)');
            let previousBottom = -Infinity;
            for (const paragraph of copy.querySelectorAll(':scope > p')) {
                const rect = paragraph.getBoundingClientRect();
                const style = getComputedStyle(paragraph);
                let alignment = style.textAlign;
                if (alignment === 'start') alignment = style.direction === 'rtl' ? 'right' : 'left';
                if (alignment === 'end') alignment = style.direction === 'rtl' ? 'left' : 'right';
                if (alignment !== contract.text_align)
                    errors.push(name + ': prose must be ' + contract.text_align + '-aligned (STYLE.md)');
                if (Math.abs(rect.width - measure) > tolerance || rect.top < previousBottom - tolerance)
                    errors.push(name + ': paragraph measure or reading order drift (STYLE.md)');
                previousBottom = rect.bottom;
            }
        }
        return errors;
    })''', contract)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8765/')
    parser.add_argument('--output', default='artifacts/smoke')
    parser.add_argument('--chromium-path', default='')
    args = parser.parse_args()
    contract = read_essay_layout()
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

                    layout_errors = chapter_layout_errors(page, contract)
                    assert not layout_errors, f'{route} at {width}px: {layout_errors}'
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
                        assert not chapter_layout_errors(page, contract), f'{route}: enlarged-text chapter reflow failed'
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{route}: enlarged-text overflow'
                        page.locator('.sc-section').first.screenshot(path=str(out / f'{label}-enlarged-text.png'))
                        page.evaluate("document.documentElement.style.fontSize = ''")
                        page.emulate_media(media='print')
                        assert not chapter_layout_errors(page, contract), f'{route}: print chapter order failed'
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
