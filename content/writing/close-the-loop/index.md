+++
title = "Close the Loop"
description = "What control theory and Unix taught me about building with AI"
date = 2026-09-06T00:00:00-07:00
draft = false
diagrams = true
toc = false
+++

Most failures I see in AI-assisted engineering are not failures of intelligence. They are failures of feedback.

A model can be excellent at reasoning about code and still make a bad change. It can write a plausible implementation, explain why it works, run some checks, and confidently tell you that the task is finished.

None of that means the thing actually works.

The useful question is not: how do I make the model smarter?

It is:

> **What signal tells the model that reality moved toward the state I actually wanted?**

That sounds obvious. It is also the difference between an open-loop system and a closed-loop one. And once I started thinking about AI this way, a lot of my tooling changed.

## Open-loop AI

The naive pattern for AI-assisted work is simple: give the model a task, let it reason, and let it produce an artifact. The artifact may be code, a configuration change, a document, a deployment, or a design.

Then the model looks at what it produced and effectively asks itself: does this seem right?

That is not much of a control system.

A more capable model improves the odds. A better prompt may improve them again. Neither changes the fundamental architecture. There is still no return path from reality.

A closed loop looks different. The model acts. The environment changes. Something measures the result. That evidence returns to the model, which can correct course.

{{< feedback-loop >}}

Claude Code itself is built around roughly this idea: gather context, take action, verify the result, repeat. Anthropic's broader agent guidance makes the same point: agents need ground truth from the environment during execution, and coding is particularly amenable to agents because the results can often be verified automatically.[^agent-loop]

The interesting engineering work starts when you take that idea seriously.

## The build passing is not the same as the thing working

I recently rediscovered this while rebuilding this website.

The agent changed the source and committed it. The static-site build passed. The deployment completed.

And the image on the actual mobile site was broken.

The uploaded image was corrupted, but the build and deployment did not detect that. Every intermediate success was being treated as evidence for a different claim: that the user-visible result was right.

The problem was not that I needed another test of the Hugo configuration. The requirement did not live in Hugo.

The requirement was: a person opening this site on a phone should see the right page.

So that is where the verification eventually had to happen: on the deployed domain, in an actual browser, at the relevant viewport.

That leads to a rule I now use fairly aggressively:

> **Verify at the layer where the requirement exists.**

If the requirement is visual, inspect the rendering. If it is an API contract, exercise the API. If it is a deployed service, observe the deployed service. If it is a data pipeline, check the resulting data. If it is a business process, measure the business outcome.

Intermediate checks are useful. They are not substitutes for the endpoint.

## Design the feedback loop before the implementation

This changed how I think about specification too.

Before writing code, I increasingly want to know what "done" means, what could make a bad result look good, and what must not regress. But I also want to know what signal I can observe while the work is still underway, how expensive it is, how often I can check it, and what the fallback is when there is no cheap automated check.

That last group matters more than I initially appreciated.

A final acceptance test tells you whether you arrived. A feedback loop tells you whether you are still driving in the right direction.

I eventually made this explicit in my Socrates tooling. Earlier versions concentrated on end-state validation. Later versions required a **Feedback Loop Design** as part of the specification itself: a signal, its cost and cadence, and a fallback when there is no fast automated check.[^socrates]

That was not a stylistic preference. It came from watching execution discover too late that it had no useful way to tell whether it was making progress.

The verification path is part of the design.

## A green signal you have not tried to break is weak evidence

Tests are the obvious feedback mechanism for code. But "run the tests" is not quite enough.

A test harness can itself be wrong. A test can pass because it never exercises the behavior. A selector can match the wrong element. A mock can hide a disconnected integration. A regression test can be green because it was never wired into the suite.

So one of the rules I ended up putting into my methodology is:

> **Don't trust a green result you haven't tried to break.**

For a new harness, I want to write the test, deliberately break the relevant implementation, confirm the test turns red, restore the implementation, and confirm green.

The point is not ritualistic TDD. The point is to demonstrate that the verifier can detect the failure it claims to detect.[^methodology]

The same principle applies outside tests. If a browser check is supposed to catch horizontal overflow, create overflow and make sure it catches it. If a deployment verifier claims to detect a stale revision, point it at a stale revision. If a policy gate claims to prevent a class of writes, try the prohibited write in an isolated test environment.

A feedback loop is only useful if the signal discriminates between success and failure. This does not mean every test in an established suite needs a new break-check on every run. It means uncertain harness wiring should not get the benefit of the doubt.

## Use AI to discover the process

There is a common pattern in my own workflow.

At first, the process exists only as conversation. I tell Claude something like:

> After making the change, inspect the actual rendered output. Don't just trust the build.

The next time, I say it again. Eventually I stop saying it and encode the procedure in a skill. And if the procedure proves stable enough, I stop asking AI to perform the mechanical parts at all.

{{< progressive-formalization >}}

I think of this as **progressive formalization**.

Natural language is very flexible. That makes it useful when you are still learning the problem. Software is less flexible. That is exactly why it becomes preferable once the behavior is understood.

So my rule is:

> **Every repeated correction is a candidate for compilation.**

Not every correction should become code. Some expose a misunderstood goal, and the right response is another conversation. But if I keep reminding the model to do the same mechanically checkable thing, I should ask whether I am fixing the wrong layer.

## Unix has something to say about this

There is a temptation with AI to construct increasingly capable monoliths.

Give the agent more tools. Give it more context. Put more rules into its prompt. Have it remember policy, run the checks, decide whether the checks are good enough, and grade its own work.

That is not how I generally like to build software.

The Unix instinct is to decompose. Give one thing a narrow job. Make interfaces explicit. Compose specialized tools. Prefer a small program with inspectable behavior over a large system full of implicit state.

My own Constitution for Claude tooling explicitly carries that forward: specialized, composable tools, simple interfaces, and small mechanisms over monolithic solutions.[^constitution]

So the system I want increasingly puts formatters, validators, tests, browser checks, and policy enforcement outside the model's reasoning. The model calls those tools, reads their results, and handles the parts they cannot settle.

The model is still important. It is simply no longer responsible for everything.

The Unix answer to agent reliability is not necessarily a smarter monolith. It is to keep carving deterministic pieces out of the agent until the model is concentrating on the parts that genuinely require judgment.

## Skills are for procedures. Programs are for invariants.

This is where I find Claude skills particularly useful.

A skill is a good place for a procedure that still requires reasoning: investigate the codebase, challenge assumptions, inspect several sources, decide which validation strategy applies, and adapt based on what you find.

Claude Code's skill model supports this sort of repeated checklist or multi-step procedure, with detailed supporting material available when needed.[^skills]

But there is a boundary.

Suppose a skill says: always run the formatter. Why should that remain a reasoning task?

Or: never write to these paths. Why should that depend on the model remembering prose?

Or: do not declare this deployment successful unless the live revision matches. That can be a program.

The rough hierarchy I use is:

| Concern | Mechanism |
| --- | --- |
| Durable context | Documentation |
| Reusable reasoning | Skill |
| Contextual judgment | AI or a person |
| Hard policy | Enforced permissions, hooks, or CI gates |
| Mechanical correctness | Test or program |

Claude's own documentation makes a useful distinction here: instructions such as `CLAUDE.md` are context, while command hooks run at defined lifecycle events rather than depending on the model to remember to invoke them.[^hooks]

A hook is not automatically a security boundary, and code is not automatically correct. The rule, its implementation, and the permissions around it still need to be sound.

## If the instruction keeps failing, stop rewriting the instruction

I learned this one empirically.

I had a rule that forked agents should not write files under certain circumstances. The rule was clear. Then an agent violated it.

So I strengthened the instruction. It happened again. I documented the failure. It happened again. Eventually it happened immediately after the agent had read the history explaining that exact failure.

At that point the conclusion was hard to avoid:

> **The wording was not the bottleneck.**

My operating notes record those repeated failures and the move toward enforcing the boundary in the harness rather than relying on another restatement.[^operating-rules]

This is a systems-design lesson that predates AI. Policy is not mechanism. A statement saying something must not occur is useful. A mechanism that prevents it is different.

If correctness requires the model to remember an instruction at the right time, what you have is a preference, not an invariant.

## The AI should not grade its own homework

One of my newer tools makes this distinction very explicit.

I have a small bug-and-feature dispatcher for a scoped set of repositories. An AI worker receives the task, investigates it, writes the change, and adds a test.

But the worker's claim that it succeeded is not evidence for the merge decision.

A separate script inspects the actual worktree. It reruns the test suite, checks whether the diff includes a test file, and flags changes to sensitive paths. Independent code review remains a judgment step. The dispatcher combines that review with the mechanical results rather than trusting the worker's completion message.[^dispatcher]

The dispatcher documentation says it directly: **never trust the fixer's self-report**.

These checks are useful, not omniscient. Touching a test file does not prove meaningful coverage, and a passing suite does not prove the tests measure the right requirement. The current script exposes verification results; the dispatcher protocol still coordinates the decision to merge or open a PR. That distinction matters when describing what is actually enforced.[^worker]

That is what I mean by taking AI out of the loop. Not removing all judgment, and not pretending a few checks establish correctness. Removing repeated mechanical work from the model's responsibilities.

The AI interprets the problem, searches the codebase, reasons about the cause, and writes the implementation. Conventional software obtains the observations that conventional software can obtain more consistently.

## But don't mechanize judgment

There is an opposite failure mode.

At one point I added a hard gate requiring an independent high-capability model to critique every plan before Claude could exit plan mode.

It also fired for small, obvious, low-risk plans where another review added very little. The presence of a gate did not make its policy appropriate.

I removed the universal gate and made additional critique contextual instead.[^operating-rules]

This is an important constraint on the argument. The goal is not to turn everything into hooks.

> **Mechanize invariants. Preserve judgment for tradeoffs.**

If a decision depends on context, risk, ambiguity, or competing goals, that is exactly where a model can be useful. If the answer can be determined mechanically, asking an LLM is often just a slower and less consistent implementation.

## Two loops

There is another feedback loop that matters over a longer timescale.

The first is the execution loop: **act → observe → correct → verify**.

But there is also a learning loop: **failure → reflection → lesson → skill, rule, or mechanism → future behavior**.

My tooling has gradually accumulated this structure. Incidents become lessons. Repeated lessons become operating rules. Repeated procedures become skills. Mechanically checkable boundaries become candidates for enforcement in code.[^constitution]

The system becomes less dependent on remembering the same lesson conversationally every time.

That is the part of AI-assisted engineering I find most interesting. Not that a model can write more code. That it can help us discover which parts of our own reasoning should eventually become software.

## Close the loop first

When I start building an AI-assisted workflow now, I increasingly ask these questions in order:

1. What is the desired state?
2. How can the system observe whether it is getting closer?
3. Can the model access that observation itself?
4. What failure would create a false green?
5. Which parts of the procedure still require judgment?
6. Which repeated decisions can become deterministic?
7. Can I remove AI from those parts entirely?

The progression is not more prompt, more context, more agents, more autonomy.

It is closer to: **close the loop → observe failures → improve the procedure → formalize the procedure → automate the invariant**.

Use AI to discover the loop. Use AI to help build the loop. Then take AI out of every part where software can provide a faster, cheaper, more consistent answer.

The goal is not an AI that never makes mistakes.

It is a system where mistakes become observations, observations become feedback, and repeated feedback eventually becomes software.

[^agent-loop]: Anthropic, [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works#the-agentic-loop) and [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
[^socrates]: [Add in-progress feedback-loop design to the Socrates lifecycle](https://github.com/lanej/dotfiles/commit/ec94ec4159c9e7ea6fa04fba37d94f342515128c), September 1, 2026. Socrates has a broader role in clarifying intent and specifying work; this is the feedback-design part of it.
[^methodology]: My [methodology skill](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/skills/methodology/SKILL.md), particularly Feedback Loop Design and harness verification.
[^constitution]: My [tooling Constitution](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/CONSTITUTION.md), particularly Root Cause and Technical Integrity, Unix Philosophy, and the distinction between durable principles and mechanisms.
[^skills]: Anthropic, [Extend Claude with skills](https://code.claude.com/docs/en/skills).
[^hooks]: Anthropic, [How Claude remembers your project](https://code.claude.com/docs/en/memory) and [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide).
[^operating-rules]: My [operating rules](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/CLAUDE.md), including the recorded no-write failures and removal of the universal plan-critique gate. These are operating notes, not proof that every described safeguard is implemented or unbypassable.
[^dispatcher]: The [bug-and-feature dispatcher protocol](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/skills/bugfix-dispatcher/SKILL.md).
[^worker]: The corresponding [mechanical worker script](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/bin/bugfix-worker). Its verification subcommand reruns tests and examines the diff; its finish subcommand is not itself a complete enforcement of the protocol's merge criteria.
