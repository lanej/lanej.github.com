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

## Rust highlighting

Rust fences use the pinned Tree-sitter Rust grammar at build time. Types,
constructors, calls, parameters, and fields get distinct roles; this does not
resolve names like a compiler. The palette lives in
`data/syntax/palette.json` and the shared code styles in `assets/css/syntax.css`.

After editing Rust snippets or the palette, run:

```sh
python3 scripts/rust-highlighting.py --write
bash scripts/build.sh
```

Commit `data/syntax/rust.json` with the source change. The build verifies this
generated cache, and the render hook refuses a missing snippet. That keeps the
normal build and trusted Hugo-only PR previews consistent. No highlighting
JavaScript or parser is delivered to readers. Inline token colors preserve RSS;
the shared stylesheet supplies print and keyboard-scroll behavior.

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

### Wirelit documentation

The same Pages bundle serves Wirelit's Starlight documentation at
`https://lanej.io/wirelit/`. After `bash scripts/build.sh`, run
`bash scripts/build-wirelit.sh` to assemble it locally using Node 24.
The builder fetches the exact commit in `.wirelit-version`, installs its locked
dependencies, compiles the complex sample, and runs the built Wirelit CLI to
generate the reference before building Starlight. Astro receives the custom
domain through `--site`; the project supplies its `/wirelit/` base path.

The builder validates canonical URLs, internal links, anchors, assets, and search,
then writes `public/wirelit/build.json`. Deployment checks every published file
against those hashes, independently of the Hugo manifest. To update the docs,
replace `.wirelit-version` with a reviewed full commit SHA and open a website PR.
The website remains the only publisher; no separate Wirelit Pages setting is
required. Hugo's clean build removes the old mount before it is reassembled.

### Zellij client documentation

The same GitHub Pages bundle serves [zellij-client.nvim](https://lanej.io/zellij-client.nvim/). Its Starlight source lives in the library repository. `.zellij-client-version` pins the full source commit; `bash scripts/build-zellij-client.sh` fetches that commit, installs the website lockfile and assembles its built output after the Hugo build. It validates the base path, canonical URLs, local assets, anchors and search before recording file hashes in `public/zellij-client.nvim/build.json`.

Update the pin through a website PR after reviewing a documentation revision. The existing preview workflow captures the overview and client API at mobile and desktop sizes. Deployment verifies every project file against the tested manifest and checks the rendered pages on lanej.io. The website remains the only Pages publisher; the library's docs workflow checks its build without deploying separately.

### Easy UI pull request Storybooks

Each open same-repository `lanej/easy-ui` PR is built at
`https://lanej.io/previews/easy-ui/pr-<number>/storybook/`. Preserved PR numbers in
`data/easy-ui-previews.json` keep selected previews available after closure. The
builder pins each checkout to the fetched PR head SHA, builds package declarations
before Storybook, and keeps each preview in its own directory.

Previews refresh with the lanej.io Pages deployment, including a manual run of
`pages.yml` on `master`. Before posting a link, confirm the preview's adjacent
`revision.txt` matches the Easy UI PR head SHA. The workflow compares entry-point
bytes with the tested bundle and captures each live preview at mobile and desktop
widths. The `live-domain-verification` artifact retains those screenshots and
the revision report.

The Pages build allows 45 minutes for the retained Storybooks and site checks.
Active publishing runs finish before the latest queued update starts.

### Website deployment

Website PRs have browsable GitHub Pages snapshots under
`https://lanej.io/previews/site/pr-<number>/`. The description links directly to
the changed essay or page after deployment verification. These are complete Hugo
snapshots with relative navigation, isolated assets, a source revision marker,
and `noindex, nofollow`; the canonical website and its discovery surfaces retain
their published content.

Owned PR changes request a refresh from the trusted default-branch workflow.
Preview-only refreshes reuse the currently published, hash-verified site bundle
instead of rebuilding Wirelit and Easy UI Storybooks. Ordinary website changes
still run the complete build. Both modes use the same serialized Pages publisher.
The retained production artifact lasts 14 days; if no usable artifact remains,
refresh planning falls back to the full build. Each preview is pinned to its PR
head, and a broken unrelated draft is isolated. Forks are excluded.

The publisher uses pinned Hugo without executing PR scripts or forwarding Actions
credentials to the preview build. It verifies deployed bytes and mobile/desktop
rendering before updating the `site-preview` block in each PR description. Preserve
that block and the separate screenshot-preview markers during description edits.

PR descriptions receive a **Page previews** section with affected pages at 390px
mobile and 1440px desktop widths, collapsed by default. Only pages whose rendered
HTML or referenced assets differ from the PR base are included. Source dependency
selection uses committed changes; routine CI activity refreshes and unchanged
pages selected for verification do not add previews. Offline draft-only edits
need no screenshots. Preserve its HTML markers when editing the
description. Previews use immutable URLs on `pr-previews/<number>` branches, not
website source. Fork PRs provide the `pr-page-previews` artifact instead.

Local verification and PR previews include rendered unlisted essay bundles through
`scripts/verification_pages.py`. This inventory stays separate from the public
build manifest, feeds, and discovery surfaces. Shared essay geometry rules must
include new essays and their print/enlarged states.

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
