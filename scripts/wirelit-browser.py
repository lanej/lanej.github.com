"""Check the co-hosted documentation at mobile and desktop sizes."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright
from wirelit_docs import PREVIEW_ROUTES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    parser.add_argument('--output', default='artifacts/wirelit-docs')
    parser.add_argument('--chromium-path', default='')
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    revision = Path('.wirelit-version').read_text().strip()
    checks = []
    with sync_playwright() as pw:
        launch = {'executable_path': args.chromium_path, 'args': ['--no-sandbox']} if args.chromium_path else {}
        browser = pw.chromium.launch(**launch)
        for width in (390, 1440):
            page = browser.new_page(viewport={'width': width, 'height': 900}, color_scheme='dark')
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            manifest = page.request.get(args.url.rstrip('/') + '/wirelit/build.json')
            assert manifest.ok and manifest.json()['revision'] == revision, 'Wirelit revision differs from the pin'
            for index, route in enumerate(PREVIEW_ROUTES):
                response = page.goto(args.url.rstrip('/') + route, wait_until='networkidle')
                assert response and response.ok, route
                assert page.locator('link[rel="canonical"]').get_attribute('href') == 'https://lanej.io' + route
                assert page.locator('h1').count() == 1, route
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{route}: overflow at {width}px'
                page.locator('img').evaluate_all('(images) => Promise.all(images.map(image => image.decode()))')
                if index:
                    assert page.locator('.wirelit-signature a').count() == 2, 'Linked request/response signature is missing'
                    page.get_by_role('tab', name='Go', exact=True).click()
                    assert page.locator('[role="tabpanel"]:visible').count() >= 1
                    page.get_by_role('tab', name='HTTP / JSON', exact=True).click()
                assert not errors, errors
                slug = 'method' if index else 'overview'
                page.screenshot(path=str(out / f'{slug}-{width}.png'))
                checks.append({'route': route, 'width': width, 'revision': revision})
            page.close()
        browser.close()
    (out / 'report.json').write_text(json.dumps({'status': 'passed', 'checks': checks}, indent=2) + '\n')


if __name__ == '__main__':
    main()
