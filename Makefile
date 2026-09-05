.PHONY: new preview build check test
HUGO ?= hugo

new:
	@test -n "$(SLUG)" || (echo 'Usage: make new SLUG=my-essay' >&2; exit 1)
	@printf '%s' "$(SLUG)" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$$' || (echo 'Use a lowercase-hyphenated slug.' >&2; exit 1)
	$(HUGO) new content --kind writing writing/$(SLUG)/index.md

preview:
	$(HUGO) server --buildDrafts --buildFuture --bind 127.0.0.1 --disableFastRender

build:
	HUGO_BIN="$(HUGO)" bash scripts/build.sh

check: build

test: build
	HUGO_BIN="$(HUGO)" python3 scripts/test-writing.py
