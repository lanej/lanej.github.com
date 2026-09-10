# lanej.io

Josh Lane’s professional website. Hugo, Markdown, native CSS and a locally hosted
photograph. No theme, frontend framework, CMS, external fonts, or runtime packages.
A small native JavaScript enhancement opens citation previews; all content and
ordinary references remain usable without it.

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
footnotes. Every H2 becomes a numbered chapter in the shared essay format;
blockquotes and diagram shortcodes use the common components in `STYLE.md`.
TOML front matter provides `title`, `description`, `date`, and `draft`. Set
`lastmod` explicitly when a published article is substantively revised. Dates
remain in structured metadata and RSS, outside the visible reading layout.

### Sources and citation previews

Use normal Markdown footnotes. Every article automatically gets click/tap source
cards; no per-post setup is needed. Prefer a bold linked title, author/year when
known, and a paragraph preserving the source's context and limitations. Older
prose notes work too. See [the citation guide](docs/citations.md) for examples.
Static endnotes, return links, print, and RSS remain available. Sources are never
fetched or summarized by the visitor's browser.

### Images, captions, and sharing

Use descriptive alt text. A standalone Markdown image becomes a figure; its
optional title becomes a visible caption, not a hover-only tooltip:

```markdown
![A description of what the diagram shows](diagram.png "A visible caption explaining its significance.")
```

An article can use its own social-preview image. Put the approved image in the
article bundle (or `assets/`) and add these optional front-matter fields:

```toml
social_image = "cover.jpg"
social_image_alt = "Describe the cover or diagram"
```

Supported formats are JPEG, PNG, and WebP. The build verifies the resource,
requires alt text, and records its actual dimensions in Open Graph metadata.
Article images are used in Open Graph, Twitter cards, and BlogPosting data; they
never replace the portrait in Person metadata. Omitting `social_image` keeps the
headshot fallback. No image service or visitor-side JavaScript is involved.

When the text and every asset in its folder are approved for public release:

```sh
python3 scripts/writing.py publish my-first-essay
# Review content/writing/my-first-essay/ before staging the entire bundle.
git switch -c writing/my-first-essay
git add content/writing/my-first-essay
git diff --cached
git commit -m "Publish my-first-essay"
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

- `content/`: public pages and approved essays only. Work section links live in the page’s `sections` front matter.
- `data/work.yaml`: homepage selected-work summaries.
- `data/contributions.yaml`: dated merged upstream contributions and evidence links.
- `layouts/`: shared pages, circular portraits, article metadata and RSS. The speaker-resources shortcode groups the reusable biography and headshot download in a native disclosure.
- `assets/css/site.css` and `editorial.css`: compiled into one fingerprinted stylesheet. Articles with `diagrams: true` also include `diagrams.css`.
- `assets/js/citations.js` and `assets/css/citations.css`: local, fingerprinted citation previews, loaded only by articles with footnotes.
- `assets/images/josh-lane.webp`: approved 1254 × 1254 source photograph. Hugo makes responsive hero, header-avatar and downloadable JPEG derivatives.
- `drafts/`: local-only work, ignored by Git and excluded from production.

The homepage uses a compact circular portrait beside its introduction. Interior
pages use a 44-pixel circular home link at the right of the header, with navigation
on the left and no visible name. The accessible home-link label is retained. The
downloadable image remains uncropped.

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

`test-writing.py` creates a disposable site and checks draft-to-publication,
exclusion of private/future text, full-text RSS, captions, article-specific share
images and portrait fallbacks. Missing share images and alt text fail the build.
Fixture content is never put in this repository’s `content/` or deployed.

Browser tests cover portraits, image resolution, keyboard navigation, section
links, speaker-resource disclosure, tablet composition, and text reflow at 200%.
`header_checks.py` requires one navigation row at normal text sizes, the portrait
at the right margin, aligned centers, no visible header name, an accessible home
link, unclipped text, and 44-by-44-pixel tap targets. The same checks run on every
page in preflight and production; header screenshots are saved at mobile and
desktop sizes. At enlarged text sizes, wrapping and vertical scrolling are allowed;
we do not shrink text or hide content to pass a first-screen test. Published
articles are discovered automatically, including their diagrams and citation
previews. Citation tests cover keyboard/touch interaction, repeated notes, complete
source content, long-note scrolling, print, no-JavaScript and unsupported-browser
fallbacks, plus disposable future-article fixtures. The test tools are not visitor
dependencies.

## Deployment

Pull requests include an automatically refreshed **Page previews** section in the
description. CI captures affected pages at 390px mobile and 1440px desktop widths;
select a viewport image to open the full-page capture. Shared templates and assets
conservatively capture every page. The section identifies the source revision and
preserves text outside its HTML markers.

Images live on separate `pr-previews/<number>` branches and use immutable commit
URLs, so they stay viewable after Actions artifacts expire and never enter the
website build. Same-repository PRs publish automatically after the build passes;
fork PRs provide the `pr-page-previews` download artifact without write access.

Merge a PR into `master`. Actions builds Hugo once, tests the output, deploys that
exact Pages artifact, then checks **https://lanej.io/**. Production checks wait for
the expected revision, compare actual response hashes with the tested artifact,
decode images, and capture desktop/mobile screenshots. Inspect the
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
published under Josh’s name merely to populate the site. Work is the concise
reference; About carries the narrative. Preserve the evidence and remove copy
that merely tells readers why the evidence is important.
