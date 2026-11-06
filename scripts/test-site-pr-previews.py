"""Hosted-preview regression checks, including the real pinned Hugo renderer."""
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.request import HTTPRedirectHandler
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location('site_previews', Path(__file__).with_name('site-pr-previews.py'))
previews = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previews)
SHA = 'a' * 40


class HostedPreviewTests(unittest.TestCase):
    def test_trust_boundary_excludes_forks_and_invalid_identifiers(self):
        pr = {'number':87,'head':{'repo':{'full_name':previews.REPOSITORY},'sha':SHA}}
        self.assertEqual(previews.trusted(pr), (87, SHA))
        for changed in [dict(pr,number='../87'), dict(pr,head={'repo':None,'sha':SHA}),
                        dict(pr,head={'repo':{'full_name':'other/site'},'sha':SHA}),
                        dict(pr,head={'repo':{'full_name':previews.REPOSITORY},'sha':'master'})]:
            with self.assertRaises(AssertionError): previews.trusted(changed)

    def test_only_explicit_refreshes_or_nonrendering_infrastructure_take_fast_path(self):
        self.assertTrue(previews.fast_refresh({'inputs':{'preview_refresh':True}}, []))
        self.assertTrue(previews.fast_refresh({}, ['scripts/site-pr-previews.py','AGENTS.md']))
        self.assertFalse(previews.fast_refresh({}, []))
        for path in ['content/about.md','layouts/baseof.html','assets/css/site.css','data/work.yaml']:
            self.assertFalse(previews.fast_refresh({}, ['AGENTS.md', path]))

    def test_renderer_has_no_actions_or_github_credentials(self):
        with patch.dict(os.environ, {'PATH':'/bin','HOME':'/home/runner','GH_TOKEN':'secret',
                        'GITHUB_TOKEN':'secret','ACTIONS_RUNTIME_TOKEN':'secret',
                        'ACTIONS_ID_TOKEN_REQUEST_TOKEN':'secret','UNRELATED_SECRET':'secret'}, clear=True):
            env = previews.build_environment(SHA)
        self.assertEqual(env['PATH'], '/bin')
        self.assertEqual(env['HUGO_PARAMS_REVISION'], SHA)
        self.assertEqual(env['HUGO_RELATIVEURLS'], 'true')
        self.assertNotIn('secret', env.values())

    def test_fork_cannot_select_the_cached_bundle_job(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'event.json'
            path.write_text(json.dumps({'pull_request':{'head':{'repo':{'full_name':'other/site'}}}}))
            with patch.dict(os.environ,{'GITHUB_EVENT_PATH':str(path),'GITHUB_EVENT_NAME':'pull_request'}), \
                    patch.object(previews,'production_artifact') as artifact, patch('sys.stdout',new_callable=io.StringIO) as output:
                previews.mode()
                self.assertIn('preview_refresh=false',output.getvalue())
                artifact.assert_not_called()

    def test_github_credentials_do_not_reach_site_reads_or_redirects(self):
        with patch.dict(os.environ, {'GH_TOKEN':'fixture-token'}, clear=True), patch.object(previews,'urlopen') as fetch:
            for url in ['https://api.github.com/repos/lanej/lanej.github.com/pulls',
                        'https://lanej.io/build.json','https://api.github.com.example.test/pulls']:
                previews.read(url)
                request = fetch.call_args.args[0]
                auth = request.get_header('Authorization')
                self.assertEqual(auth, 'Bearer fixture-token' if urlsplit_host(url)=='api.github.com' else None)
                redirected = HTTPRedirectHandler().redirect_request(request,None,302,'',{},'https://example.test/')
                self.assertIsNone(redirected.get_header('Authorization'))

    def test_description_links_the_affected_page_and_preserves_other_markers(self):
        record = {'number':87,'sha':SHA,'prefix':'/previews/site/pr-87/','entry':'/writing/architecture/'}
        screenshots = '<!-- page-previews:start -->\nScreenshots\n<!-- page-previews:end -->'
        body = '[Open PR #87 on GitHub](https://github.com/lanej/lanej.github.com/pull/87)\n\nHuman text\n'+screenshots
        updated = previews.preview_section(body, record)
        self.assertIn('[Preview this PR](https://lanej.io/previews/site/pr-87/writing/architecture/)', updated)
        self.assertNotIn('[Open PR #87', updated)
        self.assertIn('Human text\n'+screenshots, updated)
        self.assertEqual(previews.preview_section(updated, record), updated)

    def test_entry_prefers_a_rendered_changed_essay(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            for path in ['index.html','about/index.html','writing/architecture/index.html']:
                file=root/path;file.parent.mkdir(parents=True,exist_ok=True);file.write_text('page')
            files=[{'filename':'content/about.md'},{'filename':'content/writing/architecture/index.md'}]
            self.assertEqual(previews.entry_route(files,root), '/writing/architecture/')
            self.assertEqual(previews.entry_route([{'filename':'content/missing.md'}],root), '/')

    def test_restoration_rejects_archive_traversal_and_wrong_production_revision(self):
        for path in ['../escape','/absolute']:
            data=io.BytesIO()
            with ZipFile(data,'w') as archive: archive.writestr(path,'unsafe')
            with tempfile.TemporaryDirectory() as temporary, patch.object(previews,'read',side_effect=[b'{}',data.getvalue()]):
                with self.assertRaises(AssertionError): previews.restore(Path(temporary)/'public',123)
        data=io.BytesIO()
        with ZipFile(data,'w') as archive: archive.writestr('build.json',json.dumps({'revision':'old','files':{}}))
        with tempfile.TemporaryDirectory() as temporary, patch.object(previews,'read',side_effect=[b'{"revision":"new","files":{}}',data.getvalue()]):
            with self.assertRaisesRegex(AssertionError,'currently published'):
                previews.restore(Path(temporary)/'public',123)

    def test_pinned_hugo_emits_portable_navigation_and_noindex(self):
        hugo=Path(os.getenv('HUGO_BIN',str(previews.ROOT/'.tools/hugo'))).resolve()
        self.assertTrue(hugo.is_file(),'Install the pinned Hugo before running this test')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';output=root/'public/previews/site/pr-87'
            (source/'layouts').mkdir(parents=True);(source/'content/writing/example').mkdir(parents=True)
            (source/'static/css').mkdir(parents=True)
            (source/'hugo.toml').write_text("baseURL='https://lanej.io/'\ndisableKinds=['taxonomy','term']\n")
            (source/'layouts/single.html').write_text('<!doctype html><html><head><link rel="stylesheet" href="/css/test.css"></head><body><h1>{{ .Title }}</h1><a href="/">Home</a></body></html>')
            for name in ('home.html','list.html'):
                (source/'layouts'/name).write_text('<html><head></head><body>Preview index</body></html>')
            (source/'content/writing/example/index.md').write_text('+++\ntitle="Preview example"\ndraft=true\n+++\nA draft.')
            (source/'static/css/test.css').write_text('body{color:green}')
            previews.render(source,output,SHA,str(hugo))
            page=(output/'writing/example/index.html').read_text()
            self.assertIn('../../css/test.css',page)
            self.assertIn('href=../../',page)
            self.assertIn('noindex, nofollow',page)
            self.assertIn(SHA,page)


def urlsplit_host(url):
    from urllib.parse import urlsplit
    return urlsplit(url).netloc


if __name__ == '__main__': unittest.main()
