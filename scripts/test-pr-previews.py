"""Check preview scope and preservation of human-authored PR text."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('previews', Path(__file__).with_name('pr-previews.py'))
previews = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previews)


class PreviewTests(unittest.TestCase):
    routes = {'/', '/record/', '/about/', '/writing/', '/writing/example/'}

    def test_company_icons_affect_work(self):
        self.assertEqual(previews.affected_routes(
            ['assets/css/work.css', 'static/logos/companies/easypost.svg', 'STYLE.md'], self.routes), ['/record/'])

    def test_shared_template_affects_every_page(self):
        self.assertEqual(previews.affected_routes(['layouts/partials/header.html'], self.routes), sorted(self.routes))

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


if __name__ == '__main__':
    unittest.main()
