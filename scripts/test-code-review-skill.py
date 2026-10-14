#!/usr/bin/env python3
"""Check skill generation and the documented installer without network access."""

import hashlib
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "code_review_skill", ROOT / "scripts/code-review-skill.py"
)
assert spec is not None and spec.loader is not None
skill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skill)


class GenerationTests(unittest.TestCase):
    def test_output_matches_guide_and_adapter(self):
        source = skill.SOURCE.read_text(encoding="utf-8")
        adapter = skill.ADAPTER.read_text(encoding="utf-8")
        expected = skill.render(source, adapter)
        self.assertEqual(skill.OUTPUT.read_bytes(), expected.encode("utf-8"))
        guidance = source.split(skill.BEGIN)[1].split(skill.END)[0].strip()
        self.assertIn(guidance, expected)
        digest = hashlib.sha256(guidance.encode("utf-8")).hexdigest()
        self.assertIn(f'guidance-sha256: "{digest}"', expected)
        self.assertNotIn("{{GUIDANCE", expected)
        self.assertNotIn("simpler than necessary", expected)

    def test_invalid_markers_fail(self):
        adapter = "{{GUIDANCE_SHA256}}\n{{GUIDANCE}}"
        for source in (
            "no markers", skill.BEGIN + "text", "text" + skill.END,
            skill.END + "text" + skill.BEGIN,
            skill.BEGIN + " " + skill.END,
            skill.BEGIN + skill.BEGIN + "text" + skill.END,
            skill.BEGIN + "text" + skill.END + skill.END,
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                skill.render(source, adapter)

    def test_invalid_adapter_fails(self):
        source = skill.BEGIN + "Guidance" + skill.END
        for adapter in (
            "", "{{GUIDANCE}}", "{{GUIDANCE_SHA256}}",
            "{{GUIDANCE}} {{GUIDANCE}} {{GUIDANCE_SHA256}}",
            "{{GUIDANCE}} {{GUIDANCE_SHA256}} {{GUIDANCE_SHA256}}",
        ):
            with self.subTest(adapter=adapter), self.assertRaises(ValueError):
                skill.render(source, adapter)

    def test_missing_or_changed_published_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "SKILL.md"
            with self.assertRaises(ValueError):
                skill.check_file(target, b"expected\n")
            target.write_bytes(b"stale\n")
            with self.assertRaises(ValueError):
                skill.check_file(target, b"expected\n")
            target.write_bytes(b"expected\n")
            skill.check_file(target, b"expected\n")

    def test_check_does_not_rewrite_output(self):
        before = skill.OUTPUT.stat().st_mtime_ns
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/code-review-skill.py"), "--check"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(skill.OUTPUT.stat().st_mtime_ns, before)

    def test_standalone_format_and_references(self):
        text = skill.OUTPUT.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: code-review\n"))
        frontmatter = text.split("---\n", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^description: .+")
        self.assertLessEqual(len(text.splitlines()), 500)
        references = set(re.findall(r"\[\^([^\]]+)\](?!:)", text))
        definitions = re.findall(r"(?m)^\[\^([^\]]+)\]:", text)
        self.assertEqual(references, set(definitions))
        self.assertEqual(len(definitions), len(set(definitions)))
        self.assertNotIn("/install-the-agent-skill", text)


class InstallTests(unittest.TestCase):
    def test_documented_command_preserves_existing_skill_on_failure(self):
        source = skill.SOURCE.read_text(encoding="utf-8")
        commands = re.findall(r"```sh\n(.*?)\n```", source, re.DOTALL)
        self.assertEqual(len(commands), 1)
        command = commands[0]
        # Exercise the actual documented shell command. Stub only the network.
        for fail, existing in ((False, False), (False, True), (True, False), (True, True)):
            with self.subTest(fail=fail, existing=existing):
                with tempfile.TemporaryDirectory(prefix="review install ") as tmp:
                    home = Path(tmp) / "home with spaces"
                    bindir = Path(tmp) / "bin"
                    bindir.mkdir()
                    curl = bindir / "curl"
                    curl.write_text(
                        f"#!{sys.executable}\n"
                        "import os, pathlib, sys\n"
                        "assert 'https://lanej.io/skills/code-review/SKILL.md' in sys.argv\n"
                        "target = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])\n"
                        "fail = os.environ['FAIL_DOWNLOAD'] == '1'\n"
                        "data = b'partial download' if fail else pathlib.Path(os.environ['SKILL_FIXTURE']).read_bytes()\n"
                        "target.write_bytes(data)\n"
                        "sys.exit(22 if fail else 0)\n",
                        encoding="utf-8",
                    )
                    curl.chmod(0o755)
                    target = home / ".claude/skills/code-review/SKILL.md"
                    if existing:
                        target.parent.mkdir(parents=True)
                        target.write_bytes(b"previous installed skill\n")
                    env = dict(os.environ, HOME=str(home),
                               PATH=f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}",
                               FAIL_DOWNLOAD="1" if fail else "0",
                               SKILL_FIXTURE=str(skill.OUTPUT))
                    result = subprocess.run(
                        ["bash", "-c", command], env=env, capture_output=True,
                        text=True, check=False,
                    )
                    if fail:
                        self.assertNotEqual(result.returncode, 0)
                        if existing:
                            self.assertEqual(target.read_bytes(), b"previous installed skill\n")
                        else:
                            self.assertFalse(target.exists())
                    else:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(target.read_bytes(), skill.OUTPUT.read_bytes())
                    self.assertEqual(list(target.parent.glob(".SKILL.md.*")), [])


if __name__ == "__main__":
    unittest.main()
