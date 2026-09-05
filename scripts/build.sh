#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
HUGO_BIN=${HUGO_BIN:-.tools/hugo}
export HUGO_PARAMS_REVISION=${GITHUB_SHA:-${HUGO_PARAMS_REVISION:-local}}
# Do not publish empty archives when the only nested content is draft/future.
# Hugo itself decides which content is publishable; do not duplicate its date rules.
kinds=taxonomy,term
if ! "$HUGO_BIN" list published | python3 -c 'import csv,sys; sys.exit(not any(r["kind"] == "page" and r["section"] for r in csv.DictReader(sys.stdin)))'; then
  kinds=taxonomy,term,section,RSS
fi
# Discard generated output so withdrawn posts and their media cannot linger.
rm -rf -- public
"$HUGO_BIN" --disableKinds "$kinds" --gc --minify --cleanDestinationDir --panicOnWarning
python3 scripts/check.py public
