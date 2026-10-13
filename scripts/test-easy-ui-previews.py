"""Guard trusted PR selection, SHA pinning, build order, and distinct URL paths."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import HTTPRedirectHandler

spec = importlib.util.spec_from_file_location('previews', Path(__file__).with_name('easy-ui-previews.py'))
previews = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previews)
SHA_A = 'a' * 40
SHA_B = 'b' * 40


def pr(number, sha=SHA_A, repository='lanej/easy-ui'):
    return {'number': number, 'head': {'repo': {'full_name': repository}, 'sha': sha}}


class PreviewTests(unittest.TestCase):
    def setUp(self):
        # Selection fixtures must not change when another real PR is preserved.
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / 'data').mkdir()
        self.preserved = root / 'data/easy-ui-previews.json'
        self.preserved.write_text(json.dumps([24, 29]))
        root_patch = patch.object(previews, 'ROOT', root)
        root_patch.start()
        self.addCleanup(root_patch.stop)

    def test_api_token_is_not_sent_to_public_sites_or_redirects(self):
        with patch.dict(previews.os.environ, {'GH_TOKEN': 'test-read-only-token'}, clear=True), patch.object(previews, 'urlopen') as fetch:
            for url in ['https://api.github.com/repos/lanej/easy-ui/pulls',
                        'https://lanej.io/previews/easy-ui/pr-38/revision.txt',
                        'https://api.github.com.example.test/pulls']:
                previews.read(url)
                request = fetch.call_args.args[0]
                expected = 'Bearer test-read-only-token' if url.startswith('https://api.github.com/') else None
                self.assertEqual(request.get_header('Authorization'), expected)
                redirected = HTTPRedirectHandler().redirect_request(
                    request, None, 302, '', {}, 'https://example.test/redirect')
                self.assertIsNone(redirected.get_header('Authorization'))

    def test_github_token_fallback_and_unauthenticated_local_reads(self):
        with patch.object(previews, 'urlopen') as fetch:
            for environment, expected in [({'GITHUB_TOKEN': 'test-fallback'}, 'Bearer test-fallback'), ({}, None)]:
                with patch.dict(previews.os.environ, environment, clear=True):
                    previews.read('https://api.github.com/repos/lanej/easy-ui/pulls')
                    self.assertEqual(fetch.call_args.args[0].get_header('Authorization'), expected)

    def test_trusted_head(self):
        self.assertEqual(previews.trusted_head(pr(29)), (29, SHA_A))

    def test_rejects_fork_before_executing_code(self):
        with self.assertRaisesRegex(AssertionError, 'Unexpected fork'):
            previews.trusted_head(pr(29, repository='other/easy-ui'))

    def test_rejects_invalid_identifiers(self):
        for value in [pr('../29'), pr(29, sha='main'), pr(29, sha='a' * 39)]:
            with self.assertRaises(AssertionError):
                previews.trusted_head(value)

    def test_open_owned_prs_and_preserved_closed_prs(self):
        def read(url):
            values = [pr(29, SHA_B), pr(30, repository='other/easy-ui')] if 'state=open' in url else pr(24)
            return json.dumps(values).encode()
        with patch.object(previews, 'read', side_effect=read):
            self.assertEqual(previews.preview_heads(), [(24, SHA_A), (29, SHA_B)])

    def test_additional_preserved_pr_is_fetched_by_number(self):
        self.preserved.write_text(json.dumps([24, 29, 31]))
        def read(url):
            values = [pr(29, SHA_B)] if 'state=open' in url else pr(int(url.rsplit('/', 1)[-1]))
            return json.dumps(values).encode()
        with patch.object(previews, 'read', side_effect=read) as fetch:
            self.assertEqual(previews.preview_heads(), [(24, SHA_A), (29, SHA_B), (31, SHA_A)])
        self.assertEqual(fetch.call_count, 3)

    def test_follows_pagination(self):
        def read(url):
            values = [pr(number) for number in range(1, 101)] if 'page=1' in url.split('per_page=100&')[-1] else [pr(101)]
            return json.dumps(values).encode()
        with patch.object(previews, 'read', side_effect=read):
            self.assertEqual(len(previews.preview_heads()), 101)

    def test_build_pins_each_head_and_emits_separate_paths(self):
        commands = []
        def run(command, **kwargs):
            commands.append(command)
            self.assertNotIn('GH_TOKEN', kwargs['env'])
            self.assertNotIn('GITHUB_TOKEN', kwargs['env'])
            if command[:2] == ['git', 'clone']:
                Path(command[-1]).mkdir()
            if command[:3] == ['npm', 'run', 'build:storybook']:
                storybook = Path(command[-1])
                storybook.mkdir(parents=True)
                for name in ['index.html', 'iframe.html', 'index.json']:
                    (storybook / name).write_text(name)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.dict(previews.os.environ, {'GH_TOKEN': 'test-read-only-token', 'GITHUB_TOKEN': 'test-fallback'}), patch.object(previews, 'preview_heads', return_value=[(24, SHA_A), (29, SHA_B)]), patch.object(previews.subprocess, 'run', side_effect=run):
                previews.build(root)
            records = json.loads((root / 'previews/easy-ui/manifest.json').read_text())['previews']
            self.assertEqual([record['path'] for record in records], ['previews/easy-ui/pr-24/', 'previews/easy-ui/pr-29/'])
            for number, sha in [(24, SHA_A), (29, SHA_B)]:
                self.assertEqual((root / f'previews/easy-ui/pr-{number}/revision.txt').read_text().strip(), sha)
            checkouts = [command[-1] for command in commands if 'checkout' in command]
            self.assertEqual(checkouts, [SHA_A, SHA_B])
            builds = [command[2] for command in commands if command[:2] == ['npm', 'run']]
            self.assertEqual(builds, ['build', 'build:storybook', 'build', 'build:storybook'])


if __name__ == '__main__':
    unittest.main()
