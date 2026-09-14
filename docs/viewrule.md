# Viewrule integration

[Viewrule](https://github.com/lanej/viewrule) is the site's essay layout and
accessibility checker. Its shared engine replaces the former Python chapter
detector. This repository owns the application-specific boundaries and copy;
Viewrule owns browser measurements, rule validation, reports, and detector
regressions. Nothing is added to the visitor's JavaScript or published Hugo assets.

## Use it

Install the existing Python/Hugo verification tools from the README and Node 22+:

```sh
bash scripts/install-viewrule.sh
bash scripts/build.sh
python3 scripts/viewrule.py contract
python3 -m http.server 8765 --bind 127.0.0.1 --directory public
```

In another terminal, from the same checkout:

```sh
# One-time browser installation, or set VIEWRULE_BROWSER_PATH to existing Chromium.
python3 scripts/viewrule.py install-browser
# Default: changes since the branch's merge base with origin/master, including local edits.
python3 scripts/viewrule.py check
# Explicit comparison or full audit:
python3 scripts/viewrule.py check --base COMMIT
python3 scripts/viewrule.py check --all
# Optional preview URL override:
python3 scripts/viewrule.py check --url http://127.0.0.1:8873
```

Rebuild after changing source and rerun the check against that build. The command
prints the selected routes and HTML/JSON report paths. Affected-page reports live
under `.ui-review/affected/.ui-review/runs/`; full audits use `.ui-review/runs/`. Inspect the overview
for composition and native-scale tiles for text and diagram detail. At 4K, a reduced
full-page image alone is insufficient evidence. Failed rules and incomplete captures
exit 1; invalid setup exits 2. CI runs this command in the existing build job against
the same `public/` artifact that can deploy, using the runner's Chrome binary.
Reports are retained in `preflight-verification`, including when the check fails.

## Selecting affected pages

PR builds compare the tested checkout with the PR base commit. Push builds use the
pre-push commit, so a multi-commit push includes every change. Local checks default
to the merge base with `origin/master`, including staged, unstaged, untracked,
deleted, and renamed files. An invalid/missing baseline fails setup; an initial
push with the all-zero before SHA checks everything. Scheduled and manually
dispatched workflows run full audits, as does `check --all`.

`scripts/affected_pages.py` is shared by the visual suite and PR previews. Direct
page templates select their routes; article edits also select Home and Writing;
Labs content selects Home and Labs. Targeted edits in shared CSS are parsed with
pinned tinycss2: changed rules, media contexts, and cascade order are compared,
then required class/id anchors are matched to built HTML. Global or unanchored
selectors, imports, fonts, runtime-only classes, and unknown shared dependencies
conservatively select all pages. This is dependency selection, not a geometry check.

Changed Viewrule rules select both their old and new page scopes; unscoped required rules
select everything. Optional rules with explicit class/id selectors select their
built-page consumers; selectors that cannot be resolved still select everything. Viewport/capture configuration changes are global, while source
path bookkeeping and documentation-only changes do not change rendered pages.
Every selected route retains all its configured widths, print states, and enlarged
text states. We reduce pages, never the coverage within an affected page.

`viewrule.py select` writes `.ui-review/selection.json` with the baseline, changed
files, routes, page states, and viewport count. CI uses that same list for functional
browser screenshots and PR previews. No affected pages produces an explicit skip,
without launching a capture browser. Build, links, image hashes, RSS/source checks,
and the shared citation fixture tests still run.

The full canonical contract is validated before selection so invalid rules cannot
be hidden by filtering. The wrapper copies in-scope source files into a generated
project and filters only its rule copy to selected page names. Versioned rules are
never rewritten. The native engine fingerprints the snapshot; each run rebuilds it
and removes deleted source files. Reports and selection evidence are retained in
the workflow artifact. `contract` and rule-authoring commands still use the full
canonical project by default.

## Contract and coverage

`.ui-review/site.json` contains URL, viewport, capture, and freshness settings.
`scripts/viewrule.py` discovers all built pages, gives essays a required chapter
readiness selector, and writes the ignored native `.ui-review/config.json`.
It adds desktop print and 200% root-text states for every essay.
When selected, the homepage and Writing archive run at all seven configured widths and at 200%
root text on narrow phone, ordinary phone, and desktop. The homepage rules protect
Writing/Labs placement, stacking order, and Work below both sections.
The archive’s `writing-index-shell-alignment`
rule compares the heading, introduction, grid, and left-column entries with the
navigation/footer left edge (2px tolerance), independently of CSS margins. The
archive grid rules check the second column against the right shell edge, the two
newest essays sharing the first row, non-overlap, row-wise reading order, and a
full-width single column at narrow sizes and enlarged text.
`.ui-review/rules.json` is the versioned native rule file; rule-authoring commands
write directly to it. No wrapper implements browser measurements.

[STYLE.md](../STYLE.md#enforcing-the-essay-standard) maps each rule to the design
requirement and documents viewport coverage. Viewrule checks bounded reading measure, consistent wide-screen prose columns,
centered stacked layouts, DOM/visual order, prose alignment, text clipping, diagram
captions, introduction text size, page overflow, and axe WCAG A/AA findings including
confirmed text contrast. Optional essay selectors allow other page types; required
readiness and chapter groups prevent absent essay structure from silently passing.
Required order groups also reject partially hidden content; authored chapters,
paragraphs, and visual containers cannot disappear merely to fit the layout.

The wrapper isolates shared user configuration under `.tools/viewrule-global` so
personal dashboard density rules do not change the site's CI contract. Put the
site's accepted preferences in its versioned rules. Stop enforcement stays off;
CI supplies the enforcement gate. A required status check in repository branch
protection is a separate repository setting.

Functional browser checks remain responsible for navigation, citations, chapter
numbering, image behavior, print fallbacks, and RSS. Detector regressions moved to
Viewrule's existing installed-CLI workflow; do not restore a parallel site detector.
No area-occupancy quota applies to essays: whitespace outside the reading column
is intentional. Geometry cannot prove readability for every font or the relevance
of a diagram. Inspect inconclusive axe results manually; no automatic source
repair or fabricated approval occurs.

## Feedback and changes

Before an agent changes UI, run `contract` and read STYLE.md. After a change, rebuild,
run `check`, and review the actual report. For the canonical feedback/learning
workflow below, use `check --all` and record the user's words against that full
project report (affected-page reports belong to the generated scoped project):

```sh
python3 scripts/viewrule.py feedback --report .ui-review/runs/RUN/report.json \
  --decision adjust --note 'The introduction is too small on my phone.'
# Author a concrete replacement rule, using the returned feedback ID:
python3 scripts/viewrule.py learn --feedback FEEDBACK_ID --rule /tmp/intro-rule.json
```

Use `--decision approve` only when the user approves that exact report. Feedback
is recorded in `.ui-review/feedback.jsonl`; review it before committing. Captures
and approved image references remain ignored, like existing preview artifacts.
Rule changes are ordinary reviewable diffs; the report also shows contract changes.
Intended measure changes update the rule, STYLE.md, and shared CSS together.

## Upgrade or remove

`scripts/install-viewrule.sh` pins a versioned release archive and SHA-256, installs
it under `.tools/`, and disables package lifecycle scripts. The archive includes
its dependency shrinkwrap. Update the version and checksum together from a tested
Viewrule release; never use an unversioned latest URL. Reinstall and rerun the same
workflow after upgrading. Restore the prior pin to roll back.

Removing the integration removes the build step, wrapper, installer, and rules;
it does not require changing Hugo or visitor assets. Preserve wanted feedback and
references before manually deleting local tool/run directories.

Essay layout regressions protect the shared prose edges across openings, chapters
with and without figures, and endnotes at laptop/desktop/4K widths. Narrow and
print/enlarged states keep the centered 640px reading column; figures stack after
prose. Browser checks compare each essay header SVG with its archive SVG, so the
subject mark remains the same from discovery to reading. Every essay receives
its own print and enlarged-text state because the shared layout affects the corpus.
