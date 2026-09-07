# Editing this website

Maintain the restrained dark-green visual direction. Keep the site static and
small: Hugo, Markdown, hand-written templates and native CSS. No theme, frontend
framework, external fonts, analytics, or decorative JavaScript without a concrete
requirement. Never generate or retouch Josh’s photograph; use the supplied image.

Edit the source, not `public/`. Keep one publishing path. Before merging, run the
pinned Hugo build, source checks, and browser verification. After deployment,
inspect screenshots captured from **https://lanej.io/** at mobile and desktop
sizes. Confirm the expected revision and that the fetched image bytes decode and
match the build. Never call a change verified solely because a deploy job passed.

Writing is the primary destination. Put it first in navigation and directly after
the compact homepage introduction, with titles, descriptions, dates, reading times,
and archive/feed links. Career history supports the essays; keep employer context
below them. Do not turn the introduction, site title, or description into a company
biography. EasyPost is the current role, not the whole identity. Preserve accurate
Fastly and Engine Yard context without inventing responsibilities or outcomes.

Inspect first-viewport screenshots as well as full-page captures. On the homepage,
show Josh’s name once in the opening. On phones, place the compact circular portrait
beside the identity, with the introduction below; the complete portrait and primary
link must fit before scrolling, including short viewports with browser chrome.
Interior headers use navigation on the left and only a 44-pixel circular home-link
portrait on the right. Do not add visible name text to the header. Preserve the
link’s accessible name, keyboard access, and focus outline. At normal text sizes,
keep the header on one row from 320px up, with every link visible and at least a
44-by-44-pixel target. At enlarged text sizes, let navigation reflow without clipping,
hiding links, or shrinking text. Run these checks in the disposable writing fixture
and against the deployed custom domain; capture the header itself as well.

Keep the visible identity label in the homepage introduction, not in interior
page chrome. Do not repeat Josh’s name as a page-title eyebrow, article byline,
or footer label. Keep authorship in accessible labels, document titles, structured
metadata, and RSS; normal biographical prose is not an identity label.

Do not publish an empty Writing section or placeholder accomplishments. Distinguish
self-reported career history from independent public evidence. No private research,
personal contact information beyond approved public routes, confidential company
metrics, or non-public business strategy belongs in this repository or its drafts.

Citation previews are an approved functional progressive enhancement, not a
frontend framework. All future writing uses ordinary Markdown footnotes and the
shared citation assets; no per-article opt-in or duplicated note text. Prefer a
bold linked work title, author/year when known, and a separate paragraph explaining
what the source supports. See [citation authoring](docs/citations.md). Never infer
missing bibliographic metadata or omit qualifications. Preserve static endnotes,
return links, print, and full-text RSS. Run the shared citation tests (including
no-JavaScript/unsupported-browser fallbacks) and inspect live mobile/desktop cards.
