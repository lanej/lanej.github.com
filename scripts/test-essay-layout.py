"""One regression check for the STYLE.md-to-browser contract boundary."""
import argparse
import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
smoke = runpy.run_path(str(ROOT / 'scripts/browser-smoke.py'))
read_contract = smoke['read_essay_layout']
layout_errors = smoke['chapter_layout_errors']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8765/')
    parser.add_argument('--chromium-path', default='')
    args = parser.parse_args()
    source = (ROOT / 'STYLE.md').read_text()
    contract = read_contract()
    fence = '```json essay-layout\n'
    body = json.dumps(contract)
    with TemporaryDirectory() as directory:
        path = Path(directory) / 'STYLE.md'
        for invalid in (
            'No contract here.', fence + body, fence + '{bad json}\n```',
            source + '\n' + source,
            fence + body.replace('"centered": true', '"centered": true, "centered": true') + '\n```',
            *[fence + json.dumps(case) + '\n```' for case in (
                {key: value for key, value in contract.items() if key != 'max_width_px'},
                dict(contract, unexpected=True), dict(contract, max_width_px=True),
                dict(contract, geometry_tolerance_px=float('nan')),
                dict(contract, centered=False), dict(contract, text_align='justify'),
                dict(contract, prose_columns=2), dict(contract, content_order=['prose', 'heading', 'visuals']),
            )],
        ):
            path.write_text(invalid)
            try:
                read_contract(path)
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid STYLE.md contract was accepted')

        # Change the document, not a detector constant or the CSS being measured.
        revised = dict(contract, max_width_px=contract['max_width_px'] + 40)
        path.write_text(fence + json.dumps(revised) + '\n```\n')
        revised = read_contract(path)
        with sync_playwright() as pw:
            launch = {'executable_path': args.chromium_path, 'args': ['--no-sandbox']} if args.chromium_path else {}
            browser = pw.chromium.launch(**launch)
            page = browser.new_page(viewport={'width': 1440, 'height': 900})
            response = page.goto(args.url.rstrip('/') + '/writing/how-you-do-it-is-part-of-the-decision/')
            assert response and response.ok
            assert page.locator('.sc-section').count(), 'Expected real essay chapters'
            assert not layout_errors(page, contract), 'Current contract does not match the site'
            assert layout_errors(page, revised), 'Document-only measure change went undetected'
            override = page.add_style_tag(content=f".sc-article{{--copy:{revised['max_width_px']}px}}")
            assert layout_errors(page, contract), 'CSS-only measure change went undetected'
            assert not layout_errors(page, revised), 'Matching document and CSS changes should pass'
            override.evaluate('(el) => el.remove()')
            assert not layout_errors(page, contract), 'Restored layout should pass'
            browser.close()
    print('Passed essay contract validation and document/CSS mismatch regression')


if __name__ == '__main__':
    main()
