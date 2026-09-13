#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Update the release URL and verified checksum together; never install latest.
version=0.3.0
checksum=5ab24b47eab578eb5ab732ff7d65b715423e7e90ce13d72cb49c9ce7cc31e0bc
node -e 'if (Number(process.versions.node.split(".")[0]) < 22) process.exit(1)'
archive=$(mktemp -d)
trap 'rm -rf "$archive"' EXIT
curl --fail --location --retry 3 -o "$archive/viewrule.tgz" \
  "https://github.com/lanej/viewrule/releases/download/v${version}/viewrule-${version}.tgz"
echo "$checksum  $archive/viewrule.tgz" | sha256sum --check
# The release includes a shrinkwrap for its transitive runtime dependencies.
npm install --prefix .tools/viewrule --no-save --package-lock=false --ignore-scripts \
  --no-audit --no-fund "$archive/viewrule.tgz"
