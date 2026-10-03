"""Keep article PR previews relevant without weakening shared visual checks."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from affected_pages import affected_routes, is_draft

spec = importlib.util.spec_from_file_location('pr_previews', Path(__file__).with_name('pr-previews.py'))
previews = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previews)


class DraftSelectionTests(unittest.TestCase):
    routes = {'/', '/writing/', '/writing/existing/', '/about/', '/record/', '/open-source/', '/404.html'}
    source = 'content/writing/new-essay/index.md'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.write('README.md', 'baseline')
        self.base = self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, text=True,
                                       stderr=subprocess.DEVNULL).strip()

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'user.name=Preview Test', '-c', 'user.email=preview@example.invalid',
                 'commit', '-qm', 'fixture')
        return self.git('rev-parse', 'HEAD')

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def article(self, draft, body='Essay.'):
        self.write(self.source, f'+++\ntitle = "Essay"\ndraft = {str(draft).lower()}\n+++\n\n{body}\n')

    def select(self, paths=None, routes=None):
        return affected_routes(paths if paths is not None else [self.source],
                               self.routes if routes is None else routes,
                               root=self.root, base=self.base)

    def test_new_draft_does_not_select_the_whole_site_or_indexes(self):
        self.article(True)
        self.assertEqual(self.select(), [])

    def test_existing_draft_edit_does_not_select_production(self):
        self.article(True)
        self.base = self.commit()
        self.article(True, 'Revised prose.')
        self.assertEqual(self.select(), [])

    def test_deleted_draft_does_not_select_production(self):
        self.article(True)
        self.base = self.commit()
        (self.root / self.source).unlink()
        self.assertEqual(self.select(), [])

    def test_draft_assets_do_not_select_existing_essays(self):
        self.article(True)
        self.base = self.commit()
        asset = 'content/writing/new-essay/figure.svg'
        self.write(asset, '<svg/>')
        self.assertEqual(self.select([asset]), [])

    def test_publishing_a_draft_selects_article_and_discovery(self):
        self.article(True)
        self.base = self.commit()
        self.article(False)
        self.assertEqual(self.select(routes=self.routes | {'/writing/new-essay/'}),
                         ['/', '/writing/', '/writing/new-essay/'])

    def test_withdrawing_published_article_keeps_discovery_coverage(self):
        self.article(False)
        self.base = self.commit()
        self.article(True)
        self.assertEqual(self.select(), ['/', '/writing/'])

    def test_deleted_published_article_keeps_discovery_coverage(self):
        self.article(False)
        self.base = self.commit()
        (self.root / self.source).unlink()
        self.assertEqual(self.select(), ['/', '/writing/'])

    def test_new_published_article_does_not_select_unrelated_pages(self):
        self.article(False)
        self.assertEqual(self.select(routes=self.routes | {'/writing/new-essay/'}),
                         ['/', '/writing/', '/writing/new-essay/'])

    def test_unknown_non_draft_route_remains_conservative(self):
        self.article(False)
        self.assertEqual(self.select(), sorted(self.routes))

    def test_malformed_draft_metadata_does_not_suppress_coverage(self):
        self.write(self.source, '+++\ndraft = true\nbroken = [\n+++\n')
        self.assertEqual(self.select(), sorted(self.routes))
        for text in ('draft = true', '+++\ndraft = true', '+++\ndraft = "true"\n+++\n'):
            self.assertFalse(is_draft(text))

    def test_shared_header_still_selects_every_page_in_a_draft_pr(self):
        self.article(True)
        self.assertEqual(self.select([self.source, 'layouts/partials/header.html']),
                         sorted(self.routes))

    def test_shared_essay_styles_still_select_all_essays(self):
        self.article(True)
        routes = self.routes | {'/writing/another/'}
        self.assertEqual(self.select([self.source, 'assets/css/essays.css'], routes),
                         ['/writing/another/', '/writing/existing/'])

    def test_explicit_draft_preview_build_can_still_check_rendered_draft(self):
        self.article(True)
        self.assertEqual(self.select(routes=self.routes | {'/writing/new-essay/'}),
                         ['/', '/writing/', '/writing/new-essay/'])

    def test_docs_and_tooling_do_not_require_screenshots(self):
        self.assertEqual(self.select(['AGENTS.md', 'docs/development.md',
                                      'scripts/pr-previews.py', '.github/workflows/pages.yml']), [])


class EmptyPreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'previews'
        self.output.mkdir()
        self.manifest = {'head_sha': 'head', 'build_sha': 'build', 'pages': []}
        (self.output / 'manifest.json').write_text(json.dumps(self.manifest))
        self.env = {'PR_HEAD_SHA': 'head', 'GITHUB_SHA': 'build',
                    'GITHUB_REPOSITORY': 'owner/site', 'GITHUB_RUN_ID': '123',
                    'GITHUB_EVENT_PATH': str(self.root / 'event.json'), 'GH_TOKEN': 'test-token'}
        event = {'pull_request': {'number': 76, 'head': {'sha': 'head',
                                                       'repo': {'full_name': 'owner/site'}}}}
        (self.root / 'event.json').write_text(json.dumps(event))

    def test_empty_capture_needs_no_browser_and_removes_old_images(self):
        selection = self.root / 'selection.json'
        selection.write_text(json.dumps({'routes': []}))
        (self.output / 'stale.png').write_bytes(b'old screenshot')
        args = SimpleNamespace(selection=str(selection), base=None,
                               output=str(self.output), chromium_path='not-installed')
        with patch.dict(os.environ, self.env), patch.dict('sys.modules', {'playwright.sync_api': None}):
            previews.capture(args)
        self.assertEqual(json.loads((self.output / 'manifest.json').read_text()), self.manifest)
        self.assertEqual(list(self.output.glob('*.png')), [])

    def publish(self, current):
        requests = []

        def respond(request):
            requests.append(request)
            self.assertTrue(request.full_url.endswith('/pulls/76'),
                            'Empty selection must not create blobs, trees, commits, or refs.')
            return io.BytesIO(json.dumps(current).encode())

        with patch.dict(os.environ, self.env), patch.object(previews, 'urlopen', side_effect=respond):
            previews.publish(SimpleNamespace(output=str(self.output)))
        return requests

    def test_empty_publish_replaces_stale_block_without_creating_preview_commit(self):
        body = f'Human text\n\n{previews.START}\n<img src="old">\n{previews.END}\n\nChecklist'
        requests = self.publish({'head': {'sha': 'head'}, 'state': 'open', 'body': body})
        self.assertEqual([r.get_method() for r in requests], ['GET', 'PATCH'])
        updated = json.loads(requests[-1].data)['body']
        self.assertIn('Human text', updated)
        self.assertIn('Checklist', updated)
        self.assertNotIn('<img', updated)
        self.assertIn('No rendered page changes detected.', updated)
        self.assertEqual(updated.count(previews.START), 1)
        self.assertEqual(updated.count(previews.END), 1)

    def test_empty_publish_is_idempotent(self):
        section = previews.preview_section(self.manifest, '', 'https://github.com/owner/site/actions/runs/123')
        body = previews.replace_section('Human text', section)
        requests = self.publish({'head': {'sha': 'head'}, 'state': 'open', 'body': body})
        self.assertEqual([r.get_method() for r in requests], ['GET'])

    def test_stale_revision_and_closed_pr_do_not_clear_newer_evidence(self):
        for sha, state in [('newer-head', 'open'), ('head', 'closed')]:
            with self.subTest(sha=sha, state=state):
                requests = self.publish({'head': {'sha': sha}, 'state': state, 'body': 'Keep this'})
                self.assertEqual([r.get_method() for r in requests], ['GET'])

    def test_full_preview_format_remains_available_for_meaningful_changes(self):
        manifest = dict(self.manifest, pages=[{'route': '/about/', 'title': 'About', 'images': {
            'mobile': {'viewport': 'about-mobile.png', 'full': 'about-mobile-full.png'},
            'desktop': {'viewport': 'about-desktop.png', 'full': 'about-desktop-full.png'},
        }}])
        section = previews.preview_section(manifest, 'https://example.invalid/images', 'https://example.invalid/run')
        self.assertEqual(section.count('<img'), 2)
        self.assertIn('/about/', section)


if __name__ == '__main__':
    unittest.main()
