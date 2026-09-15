# Development and deployment

Start with [AGENTS.md](../AGENTS.md) for editing constraints and
[STYLE.md](../STYLE.md) for the visual contract. Edit source, never generated
`public/`. Keep one publishing path.

## Build and verify

The commands below use the Linux x86-64 Hugo installer. On other platforms,
install the version in [`.hugo-version`](../.hugo-version) and set
`HUGO_BIN` to its absolute path, for example
`export HUGO_BIN="$(command -v hugo)"`, instead of running the installer.
Python 3.11+ is required; Node 22+ is only needed for development checks.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r scripts/requirements.txt
python -m playwright install --with-deps chromium webkit
bash scripts/install-hugo.sh
bash scripts/build.sh
python scripts/test-writing.py
bash scripts/install-viewrule.sh
python scripts/viewrule.py install-browser
python -m http.server 8765 --bind 127.0.0.1 --directory public &
python scripts/verify.py --engines chromium,webkit
python scripts/viewrule.py check
```

The build runs Hugo and source/unlisted-content checks. Writing tests use
disposable fixtures, never deployed content. For UI changes, follow the
[Viewrule guide](viewrule.md) for rules, affected-page selection, reports, and
measurement limits; use `check --all` for a full audit. Inspect screenshots as
well as check results.

## Source map

| Location | Purpose |
| --- | --- |
| `content/` | Public pages and approved article bundles |
| `drafts/` | Gitignored local writing, excluded from production |
| `data/` | Selected work, contribution records, and other structured content |
| `layouts/` | Shared templates, shortcodes, metadata, and RSS |
| `assets/` | CSS, JavaScript, source images, and fingerprinted icons |
| `static/` | Files served directly, including `CNAME` and fallback icons |
| `scripts/` | Authoring, builds, verification, and asset maintenance |
| `.github/workflows/` | CI, page previews, audits, and deployment |

See [labs and activity](labs-and-activity.md) for project and contribution updates,
and [publishing](publishing.md) for article assets and metadata.

### Portraits and icons

Use the approved photograph at `assets/images/josh-lane.webp`; never generate or
retouch it. Hugo creates responsive portraits and the downloadable JPEG.

After an approved icon-source change, rebuild with ImageMagick 6 or 7:

```sh
bash scripts/build-icons.sh
```

Keep the touch-icon copies in `assets/icons/` and `static/apple-touch-icon.png`
in sync. The opaque dark-green root tile is Safari's fallback; standalone project
repositories should still declare their own icons explicitly.

## Deployment

PR descriptions receive a **Page previews** section with affected pages at 390px
mobile and 1440px desktop widths. Preserve its HTML markers when editing the
description. Previews use immutable URLs on `pr-previews/<number>` branches, not
website source. Fork PRs provide the `pr-page-previews` artifact instead.

Merging into `master` builds and tests one Pages artifact, deploys that exact
artifact, then verifies `https://lanej.io/`. Production checks wait for the
expected revision, compare response hashes with the tested artifact, decode
images, and capture desktop/mobile screenshots. Inspect the
`live-domain-verification` artifact. A successful deploy alone is not verification.

GitHub Pages should use GitHub Actions as its source. The workflow includes a
legacy-publisher sequencing safeguard; retain it until the Pages source setting
has been confirmed. Keep the root `CNAME` marker equal to `static/CNAME`, and do
not maintain generated root HTML separately.

To recheck production, download the same run's `site-bundle` into `public/`, then:

```sh
python scripts/verify.py --url https://lanej.io/ --output artifacts/live --engines chromium,webkit
```

Rollback by reverting the relevant merge through the same workflow. When updating
Hugo, change `.hugo-version` and the version/checksum in `scripts/install-hugo.sh`
together, then rerun verification. Keep Actions pinned as well.
