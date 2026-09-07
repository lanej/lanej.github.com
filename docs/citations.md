# Citations in every article

Write ordinary Markdown footnotes. The shared article head automatically adds
in-place source cards to every present and future writing page with footnotes.
There is no front-matter flag, plugin, build dependency, or per-post script.
Pages without footnotes do not load the enhancement.

```markdown
Dan North's *Deliberate Discovery* motivates this claim.[^north]

[^north]: **[Introducing Deliberate Discovery](https://dannorth.net/blog/introducing-deliberate-discovery/)**  
    Dan North · 2010

    Explain what the work supports and any important qualification.
```

## Keep the citation label short

Underline a source title, author, or brief phrase, **never a whole paragraph or
sentence**. The label is a way to open the source card, not a highlight of every
word the evidence supports. Keep the marker after the complete supported claim.

The shared renderer searches only the current passage before that marker (and
since the preceding marker in the same paragraph). It prefers a short work title
already named in the prose, then a matching author from the note's author/year
line. For unstructured notes it uses up to four trailing words. All selections
are capped at six words and 64 characters. Thus *Deliberate Discovery*, Eric Ries,
and Wes Kao can each be small triggers within one otherwise ordinary paragraph.

Name a work naturally in the prose when possible and give its title in the note.
An italicized title can match part of a longer source title. Names and titles are
matched from authored text only; metadata is never inferred or fetched remotely.
Do not invent a year for an undated document. Older prose notes still work.

Ordinary links remain ordinary links, not nested citation controls. When there
is no safe text span (for example, adjacent notes or a passage consisting only of
a link), a small underlined “source” label opens the card instead. No numbered
boxes, enlarged controls, or paragraph-wide underlines are introduced.

The bold linked title becomes the card heading; author/year remains below it.
The complete original note, including every qualification and source, is retained.

## Reader behavior

- Click/tap the underlined phrase, or reach its control with Tab and press
  Enter/Space. Desktop cards appear nearby; phone cards stay inside the screen.
  Opening a card does not change the URL fragment or scroll away from the passage.
- Escape, the close button, or a click outside dismisses it. Keyboard/close-button
  dismissal returns focus to the actual reference, including repeated citations.
- Long notes scroll inside the card. “Full reference” deliberately follows the
  original endnote link. The underlined phrase does not alter the evidence scope.
- Endnotes and return links remain in delivered HTML. Without JavaScript, styles,
  or native popovers, they work as normal anchors. Print and full-text RSS retain
  ordinary references, not interactive cards or duplicated citation text.

## Implementation and regression checks

`layouts/partials/citation-assets.html` loads fingerprinted native CSS and one
small deferred JavaScript file only on articles with notes. The script enhances
Hugo's rendered footnotes; Markdown remains the single source of citation text.
There is no third-party library, network lookup, analytics, or hover-only action.

`check.py` checks static output, script integrity, and complete RSS references.
`citation_checks.py` exercises all article cards, keyboard/touch interactions,
repeated references, metadata, long notes, IDs, fallbacks, and enlarged text.
`test-citation-phrases.py`, run by the build, separately proves that long passages
produce short labels, the exact multi-source example retains its text and styling,
and ordinary links and adjacent references remain usable. It also checks phrase
length and unmodified prose across every built article, including future writing.
Inspect both closed-state text and open cards from the actual lanej.io deployment.

Reference: [MDN: Using the Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API/Using).
