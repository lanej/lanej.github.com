# Labs and open source

`content/labs.md` holds experiments. State the question, the artifact's state,
and its limits. Use synthetic data explicitly. `content/open-source.md` holds
maintained tools (including dotfiles and Viewrule), with upstream contributions
from `data/contributions.yaml`. Career and speaking remain on Work.

The delivery preview is a screenshot of the real public demo at 1120 × 1020,
not a generated illustration. Keep its declared dimensions and alt text current.
The inline demo loads only after opening its disclosure and releases its iframe
when closed. A static preview and a standalone link work without site JavaScript.
The demo requires WebGL 2; its own fallback explains unavailable graphics.

## GitHub calendar

`scripts/github-activity.py` reads the unauthenticated public contribution calendar
at https://github.com/users/lanej/contributions. It validates dates, completeness,
counts, and intensity levels before replacing `data/github_activity.json`.
A fetch or parse failure preserves the dated snapshot; it never fabricates zeros.
The page always shows the retrieval date and links to the live GitHub profile.

The existing Pages workflow refreshes this snapshot before each build and runs
weekly on Monday. It publishes through the same build/deploy path and does not
commit generated refreshes. The checked-in snapshot is an offline fallback.
To refresh it deliberately:

```sh
python3 scripts/github-activity.py
python3 scripts/test-github-activity.py
```

The full year appears on desktop; phones show the last 13 calendar weeks so
individual days remain legible. Monthly totals are available in a native disclosure.
Both views use the same days and GitHub's intensity categories.

[GitHub's contribution definitions](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)
include more than commits. The public calendar can include anonymized counts from
private work the owner has chosen to display; no private repository data is fetched.
Activity is not a measure of quality, productivity, or impact. The public HTML
format is not a versioned API; if it changes, repair the parser and its single
regression rather than making the site depend on a third-party image service.
