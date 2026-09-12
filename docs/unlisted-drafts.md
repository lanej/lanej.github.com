# Unlisted essay drafts

An unlisted draft is a normal essay rendered at its eventual URL, but omitted from the site's public discovery surfaces. It uses the shared essay layout, citations, and diagrams with a small **Draft · Unlisted** label.

| State | Front matter | Live URL | Public listings and feeds |
| --- | --- | --- | --- |
| Offline draft | `draft = true` | No | No |
| Unlisted review copy | `draft = false`, `unlisted = true` | Yes | No |
| Published essay | `draft = false`, `unlisted` absent or false | Yes | Yes |

Create a review copy with the pinned Hugo binary:

```sh
.tools/hugo new content --kind unlisted writing/essay-slug/index.md
```

Complete the description, opening callout, and visual using the existing essay conventions. Merge the review copy's PR to deploy it, then share its direct `/writing/essay-slug/` URL. No special preview server or global `--buildDrafts` flag is needed.

To publish, set `unlisted = false` (or remove it) and set `date` to the intended publication date. Keep the file path and slug unchanged. The same URL enters the homepage's date-sorted selection, Writing archive, RSS feeds, and sitemap; its draft label and `noindex` directive disappear. Normal future-date and expiry rules still apply.

## Discovery is not access control

Unlisted essays are excluded from homepage and section lists, all RSS feeds, the sitemap, and the public `build.json` inventory. Their bundle resources are also omitted from that inventory. Keep essay-specific assets in the essay's page bundle. New public page collections should use `layouts/partials/listed-pages.html` before sorting or pagination. Source validation rejects links from public HTML into unlisted essay bundles.

The HTML includes `noindex, nofollow`. Do not add its path to `robots.txt`: crawlers must be able to read the directive. [Google documents this distinction](https://developers.google.com/search/docs/crawling-indexing/block-indexing).

Anyone with the URL can read, forward, or copy it. This repository and its PRs are public, so the source, review discussions, and screenshots can also reveal it. Unlisted is suitable for work-in-progress review, **not confidential material**. Use authenticated hosting for that. Making an already-public essay unlisted cannot recall feed deliveries, external links, or cached copies.

## Verification

`scripts/test-unlisted.py` is one lifecycle regression run by `scripts/build.sh`. It builds a disposable review copy with the real templates, checks its direct page and discovery exclusions (including bundle resources), publishes it at the same URL, then makes it an offline draft and checks stale output is removed. It never adds fixture content to the production build. When Chromium is available, it also captures desktop/mobile review-state screenshots into the existing preflight artifact.
