# lanej.io

Source for [Josh Lane’s website](https://lanej.io/): writing, open-source work,
and experiments. Built with Hugo, Markdown, native CSS, and minimal JavaScript;
hosted on GitHub Pages.

## Run locally

Install Python 3.11+ and the Hugo version in [`.hugo-version`](.hugo-version).
On Linux x86-64, `bash scripts/install-hugo.sh` installs the pinned binary;
elsewhere, put that version of `hugo` on your PATH.

```sh
python3 scripts/writing.py preview
```

The preview includes local drafts and listens only on `127.0.0.1`.

## Write and publish

```sh
python3 scripts/writing.py new my-essay --title "My essay"
nvim drafts/my-essay/index.md
```

Complete the description and article, preview it, and review every asset before
preparing it for publication:

```sh
python3 scripts/writing.py publish my-essay
```

This moves the bundle into `content/writing/`; it does not commit or deploy.
Review the diff and open a PR. Merging into `master` runs the tested deployment
workflow. Local `drafts/` are gitignored and excluded from production, but
**gitignore is not access control**. Never commit private material.

## Guides

| Task | Reference |
| --- | --- |
| Drafts, images, citations, and publication | [Publishing](docs/publishing.md) |
| Build, test, deploy, and maintain the site | [Development](docs/development.md) |
| Voice, reasoning, and evidence | [Writing standards](WRITING.md) |
| Layout and shared components | [Visual standards](STYLE.md) |
| Visual verification and rule changes | [Viewrule](docs/viewrule.md) |
| Instructions for coding agents | [AGENTS.md](AGENTS.md) |
