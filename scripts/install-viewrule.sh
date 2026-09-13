#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Update the release URL and verified checksum together; never install latest.
version=0.3.1
checksum=d22783f3d37f5a7fcb0f6fae1504e4ac62ef94c56d56844d121739bf7d525419
node -e 'if (Number(process.versions.node.split(".")[0]) < 22) process.exit(1)'
archive=$(mktemp -d)
trap 'rm -rf "$archive"' EXIT
curl --fail --location --retry 3 -o "$archive/viewrule.tgz" \
  "https://github.com/lanej/viewrule/releases/download/v${version}/viewrule-${version}.tgz"
echo "$checksum  $archive/viewrule.tgz" | sha256sum --check
# The release includes a shrinkwrap for its transitive runtime dependencies.
npm install --prefix .tools/viewrule --no-save --package-lock=false --ignore-scripts \
  --no-audit --no-fund "$archive/viewrule.tgz"
