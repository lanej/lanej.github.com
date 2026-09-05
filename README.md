# lanej.io

Josh Lane’s professional website. Hugo, Markdown, HTML templates, native CSS,
and a locally hosted photograph. No theme, frontend JavaScript, CMS, font service,
or runtime package dependencies.

## Edit and preview

Install the version in `.hugo-version`, then run `hugo server`.

- `content/`: page copy and future published essays.
- `data/work.yaml`: the homepage’s selected-work summaries.
- `layouts/`: shared page structure, metadata, navigation, and image markup.
- `assets/css/site.css`: the entire visual system.
- `assets/images/josh-lane.webp`: the supplied green-background photograph,
  optimized at its original 1254 × 1254 resolution. Hugo produces responsive
  480, 800, and 1200 pixel derivatives and JPEG fallbacks.

Writing is absent from navigation until at least one essay is published. Private
research, unapproved achievements, and unpublished confidential material must
never be committed to this public repository, even as Hugo drafts.

## Build and test

On Linux, `bash scripts/install-hugo.sh` installs the checksum-verified Hugo binary.
On another system, use the same Hugo version and set `HUGO_BIN` to its path.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r scripts/requirements.txt
python -m playwright install --with-deps chromium webkit
bash scripts/install-hugo.sh
bash scripts/build.sh
python -m http.server 8765 --directory public &
python scripts/verify.py --engines chromium,webkit
```

Python packages and browser binaries are verification tools only; they do not
ship to visitors. `public/`, generated image caches, and test artifacts are ignored.

## Publish

Merge a PR into `master`. The Pages workflow builds Hugo once, validates metadata,
internal links and image decoding, then runs Chromium and WebKit at desktop and
mobile widths. It deploys that exact artifact, not a separately edited HTML tree.

After deployment, verification waits for the expected revision on **lanej.io**,
compares HTTP response hashes to the tested artifact, decodes the images, and
captures browser screenshots of Home, Work, and About. Download the
`live-domain-verification` Actions artifact for screenshots, the revision, and
verification results. A successful deployment alone is not an acceptance test.

In repository **Settings → Pages**, Source should be **GitHub Actions**. Until that
one-time administrative setting is changed, the workflow detects legacy branch
publishing and waits for its run before deploying Hugo. Domain and HTTPS settings
are left unchanged. The root `CNAME` marker is retained to protect the existing
custom domain during migration; the build checks it against `static/CNAME`.
The final source tree contains no generated root HTML.

To verify a deployed build manually, download that run’s `site-bundle` artifact
into `public/`, then run:

```sh
python scripts/verify.py --url https://lanej.io/ --output artifacts/live --engines chromium,webkit
```

To roll back, revert the relevant merge and let the same workflow publish and test.

## Content and attribution

Career accounts are identified as such and link to the professional profile;
public software examples link to package metadata or the official project.
Do not convert company-wide performance into personal achievements, invent
before/after metrics, or publish confidential strategy. Verify attribution and
publication permission before adding substantive business claims.

Hugo and Actions are pinned. To upgrade Hugo, change `.hugo-version` and the
release checksum in `scripts/install-hugo.sh` together, then run the full checks.
