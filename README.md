# lanej.io

Josh Lane’s professional website. Hugo, Markdown, native CSS and a locally hosted
photograph. No theme, frontend JavaScript, CMS, external fonts, or runtime packages.

## Writing

Install the Hugo version in `.hugo-version` and Python 3.11 or later. The authoring
helper uses only Python’s standard library. On Linux, `bash scripts/install-hugo.sh`
installs the pinned Hugo binary; elsewhere use `hugo` on PATH or `HUGO_BIN`.

```sh
python3 scripts/writing.py new my-first-essay --title "My first essay"
nvim drafts/my-first-essay/index.md
python3 scripts/writing.py preview
```

Drafts live in **gitignored `drafts/`**, not the public content tree. Preview binds
only to `127.0.0.1` and includes drafts with a visible label and noindex metadata.
A production build never mounts `drafts/`. Gitignore is not access control: never
force-add private material or put it in an issue, PR, public branch, or CI log.

Each article is a Markdown page bundle: `index.md` plus its images in the same
folder. Use ordinary Markdown headings, links, tables, fenced code blocks and
footnotes. Use descriptive alt text: `![What the diagram shows](diagram.png)`.
TOML front matter provides `title`, `description`, `date`, `draft`, and optional
`toc = true`. Set `lastmod` explicitly when a published article is substantively
revised; routine rebuilds do not change its displayed dates.

When the text and every asset in its folder are approved for public release:

```sh
python3 scripts/writing.py publish my-first-essay
# Review content/writing/my-first-essay/ before staging the entire bundle.
git switch -c writing/my-first-essay
git add content/writing/my-first-essay
git diff --cached
git commit -m "Publish my first essay"
git push -u origin writing/my-first-essay
# Open a PR, inspect its checks/screenshots, then merge.
```

The helper moves the bundle into `content/writing/`, sets `draft = false`, and
sets the publication date. It does **not** commit, push, merge or deploy. It refuses
invalid slugs, missing titles/descriptions, empty articles, duplicate destinations,
and symlinks. Subsequent edits go directly into the published Markdown file.

Merging to `master` deploys through the existing tested workflow. Writing appears
in navigation and on the homepage automatically after the first published essay.
No placeholder essay is included. The chronological index is `/writing/`; the
full-text feed is `/index.xml` (with a section feed at `/writing/index.xml`). RSS
contains essays only, not About/Work pages. A future-dated article stays excluded
until a build after its date; there is no scheduled publishing service.

## Source layout

- `content/`: public pages and approved essays only.
- `data/work.yaml`: homepage selected-work summaries.
- `data/contributions.yaml`: dated merged upstream contributions and evidence links.
- `layouts/`: shared pages, circular portraits, article metadata and RSS.
- `assets/css/site.css` and `editorial.css`: compiled together into one fingerprinted stylesheet.
- `assets/images/josh-lane.webp`: approved 1254 × 1254 source photograph. Hugo
  makes responsive hero, small header-avatar and downloadable JPEG derivatives.
- `drafts/`: local-only work, ignored by Git and excluded from production.

The homepage uses the large circular portrait. Every interior page uses one
44-pixel circular portrait beside the name in the upper-left header; About no
longer repeats a large photograph. The downloadable image remains uncropped.

## Build and verify

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r scripts/requirements.txt
python -m playwright install --with-deps chromium webkit
bash scripts/install-hugo.sh
bash scripts/build.sh
python scripts/test-writing.py
python -m http.server 8765 --directory public &
python scripts/verify.py --engines chromium,webkit
```

`test-writing.py` creates a disposable site and checks the draft-to-publication
workflow, exclusion of private/future text, full-text RSS, and article rendering
with code, footnotes, tables and non-square images. Fixture content is never put
in this repository’s `content/` or deployed. Browser tests cover circular portraits,
responsive resolution, 44-pixel navigation targets, keyboard navigation, and
horizontal overflow in Chromium and WebKit. They discover published article pages
automatically. Python/browser dependencies are test tools, not visitor dependencies.

## Deployment

Merge a PR into `master`. Actions builds Hugo once, tests the output, deploys that
exact Pages artifact, then checks **https://lanej.io/**. Production checks wait for
the expected revision, compare actual response hashes with the tested artifact,
decode the images, and capture desktop/mobile screenshots. Inspect the
`live-domain-verification` artifact. A deploy success alone is not verification.

Settings → Pages → Source should be GitHub Actions. The existing temporary
legacy-publisher sequencing safeguard remains until that administrative toggle is
changed. Domain and HTTPS settings are unchanged. The root CNAME marker must match
`static/CNAME`; no generated root HTML is maintained separately.

To recheck production, download the same run’s `site-bundle` into `public/`:

```sh
python scripts/verify.py --url https://lanej.io/ --output artifacts/live --engines chromium,webkit
```

Rollback by reverting the relevant merge through the same workflow. Hugo and
Actions are pinned; update `.hugo-version` and the checksum in
`scripts/install-hugo.sh` together, then rerun the checks.

## Editorial constraints

Date code contributions and link the specific upstream PR. Merged contributions,
current maintainership, and financial sponsorship are different claims. Keep
historical fog-aws work modest. Do not publish private research, company metrics,
unapproved business claims, or proprietary strategy. No synthetic essays are
published under Josh’s name merely to populate the site.
