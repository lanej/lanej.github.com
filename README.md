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
footnotes. TOML front matter provides `title`, `description`, `date`, `draft`, and
optional `toc = true`. Set `lastmod` explicitly when a published article is
substantively revised; routine rebuilds do not change its displayed dates.

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
- `assets/images/josh-lane.webp`: approved 1254 × 1254 source photograph. Hugo makes responsive hero, header-avatar and downloadable JPEG derivatives.
- `drafts/`: local-only work, ignored by Git and excluded from production.

The homepage uses a compact circular portrait on phones and a larger portrait on
desktop, scaling through tablet widths. Interior pages use one 44-pixel circular
portrait beside the name. The downloadable image remains uncropped.

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
links, speaker-resource disclosure, phone navigation rows, tablet composition,
and text reflow at 200%. At enlarged text sizes, vertical scrolling is allowed;
we do not shrink text or hide content to pass a first-screen test. Published
articles are discovered automatically, including their diagrams. The test tools
are not visitor dependencies.

## Deployment

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
