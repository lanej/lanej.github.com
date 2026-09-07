# Style

This document defines the shared visual language of the site. `WRITING.md` governs how ideas are expressed; this file governs how they are presented.

The objective is consistency without sameness. A conventional essay, a visual essay such as Socrates, a work page, and the home page may use different compositions. They should still look like parts of one system.

When a new page needs a new treatment, extend the system deliberately. Do not create a one-off visual language for the page.

## Principles

1. **Content establishes hierarchy.** Typography, spacing, rules, and layout should make structure visible without decorating it.
2. **One site, several compositions.** Reuse tokens and primitives while allowing page-specific arrangements.
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

- body copy is approximately `1rem–1.0625rem`, with generous line height;
- article copy uses `1.8` line height;
- article titles scale responsively and use tighter tracking;
- section headings are materially smaller than article titles;
- eyebrows and metadata use small type, muted or accent color, and restrained uppercase tracking.

Use weight and size before introducing boxes, fills, or ornaments.

Avoid excessive typographic emphasis inside prose. Bold, blockquotes, code, and callouts all compete for attention; they should not become the normal appearance of a paragraph.

## Measure and layout

Long-form reading width is `--copy: 680px`. Treat that as an invariant for ordinary prose.

The general site shell is capped at `--max: 1120px` with responsive side gutters. Pages may use the additional width for navigation, portraits, diagrams, indexes, or supporting material, but ordinary paragraph text should not expand to fill it.

Whitespace should separate ideas before borders or containers do. Prefer vertical rhythm to card proliferation.

A specialized article may break out of the reading column for a diagram or composition when the wider space improves comprehension. The prose before and after should return to the common measure.

## Article chrome

Ordinary writing pages share:

- the global header and footer;
- a constrained reading column;
- article title, description, and subdued metadata;
- consistent heading hierarchy;
- common link, code, table, blockquote, figure, citation, and footnote treatments;
- the common article footer and pager where applicable.

Article metadata is supporting information, not the visual lead. Titles and descriptions should dominate dates and modification information.

A custom layout such as Socrates may change the interior composition, but should retain the site's palette, typography family, navigation, interaction behavior, responsive discipline, and basic spacing logic.

## Links

Links use the accent color with a thin underline where needed for legibility. Hover may move toward the primary text color.

Do not invent article-specific link colors or animated treatments.

Navigation links are quieter than prose links and use current-page underlining rather than a filled active state.

## Citations

Citations are contextual, not ornamental.

The preferred article treatment is the existing subtle underline on the exact phrase or claim related to the source. Do not underline an entire paragraph when a phrase is sufficient. Do not restore large numeric footnote markers as the primary interaction.

Citation interaction may reveal richer source detail, but the prose must remain readable without opening it. The fallback footnotes must remain available for non-interactive and print contexts.

Citation styling must not make sourced prose visually louder than the argument itself.

## Blockquotes and callouts

The standard blockquote is a simple accent rule at the left with indented text. Use it for quotations and the small number of propositions that deserve interruption of the normal reading rhythm.

Do not create a new card style for each kind of thought.

If a recurring semantic callout becomes necessary, define one reusable component and document its meaning. Visual distinction should correspond to a real semantic distinction.

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

Tables may scroll horizontally on narrow screens. Do not shrink table text until it becomes unreadable merely to avoid scrolling.

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

## Special layouts

Special layouts are allowed when the material benefits from them. Socrates is the current example.

A special layout may vary:

- section composition;
- numbering;
- diagram placement;
- column relationships;
- local rhythm;
- use of kickers or structured labels.

It may not casually vary:

- site palette;
- font family;
- navigation and footer identity;
- link behavior;
- accessibility conventions;
- responsive quality;
- citation semantics;
- basic visual density.

Before adding a page-specific CSS file, ask whether the requirement is actually a reusable site primitive. If it is, implement it in the common system instead.

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
3. Keep article-specific CSS scoped and small; promote repeated patterns into shared CSS.
4. Do not solve overflow with `overflow: hidden` on a parent when content should reflow.
5. Do not use fixed heights for text-bearing components unless the content is strictly bounded.
6. Avoid absolute positioning for relationships that need to survive text wrapping.
7. Test real content, not placeholder strings.
8. Preserve print fallbacks for reading content and citations.
9. Keep JavaScript progressive: the underlying content must remain usable if enhancement fails.
10. Treat visual verification as part of implementation, not a final polish pass.

## Visual review

Before publishing or changing a shared component:

1. Render the affected page at desktop and phone widths.
2. Check the first viewport independently; it establishes the page hierarchy.
3. Scan the full page for horizontal overflow, clipping, alignment drift, and accidental density changes.
4. Check headings with wrapping and long links.
5. Inspect every diagram at the narrowest supported width.
6. Verify keyboard focus and touch targets.
7. Exercise citation and disclosure interactions.
8. Compare the page beside at least one ordinary essay and one special layout.
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

`WRITING.md` intentionally asks article structures and rhetorical cadence to vary. This guide intentionally constrains the visual vocabulary.

The combined rule is:

> **Standardize the system. Vary the composition.**

Readers should recognize the site before they recognize the template.