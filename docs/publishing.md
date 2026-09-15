# Publishing

For setup and a first draft, start with the [README](../README.md).
[WRITING.md](../WRITING.md) covers reasoning, voice, and evidence;
[STYLE.md](../STYLE.md) covers the shared article format.

## Drafts and article structure

The [README](../README.md#write-and-publish) has the create, preview, and publish
commands. Preview includes drafts and future-dated articles on `127.0.0.1`;
drafts have a visible label and noindex metadata.

Each article is a Markdown page bundle: `index.md` and its images in one folder.
Local bundles live in gitignored `drafts/`, which production builds never mount.
Gitignore and noindex are not access control. Never force-add private material or
put it in an issue, PR, public branch, or CI log. For approved material shared
before publication, see [unlisted drafts](unlisted-drafts.md).

Use ordinary Markdown headings, links, tables, fenced code blocks, and footnotes.
H2 headings become numbered chapters. Use the shared blockquotes and diagram
shortcodes rather than article-specific layouts.

TOML front matter supplies `title`, `description`, `date`, and `draft`. Fill in a
nonempty description and article body before publishing. Set `lastmod` explicitly
when substantively revising a published article. Dates remain in metadata and
RSS, outside the visible reading layout.

## Citations and images

Use normal Markdown footnotes; citation previews need no per-article setup.
Prefer a bold linked title, author/year when known, and a paragraph preserving
the source's context and limitations. See [citation authoring](citations.md) for
examples. Static endnotes, return links, print, and RSS remain available; the
visitor's browser does not fetch or summarize sources.

Use descriptive alt text. A standalone Markdown image becomes a figure, and its
optional title becomes a visible caption:

```markdown
![What the diagram shows](diagram.png "Why this diagram matters.")
```

For an article-specific social preview, put the approved JPEG, PNG, or WebP image
in the bundle or `assets/`, then add:

```toml
social_image = "cover.jpg"
social_image_alt = "Describe the cover or diagram"
```

The build checks the resource and alt text. Omitting `social_image` retains the
headshot fallback; Person metadata always keeps the portrait.

## Prepare and publish

Only prepare a bundle after its text and every asset are approved for public
release:

```sh
python3 scripts/writing.py publish my-essay
# Review content/writing/my-essay/ before staging the entire bundle.
git switch -c writing/my-essay
git add content/writing/my-essay
git diff --cached
git commit -m "Publish my-essay"
git push -u origin writing/my-essay
```

The helper moves the bundle into `content/writing/`, sets `draft = false`, and
sets the publication date. It does not commit, push, merge, or deploy. It rejects
invalid slugs, missing titles/descriptions, empty articles, duplicate
destinations, and symlinks. Edit published articles directly in their bundles.

Open a PR, inspect its checks and page previews, then merge into `master`.
Follow [deployment verification](development.md#deployment), not just the deploy
job's status.

The writing index is `/writing/`. Full-text feeds are `/index.xml` and
`/writing/index.xml`; they contain essays, not About or Work pages. Future-dated
articles remain excluded until a build after their date; publication is not
scheduled automatically.

## Public claims

Follow the disclosure and accuracy constraints in [AGENTS.md](../AGENTS.md).
Date code contributions and link the specific upstream PR; distinguish merged
contributions, current maintainership, and financial sponsorship. Keep historical
fog-aws work modest. Work is the concise reference; About carries the narrative.
