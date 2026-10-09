#!/usr/bin/env bash
# Publish a separately namespaced, public EasyUI Storybook preview without
# modifying the site's Hugo routes or the EasyUI GitHub Pages deployment.
set -euo pipefail

cd "$(dirname "$0")/.."

owner_repo="lanej/easy-ui"
pr_number="24"
destination="$PWD/public/previews/easy-ui/pr-$pr_number"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Use the PR head SHA, not a moving branch ref mid-build. Do not execute
# arbitrary fork PR code: this preview is explicitly restricted to lanej/easy-ui.
pr="$(curl --fail --silent --show-error --retry 3 "https://api.github.com/repos/$owner_repo/pulls/$pr_number")"
head_sha="$(printf '%s' "$pr" | python3 -c 'import json,sys; p=json.load(sys.stdin); assert p["head"]["repo"]["full_name"] == "lanej/easy-ui", "unexpected fork"; print(p["head"]["sha"])')"

git clone --quiet --no-checkout --filter=blob:none "https://github.com/$owner_repo.git" "$tmp/easy-ui"
git -C "$tmp/easy-ui" fetch --quiet --depth=1 origin "$head_sha"
git -C "$tmp/easy-ui" checkout --quiet --detach "$head_sha"

(
  cd "$tmp/easy-ui"
  npm ci --no-audit --no-fund
  npm run build:storybook -- --output-dir "$destination/storybook"
)

test -f "$destination/storybook/index.html"
printf '%s\n' "$head_sha" > "$destination/revision.txt"
printf 'Easy UI PR #%s Storybook preview at commit %s\n' "$pr_number" "$head_sha"
