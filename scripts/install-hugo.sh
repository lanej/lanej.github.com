#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
version=$(tr -d '\n' < .hugo-version)
[[ "$version" == "0.165.0" ]] || { echo 'Update the release checksum when changing Hugo versions.' >&2; exit 1; }
mkdir -p .tools
archive=$(mktemp)
trap 'rm -f "$archive"' EXIT
curl --fail --location --retry 3 -o "$archive" "https://github.com/gohugoio/hugo/releases/download/v${version}/hugo_${version}_linux-amd64.tar.gz"
echo "5c3a37a5450b3e386e5b75a87a790fea2d04a796d75e171216c80ef48a32b432  $archive" | sha256sum --check
tar -xzf "$archive" -C .tools hugo
.tools/hugo version
