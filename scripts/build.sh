#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
HUGO_BIN=${HUGO_BIN:-.tools/hugo}
export HUGO_PARAMS_REVISION=${GITHUB_SHA:-${HUGO_PARAMS_REVISION:-local}}
python3 scripts/test-code-review-skill.py
python3 scripts/code-review-skill.py --check
"$HUGO_BIN" --gc --minify --cleanDestinationDir --panicOnWarning
python3 scripts/code-review-skill.py --check --published public/skills/code-review/SKILL.md
python3 scripts/check.py public
python3 scripts/test-unlisted.py --hugo "$HUGO_BIN"
