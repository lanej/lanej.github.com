"""Regression coverage for page selection, not another geometry detector."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from affected_pages import (PageAnchors, affected_routes, change_base, changed_paths,
                            css_routes, rule_routes)

spec = importlib.util.spec_from_file_location('viewrule_wrapper', Path(__file__).with_name('viewrule.py'))
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)


class SelectionTests(unittest.TestCase):
    routes = {'/', '/labs/', '/writing/', '/writing/example/', '/about/', '/record/', '/open-source/', '/404.html'}
    documents = {
        '/': PageAnchors('<main class="home-writing"><article class="writing-item"></article></main>'),
        '/writing/': PageAnchors('<div class="writing-index writing-grid"><article class="writing-item"></article></div>'),
        '/about/': PageAnchors('<main class="prose" id="biography"></main>'),
    }

    def test_page_specific_templates(self):
        self.assertEqual(affected_routes(['layouts/home.html'], self.routes), ['/'])
        self.assertEqual(affected_routes(['layouts/writing/list.html'], self.routes), ['/writing/'])
        self.assertEqual(affected_routes(['layouts/labs.html'], self.routes), ['/labs/'])

    def test_labs_content_updates_home_teasers(self):
        self.assertEqual(affected_routes(['content/labs.md'], self.routes), ['/', '/labs/'])
        self.assertEqual(affected_routes(['content/labs/_index.md'], self.routes), ['/', '/labs/'])

    def test_article_change_and_deletion_keep_indexes(self):
        self.assertEqual(affected_routes(['content/writing/example/index.md'], self.routes), ['/', '/writing/', '/writing/example/'])
        self.assertEqual(affected_routes(['content/writing/deleted/index.md'], self.routes), ['/', '/writing/'])

    def test_unknown_shared_template_includes_404(self):
        self.assertEqual(affected_routes(['layouts/partials/header.html'], self.routes), sorted(self.routes))
        self.assertEqual(affected_routes(['layouts/new-shared.html'], self.routes), sorted(self.routes))

    def test_tooling_and_docs_do_not_render(self):
        self.assertEqual(affected_routes(['README.md', 'STYLE.md', '.github/workflows/pages.yml',
                                         '.ui-review/.gitignore', 'scripts/viewrule.py'], self.routes), [])

    def test_css_small_edit_in_shared_file(self):
        old = '.prose{color:green}.writing-index{max-width:680px}.other{color:red}'
        new = '.prose{color:green}.writing-index{min-width:0}.writing-grid{display:grid}.other{color:red}'
        self.assertEqual(css_routes(old, new, self.documents), {'/writing/'})

    def test_css_common_class_includes_every_consumer(self):
        self.assertEqual(css_routes('.writing-item{color:red}', '.writing-item{color:blue}', self.documents), {'/', '/writing/'})

    def test_css_media_change_keeps_selector_scope(self):
        self.assertEqual(css_routes('@media(min-width:800px){.writing-grid{display:grid}}',
                                    '@media(min-width:900px){.writing-grid{display:grid}}', self.documents), {'/writing/'})

    def test_css_removed_rule(self):
        self.assertEqual(css_routes('.writing-grid{display:grid}', '', self.documents), {'/writing/'})

    def test_css_reordering_changes_cascade(self):
        self.assertTrue(css_routes('.writing-item{color:red}.writing-index{color:blue}',
                                   '.writing-index{color:blue}.writing-item{color:red}', self.documents))

    def test_css_comments_only(self):
        self.assertEqual(css_routes('/* old */.writing-grid{display:grid}',
                                    '/* new */.writing-grid{display:grid}', self.documents), set())

    def test_global_css_and_unanchored_alternatives_are_conservative(self):
        for selector in (':root', 'body', ':not(.writing-grid)', '.writing-grid, h1', ':is(.writing-grid,h1)'):
            with self.subTest(selector=selector):
                self.assertEqual(css_routes('', selector + '{color:red}', self.documents), set(self.documents))

    def test_css_dynamic_pseudo_and_id_scope(self):
        self.assertEqual(css_routes('', '.writing-grid:hover::before{color:red}', self.documents), {'/writing/'})
        self.assertEqual(css_routes('', '#biography{color:red}', self.documents), {'/about/'})

    def test_css_runtime_class_and_at_rules_fall_back_to_full(self):
        for css in ('.runtime-only{display:block}', '@font-face{font-family:demo;src:url(a.woff)}', '@import "other.css";'):
            with self.subTest(css=css):
                self.assertEqual(css_routes('', css, self.documents), set(self.documents))

    def test_rule_scope_addition_change_and_removal(self):
        names = {'home':'/', 'home-enlarged':'/', 'writing':'/writing/'}
        old = [{'id':'x','pages':['home'],'min':1}]
        new = [{'id':'x','pages':['writing'],'min':2}]
        self.assertEqual(rule_routes(json.dumps(old), json.dumps(new), names), {'/', '/writing/'})
        self.assertEqual(rule_routes('', json.dumps(old), names), {'/'})
        self.assertEqual(rule_routes(json.dumps(old), '[]', names), {'/'})

    def test_global_rule_change_selects_all(self):
        self.assertEqual(rule_routes('[]', '[{"id":"global"}]', {'home':'/', 'writing':'/writing/'}), {'/', '/writing/'})

    def test_filtered_rules_preserve_original_and_scope(self):
        rules = [{'id':'global'}, {'id':'home', 'pages':['home','home-enlarged']},
                 {'id':'archive','pages':['writing']}]
        original = copy.deepcopy(rules)
        result = wrapper.scoped_rules(rules, [{'name':'home-enlarged'}])
        self.assertEqual(result, [{'id':'global'}, {'id':'home','pages':['home-enlarged']}])
        self.assertEqual(rules, original)


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.write('README.md', 'initial')
        self.write('assets/css/editorial.css', '.writing-index{color:red}')
        self.write('.ui-review/site.json', json.dumps({'sourcePaths':['assets'], 'viewports':[{'name':'desktop'}]}))
        self.git('add', '.')
        self.commit('baseline')
        self.base = self.git('rev-parse', 'HEAD')
        self.git('update-ref', 'refs/remotes/origin/master', self.base)

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, text=True, stderr=subprocess.DEVNULL).strip()

    def commit(self, message):
        self.git('-c', 'user.name=Selection Test', '-c', 'user.email=selection@example.invalid', 'commit', '-qm', message)

    def write(self, path, text):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def test_branch_diff_includes_all_commits_staged_and_unstaged(self):
        self.write('content/labs.md', 'labs')
        self.git('add', '.')
        self.commit('first')
        self.write('layouts/home.html', 'home')
        self.git('add', '.')
        self.commit('second')
        self.write('content/about.md', 'about')
        self.git('add', '.')
        self.write('assets/css/editorial.css', '.writing-index{color:blue}')
        self.write('content/new.md', 'untracked')
        self.assertEqual(change_base(self.root), self.base)
        self.assertEqual(set(changed_paths(self.root, self.base)), {
            'content/labs.md','layouts/home.html','content/about.md','assets/css/editorial.css','content/new.md'})

    def test_rename_detects_deleted_and_new_content_paths(self):
        self.write('content/writing/old.md', 'essay')
        self.git('add', '.')
        self.commit('old route')
        base = self.git('rev-parse', 'HEAD')
        self.git('mv', 'content/writing/old.md', 'content/writing/new.md')
        self.assertEqual(set(changed_paths(self.root, base)), {'content/writing/old.md','content/writing/new.md'})

    def test_bad_baseline_fails_instead_of_skipping(self):
        with self.assertRaises(subprocess.CalledProcessError):
            change_base(self.root, 'missing-ref')

    def config(self):
        return {'sourcePaths':['assets', '.ui-review/rules.json'],
                'viewports':[{'name':'mobile'},{'name':'desktop'}],
                'pages':[{'name':'home','path':'/'},{'name':'home-enlarged','path':'/','viewports':['desktop']},
                         {'name':'writing','path':'/writing/'}]}

    def test_scope_keeps_every_state_for_selected_route(self):
        self.write('layouts/home.html', 'changed')
        pages, selection = wrapper.scope(self.config(), base=self.base, root=self.root)
        self.assertEqual([p['name'] for p in pages], ['home','home-enlarged'])
        self.assertEqual(selection['viewport_states'], 3)

    def test_docs_only_skips_and_full_or_initial_push_keeps_all(self):
        self.write('README.md', 'updated')
        pages, result = wrapper.scope(self.config(), base=self.base, root=self.root)
        self.assertEqual(pages, [])
        self.assertEqual(result['status'], 'no-visual-changes')
        for options in ({'full':True}, {'base':'0'*40}):
            pages, result = wrapper.scope(self.config(), root=self.root, **options)
            self.assertEqual(len(pages), 3)
            self.assertEqual(result['mode'], 'full')

    def test_source_path_metadata_change_does_not_force_full(self):
        self.write('.ui-review/site.json', json.dumps({'sourcePaths':['assets','scripts/affected_pages.py'], 'viewports':[{'name':'desktop'}]}))
        self.assertEqual(affected_routes(['.ui-review/site.json'], {'/','/writing/'}, root=self.root, base=self.base), [])
        self.write('.ui-review/site.json', json.dumps({'viewports':[{'name':'mobile'}]}))
        self.assertEqual(affected_routes(['.ui-review/site.json'], {'/','/writing/'}, root=self.root, base=self.base), ['/','/writing/'])

    def test_snapshot_does_not_rewrite_canonical_rules_and_removes_stale_source(self):
        rules = [{'id':'home','pages':['home','home-enlarged']},{'id':'writing','pages':['writing']}]
        self.write('.ui-review/rules.json', json.dumps(rules))
        self.write('assets/removed.css', 'old')
        config = self.config()
        project = wrapper.prepare_scoped_project(config, config['pages'][:2], self.root)
        self.assertEqual(json.loads((self.root/'.ui-review/rules.json').read_text()), rules)
        self.assertEqual(json.loads((project/'.ui-review/rules.json').read_text()), rules[:1])
        (self.root/'assets/removed.css').unlink()
        wrapper.prepare_scoped_project(config, config['pages'][:2], self.root)
        self.assertFalse((project/'assets/removed.css').exists())


if __name__ == '__main__':
    unittest.main()
