# Editing this website

Maintain the restrained dark-green visual direction. Keep the site static and
small: Hugo, Markdown, hand-written templates and native CSS. No theme, frontend
framework, external fonts, analytics, or decorative JavaScript without a concrete
requirement. Never generate or retouch Josh’s photograph; use the supplied image.

Edit the source, not `public/`. Keep one publishing path. Before merging, run the
pinned Hugo build, source checks, and browser verification. Confirm the PR description
contains current mobile and desktop screenshots of affected pages from the preview
workflow. Preserve the automated preview markers when editing PR descriptions.
Screenshots are kept on separate preview branches, not in source. After deployment,
inspect screenshots captured from **https://lanej.io/** at mobile and desktop
sizes. Confirm the expected revision and that the fetched image bytes decode and
match the build. Never call a change verified solely because a deploy job passed.

Writing is the primary destination. Put it first in navigation and directly after
the compact homepage introduction, with titles, descriptions, dates, reading times,
and archive/feed links. Career history supports the essays; keep employer context
below them. Do not turn the introduction, site title, or description into a company
biography. EasyPost is the current role, not the whole identity. Preserve accurate
Fastly and Engine Yard context without inventing responsibilities or outcomes.

The career narrative runs from frontline operations through quality/software
engineering and infrastructure to technology leadership. UPS was package handling
and supervision; EMC was a quality-engineering co-op; 3M/Brontes was software
engineering and QA automation; HubSpot was software engineering. Do not inflate
those titles or imply all four were operations roles. Keep earlier Work entries
compact (company, role, dates), with the narrative on About and a short background
below homepage writing. Avoid invented origin stories, achievements, or a claim
that this was a predetermined career plan.

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

All essays use the shared Socrates-derived chapter format, with the same system
sans-serif as the rest of the site. No serif theme, custom writing layout, or
article-specific font, chapter numbering, callout style, or metadata placement.
Use Markdown H2 headings; the shared renderer generates numbered chapters and
uses one horizontally centered column capped at `--copy: 640px` for every
chapter. Keep prose left-aligned; place diagrams and tables after it at every
width. Endnotes and the article footer align to the same column. Preserve DOM
order, responsive gutters, and readable enlarged text.
Keep full-text RSS and one document-wide footnote collection. See STYLE.md.
Viewrule is the sole essay geometry detector. Before changing UI, build the site
and run `python3 scripts/viewrule.py contract`; read `.ui-review/rules.json` and
STYLE.md. Keep expectations independent of the CSS under test. Update the rules,
their explanation, and shared CSS together for intentional changes. Run
`python3 scripts/viewrule.py check` against the production preview and inspect
native-scale detail tiles, including 4K, print, and enlarged-text captures.
New measurements and their regression coverage belong in the Viewrule repository;
do not recreate a Python chapter detector or another local layout suite. Keep
functional browser checks for navigation, citations, RSS, and progressive behavior.
Use only the user's actual feedback when recording adjustment or approval; a
passing check is not design approval. See docs/viewrule.md for commands and limits.
