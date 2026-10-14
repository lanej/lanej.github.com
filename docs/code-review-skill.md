# Code-review guide and skill

The canonical review guidance is the marked section of
`content/writing/code-review/index.md`. It contains the standard, guidelines,
approval policy, and their source notes. Keep installation instructions outside
those markers so the installed skill does not tell the reviewer to install itself.

`skills/code-review/adapter.md` supplies Agent Skills metadata, the agent workflow,
and authority boundaries. It must contain exactly one `{{GUIDANCE}}` placeholder
and one `{{GUIDANCE_SHA256}}` placeholder. The generator embeds the marked guidance
verbatim and records its SHA-256 digest. Do not edit the generated file directly.

After editing either source:

```sh
python3 scripts/code-review-skill.py
python3 scripts/test-code-review-skill.py
python3 scripts/code-review-skill.py --check
```

Commit both the source changes and `static/skills/code-review/SKILL.md`. Update the
skill's metadata version for substantive changes. The static directory publishes
that exact file at `/skills/code-review/SKILL.md`; the guide lives at
`/writing/code-review/`. The raw file has no required companion assets.

`scripts/build.sh` checks synchronization before Hugo runs and compares the built
raw file afterward. Tests exercise marker validation, missing/stale output, source
notes, and the actual documented curl command with a stubbed network. They check
successful installation and failure preservation, including home paths with spaces.
These are packaging checks, not evidence of an agent's review accuracy.

The download URL tracks the deployed version. For reproducible reviews, keep the
installed file in version control. The embedded digest records source identity;
it is not a cryptographic signature or a substitute for trusting the download.
