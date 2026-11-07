"""Generate static Rust highlighting from the grammar shipped with Tree-sitter.

The checked-in cache lets Hugo-only PR previews render the same token roles as
the normal build. No parser or highlighting JavaScript is sent to the browser.
"""
import argparse
from collections import defaultdict
import hashlib
import html
from importlib.metadata import version
import json
from pathlib import Path
import re
import sys

from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_rust
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = MarkdownIt("commonmark")
LANGUAGE = Language(tree_sitter_rust.language())
QUERY = Query(LANGUAGE, tree_sitter_rust.HIGHLIGHTS_QUERY + """
(identifier) @variable
(enum_variant name: (identifier) @constructor)
["->" "=>" "=" "==" "!=" "&&" "||" "+" "-" "/" "%" "!"
 "?" "<" ">" "<=" ">=" "|" "^"] @operator
""")

# Specific syntax wins over broad identifier conventions in the upstream query.
# In particular, Decision is a type in Decision::Skip, while Skip is a constructor
# even when the same syntax is also captured as a scoped function call.
PRIORITY = {
    "variable": 10, "punctuation": 20, "operator": 25,
    "property": 40, "function": 50, "parameter": 76, "lifetime": 77,
    "constructor": 60, "type": 70, "constant": 75,
    "keyword": 80, "attribute": 85, "comment": 90,
    "string": 95, "escape": 100,
}


def role(capture):
    if capture == "variable.parameter":
        return "parameter"
    if capture == "label":
        return "lifetime"
    kind = capture.split(".", 1)[0]
    return kind if kind in PRIORITY else None


def highlight(source, palette):
    """Use byte ranges from Rust's syntax tree; preserve every source character."""
    data = source.encode("utf-8")
    tree = Parser(LANGUAGE).parse(data)
    starts, ends = defaultdict(list), defaultdict(list)
    for capture, nodes in QueryCursor(QUERY).captures(tree.root_node).items():
        kind = role(capture)
        if not kind:
            continue
        for node in nodes:
            if node.start_byte == node.end_byte:
                continue
            item = (node.start_byte, node.end_byte, kind)
            starts[node.start_byte].append(item)
            ends[node.end_byte].append(item)
    boundaries = sorted({0, len(data), *starts, *ends})
    active, runs = set(), []
    for left, right in zip(boundaries, boundaries[1:]):
        active.difference_update(ends[left])
        active.update(starts[left])
        selected = max(active, key=lambda item: (
            PRIORITY[item[2]], -(item[1] - item[0]), item[2]
        ))[2] if active else None
        text = data[left:right].decode("utf-8")
        if runs and runs[-1][0] == selected:
            runs[-1] = (selected, runs[-1][1] + text)
        else:
            runs.append((selected, text))
    rendered = []
    for kind, text in runs:
        escaped = html.escape(text, quote=False)
        if kind:
            color = palette["tokens"][kind]
            escaped = f'<span class="syn syn-{kind}" style="color:{color}">{escaped}</span>'
        rendered.append(escaped)
    return "".join(rendered)


def rust_blocks(markdown):
    """Use CommonMark parsing for nested, quoted, indented, and tilde fences."""
    for token in MARKDOWN.parse(markdown):
        language = token.info.split()[0].lower() if token.info.split() else ""
        if token.type == "fence" and language in ("rust", "rs"):
            yield token.content


def generate(root):
    palette = json.loads((root / "data/syntax/palette.json").read_text())
    for color in (palette["background"], palette["foreground"], *palette["tokens"].values()):
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            raise ValueError("Syntax palette colors must be six-digit hex values")
    if set(palette["tokens"]) != set(PRIORITY):
        raise ValueError("Every syntax role needs one palette color")
    snippets = {}
    for path in sorted((root / "content").rglob("*.md")):
        for source in rust_blocks(path.read_text()):
            # Hugo removes trailing newlines from .Inner; its native highlighter
            # then adds one when rendering. Match that behavior for cache keys
            # and copyable code, including snippets with trailing blank lines.
            inner = source.rstrip("\n")
            digest = hashlib.sha256(inner.encode("utf-8")).hexdigest()
            snippets[digest] = {"html": highlight(inner + "\n", palette)}
    return {
        "schema": 1,
        "tree_sitter": version("tree-sitter"),
        "rust_grammar": version("tree-sitter-rust"),
        "markdown": version("markdown-it-py"),
        "snippets": dict(sorted(snippets.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--write", action="store_true")
    actions.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    target = args.root / "data/syntax/rust.json"
    expected = json.dumps(generate(args.root), indent=2, ensure_ascii=False) + "\n"
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected)
    elif not target.exists() or target.read_text() != expected:
        print("Rust highlighting is stale. Run: python3 scripts/rust-highlighting.py --write",
              file=sys.stderr)
        return 1
    print(f'Rust highlighting is synchronized: {len(json.loads(expected)["snippets"])} blocks.')
    return 0


if __name__ == "__main__":
    sys.exit(main())
