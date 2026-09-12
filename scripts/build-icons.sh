#!/usr/bin/env bash
# Rebuild deterministic icon exports from the approved photograph (ImageMagick 6/7).
set -euo pipefail
cd "$(dirname "$0")/.."
if command -v magick >/dev/null 2>&1; then im=magick; else im=convert; fi
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p assets/icons

# Apply the same circular frame used on the site, without changing the photograph.
"$im" assets/images/josh-lane.webp -resize 720x720 \
  \( -size 720x720 xc:black -fill white -draw 'circle 360,360 360,0' \) \
  -alpha off -compose CopyOpacity -composite "$tmp/circle.png"
for size in 16 32 48; do
  "$im" "$tmp/circle.png" -resize "${size}x${size}" -strip "$tmp/$size.png"
done
"$im" "$tmp/16.png" "$tmp/32.png" "$tmp/48.png" static/favicon.ico
cp "$tmp/48.png" assets/icons/favicon-48.png

# iOS supplies its own outer corner mask; give the circular portrait an opaque tile.
"$im" "$tmp/circle.png" -resize 156x156 -background '#0d1513' \
  -alpha remove -alpha off -gravity center -extent 180x180 -strip \
  assets/icons/apple-touch-icon.png
