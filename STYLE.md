# Style

This document defines the shared visual language of the site. `WRITING.md` governs how ideas are expressed; this file governs how they are presented.

All essays use the shared Socrates-derived format: the site system sans-serif, numbered chapters, accent callouts, and responsive diagram panels. The home and work pages keep their own layouts. Essays do not have separate visual identities.

When a new page needs a new treatment, extend the system deliberately. Do not create a one-off visual language for the page.

## Principles

1. **Content establishes hierarchy.** Typography, spacing, rules, and layout should make structure visible without decorating it.
2. **One essay format.** Share typography, chapter hierarchy, callouts, diagrams, and article chrome across the complete writing corpus.
3. **Restraint is the default.** The dark field, muted copy, pale green accent, thin rules, and generous whitespace already provide identity. Add another treatment only when it carries meaning.
4. **Mobile is a first-class composition.** Responsive work is not shrinking the desktop layout. Important relationships must remain legible and intentional at phone widths.
5. **Accessibility is part of the design.** Keyboard targets, focus states, readable contrast, semantic structure, and non-color cues are invariants.
6. **Presentation should survive the content.** A longer title, denser paragraph, extra citation, or narrower viewport must not produce clipping, overlap, or horizontal overflow.

## Canonical tokens

The canonical site tokens currently live in `assets/css/site.css`:

```css
:root {
  --bg: #0d1513;
  --text: #eef1ee;
  --muted: #afbbb4;
  --accent: #acc8b7;
  --line: #2b3a34;
  --max: 1120px;
  --copy: 680px;
}
```

Use these variables rather than introducing nearby colors or widths locally. A specialized component may need an additional surface or interaction color, but it should derive from the same palette and be reusable if the pattern recurs.

Do not introduce a second accent color for an individual article.

## Typography

The site uses the system sans-serif stack. Do not add a display face or article-specific font without changing the site-wide design system.

The hierarchy is intentionally modest:

- body copy is approximately `1rem–1.05rem`, with generous line height;
- article copy uses `1.8` line height;
- article titles scale responsively and use tighter tracking;
- section headings are materially smaller than article titles;
- eyebrows and metadata use small type, muted or accent color, and restrained uppercase tracking.

Use weight and size before introducing boxes, fills, or ornaments.

Avoid excessive typographic emphasis inside prose. Bold, blockquotes, code, and callouts all compete for attention; they should not become the normal appearance of a paragraph.

## Measure and layout

Every essay shares one responsive column system for its opening and chapters.
When the essay container has at least 64rem of readable width, use two equal
columns with a 48px gutter: prose on the left and supporting visuals on the right.
The 1240px essay shell caps each column at 596px. Chapters without a supporting
visual keep their heading and prose in that same left column; do not center them
or add illustrations merely to fill the other column. Endnotes and the footer
align with the prose column.

Below that threshold, and with enlarged text or print, use one centered reading
column capped at 640px. Container queries use rem units so enlarged text triggers
the same reflow. Keep headings before prose and figures after prose in DOM order;
stack opening art and supporting diagrams below their prose at narrow widths.
Opening diagrams reflow into readable labeled nodes on phones; illustrations
retain their aspect ratio. Keep text left-aligned and preserve natural word spacing.
Never split running paragraphs into newspaper columns or shrink text to fit.

The general site shell is capped at `--max: 1120px`; essays use the shared 1240px
shell. Titles and descriptions span the essay opening above the copy and art.
The same subject symbol from the homepage/archive sits beside each essay title
(40px desktop, 32px phone). Use the shared partial and symbol mapping, with no
per-article copies of the SVG. Keep its decorative semantics and the title's
accessible name. Printed essays omit this decorative symbol.

The homepage keeps the compact introduction above a two-column destination grid:
Writing on the left and Labs on the right. Each column needs at least 24rem, with a
48px gutter; narrow screens and enlarged text stack Writing before Labs. Keep the
latest three essays, reading times, archive and RSS links. Labs uses concise previews
of the existing experiments with explicit prototype/demonstration status and links
to their explanatory sections. Career context follows both destinations.

The Writing archive uses the full site shell, with its heading and introduction
aligned to the navigation and footer left edge. The introduction keeps the 680px
copy cap. Essays form two equal columns with a 48px gutter when each can be at
least 24rem wide; otherwise they form one full-width column. The shell cap prevents
a third column. Preserve newest-first DOM order, flowing left to right across each
row. At 200% root text, the archive returns to one column. Keep titles and descriptions
together and let rows grow with their content. Do not center the archive as an essay.

Whitespace should separate ideas before borders or containers do. Prefer vertical rhythm to card proliferation.

## Article chrome

Every essay uses `layouts/writing/single.html`, `layouts/partials/essay-content.html`, and `assets/css/essays.css`. No article-specific layout or stylesheet.

- Writing link and calculated reading time appear above the title. Dates stay in metadata and RSS only.
- The title and description span the full essay width above the opening columns. The accent callout and opening prose sit beside the relevant visual beneath them. The first introductory blockquote becomes the opening callout without duplicating it; RSS keeps the authored order. Use `essay_visual` for a shared vector diagram or `essay_image` for an existing illustration. Large illustrations fade into the background; opening visuals stack below prose on phones. Print omits opening art.
- Every Markdown H2 starts a chapter with a generated two-digit number, short accent rule, common heading size, and thin divider. H3 is an unnumbered subsection.
- Chapters share the responsive columns described above. Headings precede prose; diagrams and tables follow it in DOM order and appear beside it on wide screens. Heading and spacing treatments stay shared.
- All essays share the same archive/feed footer and citation behavior.

Chapter numbers come from heading order, not handwritten numbers. Do not independently opt articles into a different contents menu, heading treatment, or metadata position.

## Work icons

Use actual company logos beside company headings and career entries, consistently
fitted inside 36px circular frames with 5px padding and a white interior. Preserve
each logo's proportions and brand colors. Bundle the assets locally; do not use
stock icons, redraw logos, tint them to match the site, or hotlink remote favicons.
Use a company's standalone brand mark when available, and its real wordmark
otherwise. Sources and extraction notes live in `static/logos/companies/README.md`.

Open-source project headings use locally bundled GitHub owner or organization
avatars in the same 36px circular badge, with the same 5px padding and 12px gap.
The shared `.work-logo` class keeps both treatments consistent. Keep project names
beside the decorative avatars and align descriptions beneath the names. Avatar
sources live in `static/logos/projects/README.md`.

Speaking engagements use the same badge and alignment, with an official event
icon beside the conference name and the talk details beneath it. Keep the event
assets local and document sources in `static/logos/events/README.md`.

Work uses one combined career narrative from `data/career.yaml`, not separate
descriptions and chronology. Group actual job titles under one employer logo,
with newest roles first and a thin vertical path connecting small role markers.
Place descriptions under the roles they describe; retain company-wide context
at company level rather than assigning it to an unverified role or date range.
Dates belong below each role; employer tenure belongs below the company name.
Keep unknown promotion dates unspecified rather than estimating them.

## Links

Links use the accent color with a thin underline where needed for legibility. Hover may move toward the primary text color.

Do not invent article-specific link colors or animated treatments.

Navigation uses Writing, Labs, Open source, Work, and About in that order.
At 700px and below, show icons with accessible names; above that, show icons and
labels. Keep 44px targets and mark the current destination with a short underline.
Labs holds experiments with explicit prototype status and limitations. Open source
includes maintained tools, dotfiles, activity, and upstream contributions, separate
from career history. Activity is a dated public GitHub calendar snapshot, not a
measure of impact; show the last 13 weeks on phones and the full year on desktop.

## Citations

Citations are contextual, not ornamental.

The preferred article treatment is the existing subtle underline on the exact phrase or claim related to the source. Do not underline an entire paragraph when a phrase is sufficient. Do not restore large numeric footnote markers as the primary interaction.

Citation interaction may reveal richer source detail, but the prose must remain readable without opening it. The fallback footnotes must remain available for non-interactive and print contexts. Endnotes align with the chapter prose column, including when it centers in narrow layouts and print. Keep each source together.

Citation styling must not make sourced prose visually louder than the argument itself.

## Blockquotes and callouts

Use the Socrates treatment everywhere: a four-pixel accent rule, the common dark surface, shared padding, and normal system sans-serif text. No serif or italic article theme.

Ordinary Markdown blockquotes use this treatment. Use them for a quotation or a central question or proposition worth returning to. Each developed essay should have a clear visual pause, usually in its opening or at a consequential decision. Do not manufacture a maxim or repeat prose just to fill a box.

An optional `callout` front-matter field supports the opening treatment. Prefer a blockquote in the body when the passage belongs in the argument and full-text RSS.

## Diagrams

Diagrams exist to carry information that prose communicates less efficiently: loops, dependencies, sequences, comparisons, state changes, and layered structures.

All diagrams should:

- use the common palette and typography;
- fit within the available width at every supported viewport;
- avoid tiny labels that require zooming;
- preserve alignment and hierarchy when text wraps;
- use borders, arrows, spacing, and accent bars consistently;
- include an accessible label or equivalent textual explanation;
- avoid decorative complexity that does not encode information.

A diagram may be visually distinctive. It should not look imported from another brand.

Prefer CSS/HTML diagrams when they need to reflow with content. Prefer static images only when the visual cannot reasonably be represented responsively in the site system.

## Accent bars and rules

The accent color can mark hierarchy or direction, especially in diagrams and designed essays. Use it sparingly.

Thin `--line` rules are the default separator between structural regions. Accent rules indicate emphasis or semantic relationship; they should not replace ordinary separators everywhere.

Repeated accent bars should share width, thickness, spacing, and alignment within a composition.

## Images and portraits

Portraits are circular throughout the site. Preserve the source image's aspect ratio and use `object-fit: cover` for circular framing.

Do not allow important facial content to be clipped by a responsive crop. Verify portrait composition at desktop and phone widths.

Article images should preserve intrinsic aspect ratio, stay within their container, and include captions when context is not obvious from the surrounding prose.

## Code and tables

Inline code uses the shared dark surface and compact padding. Code blocks use the same surface with a thin site rule and horizontal scrolling when required.

Chapter tables follow the prose in DOM order alongside other supporting visuals, using the right column on wide screens and stacking below prose at narrow widths. They remain inline in full-text RSS. Tables may scroll horizontally on narrow screens. Do not shrink table text until it becomes unreadable merely to avoid scrolling.

Do not introduce syntax or table colors that compete with the site's accent unless a site-wide syntax system is adopted.

## Responsive behavior

The primary verification widths are desktop, tablet, ordinary phone, and narrow phone. The existing CSS uses breakpoints around 1000px, 700px, 600/560px, and 360px; new components should work with that responsive model rather than accumulating arbitrary nearby breakpoints.

At every supported width:

- no horizontal page overflow;
- no clipped text or controls;
- no overlapping labels, diagrams, or navigation;
- minimum interactive targets remain approximately 44px;
- reading order remains sensible when columns collapse;
- diagrams remain understandable without pinch zoom;
- headings wrap naturally;
- long URLs and code cannot force the page wider;
- the first mobile viewport should have an intentional hierarchy rather than a cropped desktop composition.

Prefer reflow over scale-down.

## Interaction and accessibility

Keyboard focus uses the shared accent outline and must remain visible.

Interactive behavior must not depend on hover alone. Citation popovers, disclosure elements, navigation, and any future controls need keyboard and touch behavior.

Color cannot be the only indicator of state. Current navigation uses an underline; citation relationships use underline changes in addition to color.

Respect semantic HTML before adding ARIA. Motion should be unnecessary to understand the interface.

## One format across essays

Socrates supplies the chapter and diagram composition; the rest of the site supplies the font and palette. Socrates itself follows the same template as every other essay.

Allowed differences are content-driven: chapter count, diagram topology, an existing relevant illustration, and the length of the argument. Font, heading size, numbering, callout treatment, spacing, and article chrome are shared.

A new diagram may need its own geometry, but it must use the shared panel, node, label, caption, and responsive conventions. Improve the shared components instead of introducing page-specific CSS.

## Avoid visual drift

Watch for these failure modes across the corpus:

- slightly different greens introduced by individual components;
- arbitrary border radii;
- several versions of the same callout;
- inconsistent article widths;
- headings with different spacing for no semantic reason;
- one-off mobile breakpoints fixing symptoms rather than layout;
- diagrams with unrelated arrow, label, or border conventions;
- dates or metadata competing with titles;
- citation treatments changing between articles;
- decorative cards accumulating because an article feels visually sparse.

The answer to visual monotony is better composition, not more component types.

## Implementation rules

1. Reuse CSS custom properties from the shared system.
2. Prefer shared classes and semantic components to page-specific selectors.
3. Keep essay layout in the shared stylesheet. Content-specific diagram geometry may vary, but must reuse the shared visual conventions.
4. Do not solve overflow with `overflow: hidden` on a parent when content should reflow.
5. Do not use fixed heights for text-bearing components unless the content is strictly bounded.
6. Avoid absolute positioning for relationships that need to survive text wrapping.
7. Test real content, not placeholder strings.
8. Preserve print fallbacks for reading content and citations.
9. Keep JavaScript progressive: the underlying content must remain usable if enhancement fails.
10. Treat visual verification as part of implementation, not a final polish pass.

## Enforcing the essay standard

[Viewrule](https://github.com/lanej/viewrule) owns the essay detector. The executable
contract is `.ui-review/rules.json`; `.ui-review/site.json` declares capture settings.
The shared CSS implements the layout independently. Expected geometry never comes
from the stylesheet being checked.

| Standard | Viewrule rule |
| --- | --- |
| Homepage Writing and Labs share a row and shell edges on wide screens; stack in that order on phones and enlarged text, with Work below both | `home-destination-first-row`, `home-destination-left-edge`, `home-destination-right-edge`, `home-destinations-no-overlap`, `home-destinations-phone-order`, `home-destinations-enlarged-order`, `home-work-follows-destinations` |
| Writing archive heading, introduction, and left-column entries share the shell left edge within 2px | `writing-index-shell-alignment` (`align`) |
| Two archive columns on wide screens, one at narrow widths or enlarged text; entries remain separate and read across rows | `writing-grid-right-edge`, `writing-grid-first-row`, `writing-grid-no-overlap`, `writing-grid-phone-column`, `writing-grid-enlarged-column`, `writing-grid-reading-order` |
| Fill the centered 640px column when stacked; align all wide-screen prose columns | `essay-reading-measure`, `essay-reading-measure-print-enlarged`, `essay-wide-prose-left`, `essay-wide-prose-right`, `essay-wide-support-right`, `essay-wide-columns`, `essay-prose-local-measure` |
| Heading before prose; supporting visuals alongside on wide screens and after prose when stacked | `essay-chapter-order`, `essay-support-order-narrow`, `essay-support-order-print-enlarged`, `essay-support-columns-no-overlap` |
| Every authored chapter and visual container remains visible | `essay-chapters-visible`, `essay-visuals-visible` (`vertical-order`) |
| Opening visuals follow prose when stacked and stay separate on wide screens; title icons remain visible | `essay-opening-order-narrow`, `essay-opening-order-enlarged`, `essay-opening-no-overlap`, `essay-title-icon-present` |
| Sequential paragraphs without overlap or rearrangement | `essay-paragraph-order` (`vertical-order`) |
| Left-aligned prose in one column | `essay-prose-alignment`, `essay-prose-direction`, `essay-prose-columns` (`style`) |
| Text components do not truncate their own content | `site-text-not-clipped` (`no-clip`) |
| Visible captions on shared diagrams | `site-diagram-context` (`context`) |
| At least 16px home introduction text | `site-introduction-text` (`min-font-size`) |
| Page overflow and confirmed WCAG A/AA accessibility violations, including text contrast | Built-in Viewrule checks |

The English essay corpus uses left-to-right text. The direction rule makes CSS
`text-align: start` equivalent to physical left alignment; right, center, and
justified prose fail. Print uses dark text on light surfaces through the shared
print tokens, including code, tables, and diagram labels.

Every selected essay runs at 320, 390, 768, 961, 1100, 1440, and 3840 CSS pixels.
Every essay also runs at 1440px in print media and at 200% root text. When selected, the homepage and Writing archive run at all seven widths, plus 200%
root text at 320, 390, and 1440px. Other pages run at mobile, desktop, and 4K widths (404 at
mobile and desktop). Change builds select affected routes; scheduled/manual audits
cover all pages. Selection never removes states from an affected route. Full-page captures include overlapping native-scale details;
incomplete coverage fails rather than passing a resized overview.

Essay selectors are optional on non-essay pages. Each essay's required readiness
selector includes `.sc-article .sc-section`, and required chapter order groups
ensure prose and headings cannot silently disappear. Supporting visuals remain
optional in text-only chapters, which retain the shared prose alignment. Full-text RSS, chapter numbering, citation behavior,
and other functional checks remain in the website workflow.

Run the commands in [Viewrule integration](docs/viewrule.md). The previous Python
chapter detector and its regression were removed; the installed Viewrule workflow
now owns their readable, broken, and document/CSS mismatch cases. Extend that
engine when a new measurement is needed rather than adding a local detector.

An intended change to the measure updates the relevant rule, this explanation,
and the shared CSS together, with current previews for review. A passing geometry
check does not establish comfortable line length for every platform font or prove
that a diagram supports an argument. Contrast cases axe cannot resolve remain
explicit manual-review items.

## Visual review

Before publishing or changing a shared component:

1. Render the affected page at desktop and phone widths.
2. Check the first viewport independently; it establishes the page hierarchy.
3. Scan the full page for horizontal overflow, clipping, alignment drift, and accidental density changes.
4. Check headings with wrapping and long links.
5. Inspect every diagram at the narrowest supported width.
6. Verify keyboard focus and touch targets.
7. Exercise citation and disclosure interactions.
8. Compare the page beside Socrates and one other essay. Typography and chapter treatments must match.
9. Ask whether any new visual treatment encodes meaning or merely adds novelty.
10. If a one-off fix appears likely to recur, move the rule into the common system before publishing.

## Corpus-level review

Periodically inspect several pages together rather than reviewing each in isolation.

The site should exhibit stable answers to these questions:

- What color means emphasis?
- What does a link look like?
- How wide is readable prose?
- How are sections separated?
- How are sources indicated?
- How does a diagram label hierarchy?
- What happens when a layout reaches phone width?
- Which treatments are semantic, and which are merely compositional?

If two pages answer one of these differently without a content-driven reason, that is drift.

## Relationship to `WRITING.md`

`WRITING.md` lets the argument determine the number and substance of the chapters. It does not authorize different visual formats.

The combined rule is:

> **One reading format. Different arguments.**

Readers should recognize the site before they recognize the template.

## Discovery item visuals

Home Writing and Labs items and the Writing archive use a 32px subject symbol
beside the title with a 10px gap. Descriptions use the full item width below that
heading; the icon must not reserve a column beside the paragraph. Keep homepage
titles at 1.6rem (1.5rem on phones), preserving the body text scale. Reading time
and experiment status follow the description inline, separated by a muted dot.
Use 18px vertical item padding (16px on phones) and 8px before archive links.
At the configured desktop and 4K normal-text sizes, keep all three essay titles
and both Labs titles visible in the first viewport; enlarged text reflows freely.

Use shared, label-free symbols with consistent line weight and the site accent.
At this small size, judgment and inquiry symbols identify the Damocles and Socrates
essays; their existing illustrations remain in the article openings. Labs symbols
represent the route experiment and layout demonstration, not invented project logos.
Adjacent titles supply accessible context; symbols are decorative. New essays
fall back to a document symbol.

The homepage portrait sits to the left of the name and role. On desktop it spans
the identity and introduction rows; on phones the introduction spans the full
width below portrait and name. Keep the portrait first in the source order.
