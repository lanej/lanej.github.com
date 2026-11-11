#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
revision=$(tr -d '\n' < .zellij-client-version)
[[ "$revision" =~ ^[0-9a-f]{40}$ ]] || { echo 'Zellij client docs must be pinned to a full commit SHA.' >&2; exit 1; }
source_dir=$(mktemp -d)
trap 'rm -rf "$source_dir"' EXIT
git -C "$source_dir" init --quiet
git -C "$source_dir" remote add origin https://github.com/lanej/zellij-client.nvim.git
git -C "$source_dir" fetch --quiet --depth 1 origin "$revision"
git -C "$source_dir" checkout --quiet --detach FETCH_HEAD
test "$(git -C "$source_dir" rev-parse HEAD)" = "$revision"
(
  cd "$source_dir/website"
  npm ci --no-audit --no-fund
  npm run build -- --site https://lanej.io
)
python3 scripts/zellij_client_docs.py "$source_dir/website/dist"
test -f public/build.json
rm -rf public/zellij-client.nvim
cp -a "$source_dir/website/dist" public/zellij-client.nvim
echo "Assembled Zellij client $revision at /zellij-client.nvim/ in the Pages bundle."
