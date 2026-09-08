+++
title = "Close the Loop"
description = "What control theory and Unix taught me about building with AI"
date = 2026-09-06T00:00:00-07:00
lastmod = 2026-09-07T14:58:00-07:00
draft = false
essay_visual = "feedback"
+++

Most failures I see in AI-assisted engineering are not failures of intelligence. They are failures of feedback.

A model can reason well about code, write a plausible implementation, run some checks, and confidently say the task is finished.

None of that means the thing actually works.

> **What signal tells the model that reality moved toward the state I actually wanted?**

That is the difference between an open-loop system and a closed-loop one. Once I started thinking about AI this way, a lot of my tooling changed.

## Open-loop AI

The naive pattern is simple: give the model a task, let it reason, and let it produce an artifact. Then the model looks at what it produced and effectively asks itself whether it seems right.

A more capable model improves the odds. A better prompt may improve them again. Neither creates a return path from reality.

A closed loop does. The model acts. The environment changes. Something measures the result. That evidence comes back, and the next action can respond to it.

{{< feedback-loop >}}

Claude Code itself works roughly this way: gather context, act, verify, repeat. Anthropic's broader agent guidance makes the same point about obtaining ground truth from the environment during execution.[^agent-loop]

The engineering question is what counts as ground truth for the requirement at hand.

## Verify where the requirement lives

I recently rediscovered this while rebuilding this website.

The agent changed the source and committed it. The static-site build passed. The deployment completed.

The image on the actual mobile site was broken.

The uploaded image was corrupted, but none of the intermediate checks looked at the user-visible result. They established that source could build and deploy, then those successes were treated as evidence for a different claim: that the page worked.

The requirement did not live in Hugo. It was that a person opening the site on a phone should see the right page.

So verification had to happen on the deployed domain, in a browser, at the relevant viewport.

That leads to a rule I use aggressively now: **verify at the layer where the requirement exists.**

If the requirement is visual, inspect the rendering. If it is an API contract, exercise the API. If it is a deployed service, observe the deployed service. If it is a data pipeline, check the resulting data.

Intermediate checks are useful. They establish narrower claims.

## Design the feedback loop before the implementation

This changed how I think about specification.

Before writing code, I increasingly want to know what done means, what could create a false green, what signal we can observe while work is underway, how expensive that signal is, and what fallback exists when there is no cheap automated check.

A final acceptance test tells you whether you arrived. A feedback loop tells you whether you are still driving in the right direction.

I eventually made this explicit in my Socrates tooling. Earlier versions concentrated on end-state validation. Later versions required a **Feedback Loop Design**: a signal, its cost and cadence, and a fallback when no fast automated check exists.[^socrates]

That change came from watching execution discover too late that it had no useful way to tell whether it was making progress.

The verification path is part of the design.

## A green signal you have not tried to break is weak evidence

Tests are the obvious feedback mechanism for code. But a test harness can itself be wrong.

A selector can match the wrong element. A mock can hide a disconnected integration. A regression test can be green because it was never wired into the suite.

For a new or uncertain harness, I want to deliberately break the relevant behavior, confirm the signal turns red, restore the implementation, and confirm green.[^methodology]

The point is not ritualistic TDD. It is to demonstrate that the verifier can detect the failure it claims to detect.

The same principle applies outside tests. If a browser check is supposed to catch horizontal overflow, create overflow and make sure it catches it. If a policy gate claims to prevent a class of writes, try the prohibited write in an isolated environment.

A signal is useful only if it discriminates between success and failure.

## Use AI to discover the process

There is a recurring pattern in my workflow.

At first, the process exists only as conversation. I tell Claude to inspect the rendered output rather than trust the build.

The next time, I say it again. Eventually I encode the procedure in a skill. If the procedure becomes stable and mechanical enough, I stop asking AI to perform that part at all.

{{< progressive-formalization >}}

I think of this as **progressive formalization**.

Natural language is useful while we are still learning the problem. Software becomes preferable once the behavior is understood well enough to encode.

Every repeated correction is therefore a candidate for compilation. Not every correction should become code; some expose a misunderstood goal. But if I keep reminding the model to perform the same mechanically checkable action, I should ask whether I am fixing the wrong layer.

## Unix has something to say about this

There is a temptation with AI to construct increasingly capable monoliths: more tools, more context, more rules, more responsibility concentrated in the agent.

That is not how I generally like to build software.

The Unix instinct is to decompose: narrow jobs, explicit interfaces, specialized tools, inspectable behavior. My own Constitution for Claude tooling carries that forward.[^constitution]

So I increasingly put formatters, validators, tests, browser checks, and policy enforcement outside the model's reasoning. The model calls those tools, reads their results, and handles the parts they cannot settle.

The interesting direction is not necessarily a smarter monolith. It is carving deterministic pieces out of the agent until the model is concentrating on work that genuinely requires judgment.

## Skills are for procedures. Programs are for invariants.

A skill is a good place for a procedure that still requires reasoning: investigate the codebase, challenge assumptions, inspect several sources, decide which validation strategy applies, and adapt based on what you find.[^skills]

But there is a boundary.

If a skill says “always run the formatter,” why should that remain a reasoning task? If it says “never write to these paths,” why should that depend on remembering prose?

The table maps each concern to the mechanism I use.

| Concern | Mechanism |
| --- | --- |
| Durable context | Documentation |
| Reusable reasoning | Skill |
| Contextual judgment | AI or a person |
| Hard policy | Enforced permissions, hooks, or CI gates |
| Mechanical correctness | Test or program |

Claude's documentation makes a useful distinction here too: instructions such as `CLAUDE.md` are context, while hooks run at defined lifecycle events instead of depending on the model to remember to invoke them.[^hooks]

A hook is not automatically a security boundary, and code is not automatically correct. The useful distinction is whether compliance still depends on remembering an instruction at the right moment.

## When wording stops being the bottleneck

I learned this one empirically.

I had a rule that forked agents should not write files under certain circumstances. The rule was clear. An agent violated it.

I strengthened the instruction. It happened again. I documented the failure. It happened again, including immediately after an agent had read the history explaining that exact failure.[^operating-rules]

At that point the wording was no longer the useful place to invest. The boundary belonged in the harness.

This is a systems-design lesson that predates AI. Policy and mechanism are different things. If correctness requires a model to remember an instruction at the right time, what you have is a preference, not an invariant.

## The worker's self-report is not verification

One of my newer tools makes the distinction explicit.

I have a small bug-and-feature dispatcher for a scoped set of repositories. An AI worker receives the task, investigates it, writes the change, and adds a test.

But its claim that it succeeded is not evidence for the merge decision.

A separate script inspects the worktree. It reruns the test suite, checks whether the diff includes a test file, and flags changes to sensitive paths. Independent code review remains a judgment step. The dispatcher combines that review with the mechanical results instead of trusting the worker's completion message.[^dispatcher]

The current checks are useful but not omniscient. Touching a test file does not prove meaningful coverage, and a passing suite does not prove the tests measure the right requirement.[^worker]

That boundary is the point: conventional software obtains observations that conventional software can obtain consistently; the model handles interpretation and judgment around them.

## But don't mechanize judgment

There is an opposite failure mode.

At one point I added a hard gate requiring an independent high-capability model to critique every plan before Claude could exit plan mode.

It also fired for small, obvious, low-risk plans where the second review added little. I removed the universal gate and made additional critique contextual instead.[^operating-rules]

The lesson is not “turn everything into hooks.” Mechanize invariants. Preserve judgment for decisions that depend on context, risk, ambiguity, or competing goals.

## Two loops

There are really two timescales here.

The execution loop is **act → observe → correct → verify**.

The learning loop is **failure → reflection → lesson → skill, rule, or mechanism → future behavior**.

My tooling has gradually accumulated both. Incidents become lessons. Repeated lessons become operating rules. Repeated procedures become skills. Mechanically checkable boundaries become candidates for enforcement.[^constitution]

That is the part of AI-assisted engineering I find most interesting. A model can help discover which parts of our own reasoning should eventually stop being model work.

When I build an AI-assisted workflow now, I want to know the desired state, the observation that tells us whether we are getting closer, what could create a false green, and which parts of the procedure still require judgment.

Then I want the repeated mechanical parts to migrate outward into ordinary software.

The goal is not an AI that never makes mistakes. It is a system where mistakes become observations, observations improve the process, and repeated process eventually becomes mechanism.

[^agent-loop]: Anthropic, [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works#the-agentic-loop) and [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
[^socrates]: [Add in-progress feedback-loop design to the Socrates lifecycle](https://github.com/lanej/dotfiles/commit/ec94ec4159c9e7ea6fa04fba37d94f342515128c), September 1, 2026.
[^methodology]: My [methodology skill](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/skills/methodology/SKILL.md), particularly Feedback Loop Design and harness verification.
[^constitution]: My [tooling Constitution](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/CONSTITUTION.md), particularly Root Cause and Technical Integrity, Unix Philosophy, and the distinction between durable principles and mechanisms.
[^skills]: Anthropic, [Extend Claude with skills](https://code.claude.com/docs/en/skills).
[^hooks]: Anthropic, [How Claude remembers your project](https://code.claude.com/docs/en/memory) and [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide).
[^operating-rules]: My [operating rules](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/CLAUDE.md), including the recorded no-write failures and removal of the universal plan-critique gate.
[^dispatcher]: The [bug-and-feature dispatcher protocol](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/skills/bugfix-dispatcher/SKILL.md).
[^worker]: The corresponding [mechanical worker script](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/bin/bugfix-worker).