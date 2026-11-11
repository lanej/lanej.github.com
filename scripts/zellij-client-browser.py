"""Verify the co-hosted Zellij docs, search and mobile navigation."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright
from zellij_client_docs import PREVIEW_ROUTES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    parser.add_argument('--output', default='artifacts/zellij-client-docs')
    parser.add_argument('--chromium-path', default='')
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    revision = Path('.zellij-client-version').read_text().strip()
    checks = []
    with sync_playwright() as pw:
        launch = {'headless': True}
        if args.chromium_path:
            launch.update(executable_path=args.chromium_path, args=['--no-sandbox'])
        browser = pw.chromium.launch(**launch)
        try:
            for width in (390, 1440):
                page = browser.new_page(viewport={'width': width, 'height': 900}, color_scheme='dark')
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                manifest = page.request.get(args.url.rstrip('/') + '/zellij-client.nvim/build.json')
                assert manifest.ok and manifest.json()['revision'] == revision, 'Docs revision differs from pin'
                for index, route in enumerate(PREVIEW_ROUTES):
                    response = page.goto(args.url.rstrip('/') + route, wait_until='networkidle')
                    assert response and response.ok, route
                    assert page.locator('link[rel="canonical"]').get_attribute('href') == 'https://lanej.io' + route
                    assert page.locator('h1').count() == 1
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{route}: page overflow at {width}px'
                    assert page.get_by_role('link', name='Edit page').get_attribute('href').startswith('https://github.com/lanej/zellij-client.nvim/edit/main/website/')
                    page.wait_for_function("Array.from(document.querySelectorAll('main pre')).every(node => node.scrollWidth <= node.clientWidth || node.tabIndex >= 0)")
                    assert not errors, errors
                    slug = 'client-api' if index else 'overview'
                    page.screenshot(path=str(output / f'{slug}-{width}.png'))
                    page.screenshot(path=str(output / f'{slug}-{width}-full.png'), full_page=True)
                    checks.append({'route': route, 'width': width, 'revision': revision})
                page.get_by_role('button', name='Search').click()
                page.get_by_role('dialog').get_by_role('textbox', name='Search').fill('cancellation')
                page.locator('dialog .pagefind-ui__result-link').filter(has_text='Client API').first.wait_for(state='visible')
                page.keyboard.press('Escape')
                if width == 390:
                    page.get_by_role('button', name='Menu').click()
                    page.get_by_role('link', name='Get started', exact=True).first.click()
                    page.wait_for_url('**/zellij-client.nvim/getting-started/')
                assert not errors, errors
                page.close()
        finally:
            browser.close()
    (output / 'report.json').write_text(json.dumps({'status': 'passed', 'checks': checks}, indent=2) + '\n')


if __name__ == '__main__':
    main()
