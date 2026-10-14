#!/usr/bin/env python3
"""Generate the standalone skill from the guide; fail CI on source/output drift."""

import argparse
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content/writing/code-review/index.md"
ADAPTER = ROOT / "skills/code-review/adapter.md"
OUTPUT = ROOT / "static/skills/code-review/SKILL.md"
BEGIN = "<!-- code-review:begin -->"
END = "<!-- code-review:end -->"


def render(source: str, adapter: str) -> str:
    """Require one bounded guidance section and one occurrence of each placeholder."""
    if source.count(BEGIN) != 1 or source.count(END) != 1:
        raise ValueError("Guide must contain exactly one begin and one end marker")
    start = source.index(BEGIN) + len(BEGIN)
    end = source.index(END)
    if end <= start:
        raise ValueError("Guide markers are reversed or the guidance is empty")
    guidance = source[start:end].strip()
    if not guidance:
        raise ValueError("Guidance is empty")
    for token in ("{{GUIDANCE}}", "{{GUIDANCE_SHA256}}"):
        if adapter.count(token) != 1:
            raise ValueError(f"Adapter must contain exactly one {token}")
    digest = hashlib.sha256(guidance.encode("utf-8")).hexdigest()
    return adapter.replace("{{GUIDANCE_SHA256}}", digest).replace(
        "{{GUIDANCE}}", guidance
    ).rstrip() + "\n"


def check_file(path: Path, expected: bytes) -> None:
    if not path.is_file() or path.read_bytes() != expected:
        raise ValueError(
            f"Missing or out-of-date skill: {path}. "
            "Run python3 scripts/code-review-skill.py and commit the result."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing")
    parser.add_argument("--published", type=Path, help="Also check the built raw file")
    args = parser.parse_args()
    try:
        expected = render(
            SOURCE.read_text(encoding="utf-8"), ADAPTER.read_text(encoding="utf-8")
        ).encode("utf-8")
        if args.check or args.published:
            check_file(OUTPUT, expected)
        else:
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_bytes(expected)
        if args.published:
            check_file(args.published, expected)
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print("Code-review skill is synchronized with the guide.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
