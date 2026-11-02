#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
revision=$(tr -d '\n' < .wirelit-version)
[[ "$revision" =~ ^[0-9a-f]{40}$ ]] || { echo 'Wirelit must be pinned to a full commit SHA.' >&2; exit 1; }
source_dir=$(mktemp -d)
trap 'rm -rf "$source_dir"' EXIT
git -C "$source_dir" init --quiet
git -C "$source_dir" remote add origin https://github.com/lanej/wirelit.git
git -C "$source_dir" fetch --quiet --depth 1 origin "$revision"
git -C "$source_dir" checkout --quiet --detach FETCH_HEAD
test "$(git -C "$source_dir" rev-parse HEAD)" = "$revision"
(
  cd "$source_dir"
  npm ci --no-audit --no-fund
  npm run build
  npm run fixture
  node dist/cli.js generate --config examples/wirelit.json
  # Astro owns canonical URLs; Wirelit's MDX transformer owns the /wirelit links.
  GITHUB_PAGES=true npm run build --workspace examples/site -- --site https://lanej.io
  GITHUB_PAGES=true node scripts/check-links.mjs
)
python3 scripts/wirelit_docs.py "$source_dir/examples/site/dist"
test -f public/build.json # Assemble only after the validated Hugo build.
rm -rf public/wirelit
cp -a "$source_dir/examples/site/dist" public/wirelit
echo "Assembled Wirelit $revision at /wirelit/ in the Pages bundle."
