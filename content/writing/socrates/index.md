+++
title = "Socrates: Before I Say ‘Go Build It’"
description = "I want the agent to help me think through the work, not just get on with it."
date = 2026-09-06T17:45:00-07:00
draft = false
toc = false
layout = "socratic"
callout = "A better question now is worth less rework later."
+++

{{< socrates-opening >}}
Socrates is a [Claude skill](https://github.com/lanej/dotfiles/blob/e48e4f0f3b8b7e5b1fe4d0b3ff17846529902977/claude/commands/socrates.md) I use before planning a piece of work. It researches the problem, challenges my assumptions, and writes down what we decide. Once we have something coherent enough to execute, it produces a plan.

This isn’t just a tool for AI. It’s a way of thinking: slow down at the beginning, examine the problem, make the reasoning explicit, and only then commit to a direction.
{{< /socrates-opening >}}

{{< socrates-section id="why-socrates" number="01" title="Why Socrates" diagram="method" >}}
The part of the [Socratic method](https://plato.stanford.edu/entries/plato-ethics-shorter/#2) I’m borrowing is the examination of what someone thinks they already know. A claim gets tested against the rest of the person’s commitments until the contradiction—or the missing assumption—becomes visible.

That is different from requirements gathering. I may have stated my preferred solution confidently without having thought through the problem very far.

> The useful outcome is often not more certainty. It is better uncertainty.
{{< /socrates-section >}}

{{< socrates-section id="request-to-clarity" number="02" title="From request to clarity" kicker="Example: remove deployment approval" diagram="comparison" >}}
An agent can find the manual gate and remove it. Socrates asks a more useful question first: what is that gate protecting?

If the answer is destructive migrations, the task may become narrower: automate routine releases while preserving review for risky ones. If we cannot distinguish the two, that becomes the first problem to solve.
{{< /socrates-section >}}

{{< socrates-section id="layered-reasoning" number="03" title="Layered reasoning" kicker="A specification connects the dots" diagram="layers" >}}
Socrates structures the outcome as [seven linked layers](https://github.com/lanej/dotfiles/blob/e48e4f0f3b8b7e5b1fe4d0b3ff17846529902977/claude/commands/socrates.md#phase-2--validation-and-layered-reasoning). The point is not to fill seven headings. It is to make sure the work still follows from the problem.

> A requirement without a reason is a suggestion. A success metric without a method is a hope.
{{< /socrates-section >}}

{{< socrates-section id="preserve-intent" number="04" title="Document, sequence, and preserve intent" diagram="workflow" >}}
Once the specification is validated, [Socrates produces a plan](https://github.com/lanej/dotfiles/blob/e48e4f0f3b8b7e5b1fe4d0b3ff17846529902977/claude/commands/socrates.md#phase-3--plan-mode). The important thing is the ordering: clarify the task, validate the reasoning, then sequence implementation around the dependencies.

The files carry those decisions forward so the executor does not have to reconstruct the conversation from memory.
{{< /socrates-section >}}

{{< socrates-resources >}}
Continue with [Close the Loop](/writing/close-the-loop/), on verifying the work against reality. [Read the Socrates source](https://github.com/lanej/dotfiles/blob/e48e4f0f3b8b7e5b1fe4d0b3ff17846529902977/claude/commands/socrates.md).
{{< /socrates-resources >}}
