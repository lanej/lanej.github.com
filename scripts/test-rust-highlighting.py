"""Exercise Rust roles, exact source preservation, escaping, and cache freshness."""
import contextlib
import hashlib
from html.parser import HTMLParser
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rust_highlighting", ROOT / "scripts/rust-highlighting.py")
rust = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rust)
PALETTE = json.loads((ROOT / "data/syntax/palette.json").read_text())


class Rendered(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.text, self.tokens, self.tags, self.current = "", [], [], None
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.current = dict(attrs).get("class", "").removeprefix("syn syn-")

    def handle_endtag(self, tag):
        self.current = None

    def handle_data(self, text):
        self.text += text
        if self.current:
            self.tokens.append((self.current, text))

    def names(self, kind):
        return {text for role, text in self.tokens if role == kind}


def render(source):
    result = Rendered(rust.highlight(source, PALETTE))
    assert result.text == source
    return result


class HighlightingTests(unittest.TestCase):
    def test_workflow_has_distinct_roles(self):
        snippets = list(rust.rust_blocks((ROOT / "content/writing/pragmatic-hexagonal-architecture/index.md").read_text()))
        result = render(next(source for source in snippets if source.startswith("pub async fn publish_once(")))
        self.assertTrue({"Review", "CurrentPlan", "ReviewPublisher", "Outcome", "Decision"} <= result.names("type"))
        self.assertTrue({"Skip", "Publish", "Skipped", "Attempted"} <= result.names("constructor"))
        self.assertTrue({"publish_once", "decide", "publish"} <= result.names("function"))
        self.assertTrue({"plans", "review", "publisher"} <= result.names("parameter"))
        self.assertTrue({"impl", "async", "await", "match"} <= result.names("keyword"))

    def test_method_calls_win_over_field_capture(self):
        result = render("fn f(review: &Review) { review.text.trim(); }\n")
        self.assertIn("text", result.names("property"))
        self.assertIn("trim", result.names("function"))
        self.assertNotIn("trim", result.names("property"))

    def test_constructor_call_keeps_owner_type_and_variant_separate(self):
        result = render("fn f() { Decision::Skip(reason); }\n")
        self.assertIn("Decision", result.names("type"))
        self.assertIn("Skip", result.names("constructor"))
        self.assertNotIn("Skip", result.names("function"))

    def test_strings_and_comments_cannot_inject_markup(self):
        result = render('fn f() { let text = r#"</code><script>Review::Skip()</script>"#; }\n// GitHubTarget create()\n')
        self.assertEqual(set(result.tags), {"span"})
        self.assertNotIn("GitHubTarget", result.names("type"))
        self.assertNotIn("create", result.names("function"))
        self.assertIn("// GitHubTarget create()", "".join(result.names("comment")))

    def test_unicode_and_incomplete_snippets_preserve_source(self):
        for source in ['fn café(état: &État) { état.message(); }\n', 'fn pending(value: &Review) {\n']:
            with self.subTest(source=source):
                self.assertEqual(render(source).text, source)

    def test_commonmark_fences_handle_examples_quotes_and_lists(self):
        tick = chr(96)
        markdown = (
            tick * 4 + "markdown\n" + tick * 3 + "rust\nignored()\n" + tick * 3 + "\n" + tick * 4 + "\n"
            "> ~~~rust\n> fn quoted() {}\n> ~~~\n\n"
            "- Item\n\n  " + tick * 3 + "rs\n  fn nested() {}\n  " + tick * 3 + "\n"
        )
        self.assertEqual(list(rust.rust_blocks(markdown)), ["fn quoted() {}\n", "fn nested() {}\n"])

    def test_primary_roles_have_distinct_colors(self):
        roles = ("type", "constructor", "function", "parameter", "property", "keyword")
        self.assertEqual(len({PALETTE["tokens"][role] for role in roles}), len(roles))

    def test_cache_normalizes_like_hugo_and_detects_edits(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "content").mkdir()
            (root / "data/syntax").mkdir(parents=True)
            (root / "data/syntax/palette.json").write_text(json.dumps(PALETTE))
            page = root / "content/sample.md"
            fence = chr(96) * 3
            page.write_text(f"{fence}rust\nfn first() {{}}\n\n{fence}\n")
            args = ["rust-highlighting.py", "--root", str(root)]
            with patch("sys.argv", args + ["--write"]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(rust.main(), 0)
            cached = (root / "data/syntax/rust.json").read_bytes()
            digest = hashlib.sha256(b"fn first() {}").hexdigest()
            self.assertEqual(set(json.loads(cached)["snippets"]), {digest})
            page.write_text(f"{fence}rust\nfn second() {{}}\n{fence}\n")
            with patch("sys.argv", args + ["--check"]), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(rust.main(), 1)
            self.assertEqual((root / "data/syntax/rust.json").read_bytes(), cached)


if __name__ == "__main__":
    unittest.main()
