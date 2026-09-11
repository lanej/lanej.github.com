+++
title = "Socrates: Before I Say ‘Go Build It’"
description = "I built a Claude skill to challenge the request, preserve the decisions, and make the handoff executable."
date = 2026-09-06T17:45:00-07:00
draft = false
essay_image = "socrates-bust.webp"
essay_image_alt = "Illustrated bust of Socrates"
essay_image_caption = "Examine the claim before acting on it."
callout = "Research should arm the question, not eliminate it."
+++

I originally told Socrates to ask me fewer questions.

Socrates is a [Claude skill](https://github.com/lanej/dotfiles/blob/e48e4f0f3cc72f8f6ab7a0c025bd5304be24fb2d/claude/commands/socrates.md) I use before planning a piece of work. An earlier version had what sounded like a good rule: read the code, inspect the configuration, look through prior decisions, and try to answer every question before interrupting me. If the agent found a plausible answer, it should record the assumption and move on.

That worked well for facts. It was a bad rule for decisions.

Which language does this repository use? Research it. Does an old restriction still serve a purpose? The repository can tell me that the restriction exists. It cannot tell me whether I still want it.

I had optimized the skill to reduce conversation at exactly the point where the conversation was useful. I did not need a faster requirements form. I wanted the agent to help me think through the work before an implementation gave one interpretation momentum.

So I changed the rule: [research should arm the question, not eliminate it](https://github.com/lanej/dotfiles/commit/39048c0f3cc72f8f6ab7a0c025bd5304be24fb2d). Bring me what you found. Explain why it might matter. Then ask the question that the evidence cannot answer for us.

## Why Socrates {#why-socrates-title}

The part of the [Socratic method](https://plato.stanford.edu/entries/plato-ethics-shorter/#2) I’m borrowing is not “keep asking why.” It is the examination of a claim against the rest of what we think we know. A question exposes an assumption; another commitment puts pressure on it; the contradiction or missing premise becomes visible.

That matters because a request to an AI is not necessarily a correct specification of the problem. I may arrive with a preferred solution and a lot of confidence. The model may have an equally plausible interpretation. Neither deserves to become the plan merely because it was stated first.

The useful outcome is sometimes less certainty, not more. We discover the hole in an answer we were already prepared to act on.

That is different from endless debate. Socrates still has to converge. The current dialogue loop works one consequential topic at a time: research it, ask one informed question, judge the answer, follow up when it is vague or contradictory, and stop when the relevant issue is stable enough to proceed. There is no question quota to satisfy and no prize for making a small task ceremonial.

The useful thing is making the assumption visible before either of us builds on it, not getting the agent to agree with me.

{{< socrates-diagram "method" >}}

## From request to clarity {#request-to-clarity-title}

**What the lock actually stops**

An AI agent doing analysis work has a way to spend real money — one expensive query, or a session that runs long enough to add up. I wanted a hard stop: before anything costly runs, a human has to physically approve it. Touch ID, or nothing happens. The one-line description of the feature was clean: this removes the agent’s ability to approve its own spending.

That sentence claims more than the design delivers.

The same agent I’m gating also has shell access. It can delete the file that remembers today’s spending. It can unset the environment variable that turns the gate on in the first place. It can skip the guarded interface entirely and call the underlying tool directly. None of that requires beating the fingerprint check. The check only stops one specific failure mode: the agent quietly retrying with a bigger budget, typing yes to its own prompt, or not asking at all.

That distinction changes what the feature is for. It is not a wall between an agent and my money. It is friction against an *undocumented* shortcut — the kind of thing that happens by drift, not by an agent actively working around a rule. Worth building, on those terms. Not worth building if I expected it to hold against an agent actually trying to get past it.

One of the success criteria had the same problem in miniature: it promised identical behavior from two entry points that don’t even share a process, which was never something the design could deliver. Restating it as “same fail-closed behavior, same limits” was still a real requirement — just not the one originally written down.

The gate shipped. It still assumes good faith on the agent’s part. That’s now a stated fact about the feature, instead of an unexamined one.

{{< socrates-diagram "comparison" >}}

## Layered reasoning {#layered-reasoning-title}

**Make the argument inspectable**

Once the dialogue settles, Socrates does something that matters more than producing polished prose: it turns the result into a [reasoning chain](https://github.com/lanej/dotfiles/blob/e48e4f0f3cc72f8f6ab7a0c025bd5304be24fb2d/claude/commands/socrates.md#phase-2--validation-and-layered-reasoning).

The layers are problem, requirements, constraints, risks, success, validation, and execution readiness. I do not care whether all seven headings are present because seven is a nice number. I care that each layer has to follow from the one below it.

For the cost gate, the **problem** is not “the agent can approve its own spending.” The problem is that the fix is described as removing self-approval when it only blocks one narrow, in-band shortcut, and the agent still has shell access to work around it entirely. That distinction changes the **requirements**: state plainly which property is being built — friction against an undocumented shortcut, not containment against an agent actively trying to get around it. It exposes a **risk**: a control can earn more trust than it deserves once its own name overclaims. That risk changes **success** and **validation**: identical behavior across two entry points was never possible, since they don’t share a process model — the real bar is the same fail-closed behavior and the same limits, forced by an actual timeout and an actual denial, not assumed from a clean run.

This is where false greens become easier to see. “The fingerprint prompt appears” is evidence about the implementation. It is not evidence that the control holds the property its own description claims. Two entry points looking identical in a terminal does not mean they enforce the same limit underneath.

The specification also records authority boundaries. An executor can choose the timeout value or the exact prompt wording. It should not decide, on its own, to keep describing the feature as removing self-approval, full stop. Restating what a safety feature is actually worth is a decision, not an implementation detail — if the claim changes, that decision belongs back in the agreement.

That is one of the ways this is specifically about AI. The agent being gated is the same kind of agent that might one day resume this very conversation, unaware that “removes self-approval” was already found to overclaim. The document has to carry the correction, not just the code.

{{< socrates-diagram "layers" >}}

## Document, sequence, and preserve intent {#preserve-intent-title}

The output of Socrates is not the conversation. It is a set of artifacts another process can use: an authoritative `spec.md`, an optional independent critique, a `plan.md`, and verification evidence when the work is done.

The accompanying decision record illustrates what I want the handoff to preserve: the decision, why it exists, what is delegated, and what evidence would demonstrate it. It is a condensed example for the cost gate, not a copy from a saved Socrates session.

{{< socrates-diagram "record" >}}

Once that agreement is stable enough, Socrates freezes and versions the specification before planning. “Frozen” is procedural, not magical file protection. If critique exposes a bad assumption or execution discovers something genuinely new, the specification can reopen. What should not happen is an executor quietly weakening the requirement until its preferred implementation qualifies.

Then sequencing becomes a different problem. Every task in the plan has to trace back through a requirement to the original problem, and the plan gets its own dependency graph. The question is no longer “what do we mean?” but “what has to happen before what?”

The cost-gate specification went through an independent plan critique. It didn’t catch a bug in the code — it caught a bug in the claim. The plan implemented exactly what was asked and was still wrong about what that implementation was worth: “removes agent self-approval” overstated what a fingerprint prompt can do against an agent that already has shell access. A separate success criterion turned out to be impossible outright, promising identical behavior from two entry points that don’t share a process model.

That is why I separate specification review from plan review. A specification can be right while the proposed steps fail to preserve it. A plan can be internally coherent while testing the wrong thing.

The final checks forced an actual timeout, forced an actual denial, and confirmed the old `-y`/`--yes` flag could no longer quietly bypass the new gate — it now fires regardless of that flag, unconditionally. The verifier was not allowed to redefine success at the end.

This is an AI workflow, but the underlying discipline is older and broader: examine the claim, make the reasoning explicit, preserve the decisions, sequence the dependencies, and test the thing you actually meant.

I use Socrates because AI makes execution cheap enough that **starting the wrong work is increasingly the expensive mistake**. Sometimes the outcome is a better plan. Sometimes the outcome is deciding not to build the thing I originally asked for.

Before I say “go build it,” that is exactly the kind of friction I want.

{{< socrates-diagram "workflow" >}}

{{< socrates-resources >}}
Continue with [Close the Loop](/writing/close-the-loop/), on verifying the work against reality. [Read the Socrates source](https://github.com/lanej/dotfiles/blob/e48e4f0f3cc72f8f6ab7a0c025bd5304be24fb2d/claude/commands/socrates.md).
{{< /socrates-resources >}}
