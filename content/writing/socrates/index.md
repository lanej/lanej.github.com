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

I wanted an AI agent to ask before spending more money. An expensive query or a long analysis session could run past the budget I had in mind. The proposed fix was a biometric approval gate: when the work needed approval, I would authorize it with Touch ID.

The feature’s description went further: it would remove the agent’s ability to approve its own spending.

During review, that claim ran into the rest of the design. The agent retained shell access and other routes to the underlying tools. Requiring a fingerprint in one interface did not put those routes behind the same approval. The useful question became whether the gate was still worth building with that limitation.

I kept it. There was a specific behavior I wanted to stop in the normal workflow: an agent reaching a budget limit, retrying with a larger allowance, and treating its own answer to a confirmation prompt as my permission. Requiring my fingerprint made that approval step mine. It remained useful even though it could not control every action available to the agent.

That gave the specification a narrower, testable promise. Within the guarded interface, denying approval or letting it time out must stop the operation. An option that automatically answers yes must not count as authorization. The agent’s access outside that interface remained an explicit limitation.

The gate shipped with that narrower purpose. The review changed what I was prepared to rely on it for. I could require deliberate approval in this workflow without mistaking the prompt for control over all the agent’s spending.

{{< socrates-diagram "comparison" >}}

## Layered reasoning {#layered-reasoning-title}

**Make the argument inspectable**

Once the dialogue settles, Socrates does something that matters more than producing polished prose: it turns the result into a [reasoning chain](https://github.com/lanej/dotfiles/blob/e48e4f0f3cc72f8f6ab7a0c025bd5304be24fb2d/claude/commands/socrates.md#phase-2--validation-and-layered-reasoning).

The layers are problem, requirements, constraints, risks, success, validation, and execution readiness. I do not care whether all seven headings are present because seven is a nice number. I care that each layer has to follow from the one below it.

For the cost gate, the **problem** was spending beyond an intended budget without a deliberate decision from me. That established a **requirement**: when the guarded workflow asks for approval, only a human can supply it. The **constraint** was that the agent kept its other access to the tools. Recording that constraint exposed a **risk**: I might trust the gate to enforce a spending limit beyond the workflow it actually controlled.

From there, **success** becomes concrete: a denied or unanswered request must leave the costly operation unexecuted. **Validation** has to force those cases and inspect what happens afterward. A screenshot of the fingerprint prompt establishes that a prompt appeared. It says nothing about whether the operation still ran after the prompt failed.

The specification also records what the executor can decide. Prompt wording and internal code structure leave room for judgment. Continuing after a timeout changes the agreement. So does accepting an automated confirmation as approval. Those choices have to come back to me, even if they make the implementation easier.

The next agent may have none of the conversation that established these limits. The document has to explain why an apparently helpful fallback would violate the requirement.

{{< socrates-diagram "layers" >}}

## Document, sequence, and preserve intent {#preserve-intent-title}

The output of Socrates is not the conversation. It is a set of artifacts another process can use: an authoritative `spec.md`, an optional independent critique, a `plan.md`, and verification evidence when the work is done.

The accompanying decision record illustrates what I want the handoff to preserve: the decision, why it exists, what is delegated, and what evidence would demonstrate it. It is a condensed example for the cost gate, not a copy from a saved Socrates session.

{{< socrates-diagram "record" >}}

Once that agreement is stable enough, Socrates freezes and versions the specification before planning. “Frozen” is procedural, not magical file protection. If critique exposes a bad assumption or execution discovers something genuinely new, the specification can reopen. What should not happen is an executor quietly weakening the requirement until its preferred implementation qualifies.

Then sequencing becomes a different problem. Every task in the plan has to trace back through a requirement to the original problem, and the plan gets its own dependency graph. The question is no longer “what do we mean?” but “what has to happen before what?”

In the cost-gate example, independent plan critique exposed the overstated promise. That finding belonged back in the specification, where it could change both the implementation plan and the standard used to judge the result. Leaving the correction in a review comment would make it too easy for a later executor to miss.

That is why I separate specification review from plan review. A specification can be right while the proposed steps fail to preserve it. A plan can be internally coherent while testing the wrong thing.

For the gate, useful verification evidence would show the outcome of denial and timeout, including whether any costly work ran. It would also show that an automated confirmation could not substitute for the required approval. That evidence could establish the agreed behavior within the guarded workflow. The verifier could not turn it into a broader claim about every route the agent could take.

This is an AI workflow, but the underlying discipline is older and broader: examine the claim, make the reasoning explicit, preserve the decisions, sequence the dependencies, and test the thing you actually meant.

I use Socrates because AI makes execution cheap enough that **starting the wrong work is increasingly the expensive mistake**. Sometimes the outcome is a better plan. Sometimes the outcome is deciding not to build the thing I originally asked for.

Before I say “go build it,” that is exactly the kind of friction I want.

{{< socrates-diagram "workflow" >}}

{{< socrates-resources >}}
Continue with [Close the Loop](/writing/close-the-loop/), on verifying the work against reality. [Read the Socrates source](https://github.com/lanej/dotfiles/blob/e48e4f0f3cc72f8f6ab7a0c025bd5304be24fb2d/claude/commands/socrates.md).
{{< /socrates-resources >}}
