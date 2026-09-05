#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
HUGO_BIN=${HUGO_BIN:-.tools/hugo}
export HUGO_PARAMS_REVISION=${GITHUB_SHA:-${HUGO_PARAMS_REVISION:-local}}
"$HUGO_BIN" --gc --minify --cleanDestinationDir --panicOnWarning
python3 scripts/check.py public
