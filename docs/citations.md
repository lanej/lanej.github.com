# Citations in every article

Write ordinary Markdown footnotes. The shared article head automatically adds
in-place source cards to every present and future writing page with footnotes.
There is no front-matter flag, plugin, build dependency, or per-post script.
Pages without footnotes do not load the enhancement.

```markdown
A supported claim.[^source]

[^source]: **[Work title](https://example.com/paper)**  
    Author Name · 2026

    Explain what the work supports and any important qualification.
    [Another relevant source](https://example.com/other) can be included.
```

The bold linked title becomes the card heading; author/year remains below it.
Older prose-format footnotes work too. Their heading uses an existing emphasized
title or source-link label, and the complete original note is preserved below.
No author, year, title, source, or summary is inferred or fetched remotely. Do not
invent a year for an undated document. Link named works naturally in the article
body too when that helps the argument. Footnotes are for source context, not a
reason to make every ordinary link interactive.

## Citation scope in the prose

Enhanced articles do not show numbered citation badges. Instead, the prose supported
by the note gets a subtle underline and becomes the tap/click target for the same
source card.

The supported range is mechanical and author-controlled: within a paragraph or
other text block, a footnote marker applies to the text since the previous footnote
marker in that block, or from the start of the block when it is the first marker.
Place the marker immediately after the complete passage the source supports.
Multiple markers in one paragraph therefore divide that paragraph into independently
cited passages.

```markdown
Dan North's *Deliberate Discovery* makes this distinction useful for engineering.
Identify the ignorance constraining progress, then deliberately reduce it enough
to proceed.[^north] Eric Ries centers validated learning, not merely shipping a
smaller product.[^ries]
```

In the enhanced article, the Dan North passage and Eric Ries passage are separately
underlined. In static HTML, print, RSS, unsupported browsers, or with JavaScript
blocked, the original numbered footnote markers remain the fallback.

## Reader behavior

- Click/tap the underlined supported passage. Keyboard users focus the associated
  source control and press Enter/Space. Desktop cards appear near the passage;
  phone cards stay inside the visible screen. Opening a card does not change the
  URL fragment or scroll away from the passage.
- Escape, the close button, or a click outside dismisses it. Keyboard/close-button
  dismissal returns focus to the source control that opened it, including repeated
  cites.
- Every source link and qualification stays available. Long notes scroll inside
  the card. “Full reference” deliberately follows the original endnote link.
- Endnotes and return links remain in the delivered HTML. With no JavaScript,
  blocked assets, or no native Popover API, they work as normal anchors. Print and
  full-text RSS use ordinary references, never duplicate interactive cards.

## Implementation and regression checks

`layouts/partials/citation-assets.html` loads fingerprinted native CSS and one
small deferred JavaScript file only on articles with notes. The script enhances
Hugo's rendered footnotes; Markdown remains the single source of citation text.
Native `popover="auto"` supplies non-modal behavior and keyboard/light dismissal.
No third-party library, network lookup, analytics, or hover-only interaction.

`check.py` allows only this specifically identified executable script, verifies
its local URL/integrity, and checks that RSS retains every reference without
interactive markup. `citation_checks.py`, called by the normal local and live
browser checks, covers every article plus disposable future-writing fixtures:
repeated notes, structured source metadata, plain notes, multiple sources, long
content, fragment IDs, missing-target fallbacks, idempotent enhancement, keyboard
and touch use, print, unsupported-browser/no-JavaScript behavior, and 200% text.
Inspect citation screenshots from the actual lanej.io deployment before calling
a change verified. These checks run for new articles automatically.

Reference: [MDN: Using the Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API/Using).
