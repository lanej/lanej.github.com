# Publishing writing

Use Markdown page bundles. Each article is one folder, with its images and other
assets alongside `index.md`. No CMS, database, theme, or frontend JavaScript.

## Start and preview

Install the Hugo version in `.hugo-version`. From the repository root:

```sh
make new SLUG=your-essay
nvim content/writing/your-essay/index.md
make preview
```

Open `http://localhost:1313/writing/your-essay/`. The preview includes drafts and
future-dated articles; it is bound to localhost, marked noindex, and shows a draft
label. Production builds omit drafts and future-dated articles.

**Draft does not mean private.** This repository and its branches/PRs are public.
Keep confidential notes and unapproved company information outside the repository.
Only commit drafts whose source you are comfortable making public. Removing a
page later does not erase its Git history.

## Front matter

```yaml
---
title: A specific title
date: '2026-09-05T09:00:00-07:00'
description: A one-sentence description for the index, search, and link previews.
draft: true
toc: false
---
```

The title, a meaningful description, date, and nonempty article body are required
before publishing. Set `toc: true` for a longer article that benefits from a table
of contents. Add `lastmod:` when a later substantive revision warrants an updated
date. Keep the slug stable after publication; use Hugo `aliases` to preserve an
old path when a rename is necessary.

Use normal Markdown for headings, links, lists, code fences with a language,
blockquotes, tables, and footnotes. Put images next to the article and give them
an informative alt text: `![Description of the diagram](diagram.png)`.

## Publish deliberately

1. Review claims, attribution, external links, and disclosure permission.
2. Set `draft: false` and set `date` to the intended publication date and timezone.
3. Run `make test`. Inspect the local browser preview at mobile and desktop sizes.
4. Commit the article folder and open a PR. Merge after its checks pass.
5. Check the post-deployment `live-domain-verification` artifact and the actual
   article URL on `https://lanej.io/`.

Writing appears in navigation and on the homepage automatically with the first
published article. `/writing/` is the chronological archive;
`/writing/index.xml` is the full-content RSS feed. Article pages include author,
publication date, reading time, optional updated date, canonical URL, social
metadata, and BlogPosting structured data.

A future date is an exclusion rule, **not a timer**: the site only changes after
a successful build and deployment. For scheduled publication, run the existing
workflow manually on/after that date or merge at publication time. No scheduled
background publisher is configured.

## Test coverage

`make test` creates synthetic articles in a temporary copy, never in the real
content tree. It tests draft-only exclusion, future-date exclusion, archive and
RSS entries, metadata, heading anchors, a rectangular image, and rejection of
incomplete published articles. CI also browser-tests the sample article and
archive; those fixtures are never part of the deployed site.
