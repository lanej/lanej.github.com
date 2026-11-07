"""Check preview scope and preservation of human-authored PR text."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('previews', Path(__file__).with_name('pr-previews.py'))
previews = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previews)


class PreviewTests(unittest.TestCase):
    routes = {'/', '/record/', '/labs/', '/open-source/', '/about/', '/writing/', '/writing/example/'}

    def test_publish_works_without_installed_build_dependencies(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            head, build = 'a' * 40, 'b' * 40
            event = {'pull_request': {'number': 85, 'head': {
                'sha': head, 'repo': {'full_name': 'owner/site'}}}}
            (out / 'event.json').write_text(json.dumps(event))
            images = {label: {'viewport': 'preview.png', 'full': 'preview.png'}
                      for label in ('mobile', 'desktop')}
            (out / 'manifest.json').write_text(json.dumps({
                'head_sha': head, 'build_sha': build, 'pages': [
                    {'route': '/wirelit/', 'title': 'Wirelit', 'images': images}]}))
            (out / 'preview.png').write_bytes(b'fixture image bytes')
            # Execute the real CLI with site-packages disabled, as on the
            # publishing runner. Only the GitHub transport is replaced.
            runner = '''
import io, json, runpy, sys
from pathlib import Path
from unittest.mock import patch
script, output = sys.argv[1:]
sys.path.insert(0, str(Path(script).parent))
sys.argv = [script, 'publish', '--output', output]
pr = {'head': {'sha': 'a' * 40}, 'state': 'open', 'body': 'Human notes'}
responses = [pr, {'object': {'sha': 'parent'}}, {'sha': 'blob'},
             {'sha': 'tree'}, {'sha': 'images-commit'}, {}, pr, {}]
with patch('urllib.request.urlopen', side_effect=[io.StringIO(json.dumps(r)) for r in responses]) as transport:
    runpy.run_path(script, run_name='__main__')
assert transport.call_count == len(responses)
last = transport.call_args.args[0]
assert last.get_method() == 'PATCH' and last.full_url.endswith('/pulls/85')
body = json.loads(last.data)['body']
assert body.startswith('Human notes')
assert '<!-- page-previews:start -->' in body
assert 'https://raw.githubusercontent.com/owner/site/images-commit/preview.png' in body
'''
            env = dict(os.environ, PYTHONPATH='', GITHUB_REPOSITORY='owner/site',
                       GITHUB_EVENT_PATH=str(out / 'event.json'), GITHUB_SHA=build,
                       GITHUB_RUN_ID='123', GH_TOKEN='fixture-token')
            result = subprocess.run([sys.executable, '-S', '-c', runner,
                                     str(Path(__file__).with_name('pr-previews.py').resolve()), str(out)],
                                    env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('Updated PR #85 with 1 page previews.', result.stdout)

    def test_company_icons_affect_work(self):
        self.assertEqual(previews.affected_routes(
            ['assets/css/work.css', 'static/logos/companies/easypost.svg', 'STYLE.md'], self.routes), ['/open-source/', '/record/'])

    def test_contributions_affect_open_source(self):
        self.assertEqual(previews.affected_routes(
            ['data/contributions.yaml', 'layouts/partials/contributions.html',
             'static/logos/projects/ogen-github.png'], self.routes), ['/open-source/'])

    def test_shared_template_affects_every_page(self):
        self.assertEqual(previews.affected_routes(['layouts/partials/header.html'], self.routes), sorted(self.routes))
        self.assertEqual(previews.affected_routes(['.ui-review/rules.json'], self.routes), sorted(self.routes))

    def test_career_data_and_role_shortcodes_affect_work(self):
        self.assertEqual(previews.affected_routes(
            ['data/career.yaml', 'layouts/shortcodes/work-role.html',
             'layouts/shortcodes/career-timeline.html'], self.routes), ['/record/'])

    def test_article_also_affects_indexes(self):
        self.assertEqual(previews.affected_routes(['content/writing/example/index.md'], self.routes),
                         ['/', '/writing/', '/writing/example/'])

    def test_deleted_article_has_only_existing_indexes(self):
        self.assertEqual(previews.affected_routes(['content/writing/deleted/index.md'], self.routes), ['/', '/writing/'])

    def test_docs_and_workflows_do_not_change_rendered_pages(self):
        self.assertEqual(previews.affected_routes(['README.md', '.github/workflows/pages.yml'], self.routes), [])

    def test_refresh_preserves_surrounding_text_and_is_idempotent(self):
        old = previews.START + '\nOld pictures\n' + previews.END
        new = previews.START + '\nNew pictures\n' + previews.END
        body = 'Human introduction\n\n' + old + '\n\nHuman notes'
        updated = previews.replace_section(body, new)
        self.assertEqual(updated, 'Human introduction\n\n' + new + '\n\nHuman notes')
        self.assertEqual(previews.replace_section(updated, new), updated)

    def test_empty_body(self):
        self.assertIn(previews.START, previews.replace_section('', previews.START + previews.END))

    def test_no_changed_pages_remove_stale_gallery_and_preserve_human_text(self):
        body = 'Human introduction\n\n' + previews.START + '\nOld gallery\n' + previews.END + '\n\nHuman notes'
        self.assertEqual(previews.replace_section(body, ''), 'Human introduction\n\n\n\nHuman notes')
        self.assertEqual(previews.replace_section('Human notes', ''), 'Human notes')

    def test_every_changed_page_is_shown_without_unrelated_page_padding(self):
        pages = [{'title': f'Page {i}', 'route': f'/page-{i}/',
                  'images': {label: {'viewport': f'{i}-{label}.png', 'full': f'{i}-{label}-full.png'}
                             for label in ('mobile', 'desktop')}} for i in range(8)]
        section = previews.preview_section({'head_sha': 'a' * 40, 'pages': pages},
                                           'https://images.invalid', 'https://ci.invalid/run')
        self.assertEqual(section.count('<details>'), 8)
        self.assertEqual(section.count('<img '), 16)
        self.assertNotIn('<details open>', section)
        self.assertNotIn('Showing 3 of', section)
        self.assertIn('/page-7/', section)

    def test_rendered_filter_keeps_only_changed_and_new_pages(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            current, baseline = root / 'current', root / 'baseline'
            for directory in (current, baseline):
                directory.mkdir()
                (directory / 'index.html').write_text('<h1>Same homepage</h1>')
                (directory / 'about').mkdir()
                (directory / 'about/index.html').write_text('<h1>Old biography</h1>')
            (current / 'about/index.html').write_text('<h1>Revised biography</h1>')
            (current / 'new').mkdir()
            (current / 'new/index.html').write_text('<h1>New page</h1>')
            self.assertEqual(previews.rendered_changes(['/', '/about/', '/new/'], current, baseline),
                             ['/about/', '/new/'])

    def test_unchanged_asset_url_with_changed_image_is_a_page_change(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            current, baseline = root / 'current', root / 'baseline'
            for directory, image in ((current, b'new image'), (baseline, b'old image')):
                directory.mkdir()
                (directory / 'index.html').write_text('<img src="/portrait.png?v=1">')
                (directory / 'portrait.png').write_bytes(image)
            self.assertEqual(previews.rendered_changes(['/'], current, baseline), ['/'])
            (baseline / 'portrait.png').write_bytes(b'new image')
            self.assertEqual(previews.rendered_changes(['/'], current, baseline), [])

    def test_srcset_assets_are_compared(self):
        self.assertEqual(previews.PageAssets('<img srcset="/small.png 1x, /large.png 2x">').paths,
                         {'/small.png', '/large.png'})

    def test_preview_inventory_excludes_embedded_storybooks(self):
        with tempfile.TemporaryDirectory() as temporary:
            public = Path(temporary)
            (public / 'build.json').write_text(json.dumps({'files': {
                '/index.html': 'home', '/about/index.html': 'about', '/404.html': 'missing'}}))
            storybook = public / 'previews/easy-ui/pr-1/storybook'
            storybook.mkdir(parents=True)
            (storybook / 'index.html').write_text('App preview')
            self.assertEqual(previews.available_routes(public), {'/', '/about/', '/404.html'})

    def test_no_rendered_changes_embed_no_images(self):
        section = previews.preview_section({'head_sha': 'a' * 40, 'pages': []}, '', 'https://ci.invalid')
        self.assertIn('No rendered page changes detected.', section)
        self.assertNotIn('<img ', section)

    def test_unlisted_essay_has_pr_previews_without_public_discovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            public = Path(temporary)
            (public / 'build.json').write_text(json.dumps({'files': {'/index.html': 'home'}}))
            article = public / 'writing/review-copy/index.html'
            article.parent.mkdir(parents=True)
            article.write_text('<meta name="site-revision" content="test">'
                               '<article class="sc-article" data-visibility="unlisted"></article>')
            self.assertEqual(previews.available_routes(public), {'/', '/writing/review-copy/'})
            self.assertNotIn('review-copy', (public / 'build.json').read_text())


if __name__ == '__main__':
    unittest.main()
