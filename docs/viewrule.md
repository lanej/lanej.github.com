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
python3 scripts/viewrule.py check
```

Rebuild after changing source and rerun the check against that build. The command
prints the HTML report and JSON paths under `.ui-review/runs/`. Inspect the overview
for composition and native-scale tiles for text and diagram detail. At 4K, a reduced
full-page image alone is insufficient evidence. Failed rules and incomplete captures
exit 1; invalid setup exits 2. CI runs this command in the existing build job against
the same `public/` artifact that can deploy, using the runner's Chrome binary.
Reports are retained in `preflight-verification`, including when the check fails.

## Contract and coverage

`.ui-review/site.json` contains URL, viewport, capture, and freshness settings.
`scripts/viewrule.py` discovers all built pages, gives essays a required chapter
readiness selector, and writes the ignored native `.ui-review/config.json`.
It adds desktop print and 200% root-text states for three representative essays.
`.ui-review/rules.json` is the versioned native rule file; rule-authoring commands
write directly to it. No wrapper implements browser measurements.

[STYLE.md](../STYLE.md#enforcing-the-essay-standard) maps each rule to the design
requirement and documents viewport coverage. Viewrule checks bounded, centered
reading measure, DOM/visual order, prose alignment/columns, text clipping, diagram
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
run `check`, and review the actual report. Record the user's words against that run:

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
