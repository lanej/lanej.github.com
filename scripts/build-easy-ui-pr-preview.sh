#!/usr/bin/env bash
# Publish a separately namespaced, public EasyUI Storybook preview without
# modifying the site's Hugo routes or the EasyUI GitHub Pages deployment.
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/easy-ui-previews.py build
