# lanej.io

Josh Lane’s professional website: Hugo, Markdown, native CSS, and the supplied
photograph. No theme, frontend JavaScript, CMS, external fonts, or runtime package
dependencies.

## Write and preview

Install the Hugo version in `.hugo-version`:

```sh
make new SLUG=your-essay
nvim content/writing/your-essay/index.md
make preview
```

See [the writing guide](docs/writing.md) for publication, page bundles, images,
front matter, RSS, and revision conventions. Drafts default to unpublished.
**This is a public repository: a draft commit is still public.** Keep confidential
notes and unapproved company information outside it, including outside PR branches.

Writing appears in navigation and on the homepage only when there is a published
article. The build excludes drafts, future-dated articles, and empty archives.
A future publication date requires a later build; there is no automatic timer.

## Source layout

- `content/`: page copy and essays in `writing/<slug>/index.md` bundles.
- `data/work.yaml`: selected-work summaries for the homepage.
- `layouts/`: shared structure, article and archive templates, RSS, and metadata.
- `assets/css/site.css`: the visual system and CSS-only circular portrait framing.
- `assets/images/josh-lane.webp`: the supplied 1254 × 1254 photograph, unchanged.
  Hugo generates responsive hero images, small header avatars, and a JPEG download.
- `scripts/`: build checks and local/live browser verification.

All non-home pages use the small portrait in the header, not a second large image.
Edit source, never generated `public/` files.

## Build and test

On Linux, `bash scripts/install-hugo.sh` installs the pinned, checksum-verified
Hugo binary. Elsewhere install the same version and set `HUGO_BIN` to its path.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r scripts/requirements.txt
python -m playwright install --with-deps chromium webkit
bash scripts/install-hugo.sh
bash scripts/build.sh
HUGO_BIN=.tools/hugo python scripts/test-writing.py --engines chromium,webkit
python -m http.server 8765 --directory public &
python scripts/verify.py --engines chromium,webkit
```

`make test` uses an installed `hugo` and runs the build and writing lifecycle checks.
The writing tests generate synthetic articles in a temporary copy, check draft and
future exclusion, publication and withdrawal, RSS, metadata, and missing content.
CI also browser-tests that sample archive and article. Fixtures never ship.

Python packages and browser binaries are verification tools, not site dependencies.
`public/`, generated image caches, and test artifacts are ignored.

## Publish and verify

Merge a PR into `master`. Actions builds Hugo, validates the output, and checks
Chromium and WebKit across mobile and desktop widths. It deploys the same tested
artifact rather than a separately edited HTML tree.

After deployment, the verifier waits for the expected revision on **lanej.io**,
checks response hashes against the build, decodes the actual images, checks circular
framing and header avatars, and captures screenshots. It also covers Writing when
articles exist. A successful deployment alone is not verification.

Download the `live-domain-verification` Actions artifact for the report and actual
custom-domain screenshots. Preflight also includes a `writing-fixture` directory
with sample-article and archive screenshots and the publishing-test results.

In repository **Settings → Pages**, Source should be **GitHub Actions**. The
workflow retains its compatibility safeguard: when legacy branch publishing is
still enabled, it waits for that run before deploying Hugo. The domain and HTTPS
settings are unchanged; root and static `CNAME` markers are checked for agreement.

To check a deployment manually, extract its `site-bundle` artifact into `public/`:

```sh
python scripts/verify.py --url https://lanej.io/ --output artifacts/live --engines chromium,webkit
```

Rollback: revert the merge and let the same pipeline publish and verify it.

## Content and attribution

Link specific contributions to upstream PRs and distinguish merged work from
proposals. Date historical work; do not imply current maintainership. Career
accounts and public software evidence are distinct. Do not invent impact metrics,
attribute company-wide performance solely to one person, or publish confidential
strategy. Neovim support is financial support, not a claim of code authorship.

Hugo and Actions are pinned. Upgrade `.hugo-version` and the checksum in
`scripts/install-hugo.sh` together, then run the full checks.
