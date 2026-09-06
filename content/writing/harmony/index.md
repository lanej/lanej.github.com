+++
title = "Harmony"
description = "Do one thing well. Keep the whole coherent."
date = "2026-09-06T18:22:16Z"
draft = false
diagrams = true
toc = false
+++

A system can become less coherent one reasonable change at a time.

A retry policy becomes more forgiving. A storage policy becomes more economical. Each change makes sense to the person responsible for it. Together, they can break a guarantee neither person intended to change.

I like small, composable tools. I like clear boundaries, narrow responsibilities, and mechanisms I can understand without loading an entire system into my head.

But decomposition does not remove responsibility for what the pieces create together.

In [Close the Loop](/writing/close-the-loop/), I argued that AI needs feedback from the environment, and that we should turn repeated, mechanically checkable work into software. This is the next question:

> **Do the things we have made reliable still form a coherent whole?**

I have started calling that property **Harmony**. Not agreement. Not uniformity. The compatibility of a system's requirements, assumptions, and behavior as the system changes.

The rule is simple:

> **A local change is not complete until its consequences for the whole have been reconciled.**

## What Unix already got right

There is an easy version of this argument that says Unix taught us to build small parts but forgot to make them work together.

That would be wrong.

The 1978 Unix foreword by McIlroy, Pinson, and Tague puts narrow purpose and composition next to each other. It says to make each program do one thing well, then immediately asks programmers to expect their output to become input to another, potentially unknown program. Composition was part of the idea, not an afterthought.[^unix]

I am not proposing that we add integration to a philosophy built around it.

I am proposing that we make one responsibility explicit: **preserving the coherence of the composition as its parts evolve**.

A useful interface lets me ignore how another component works. It cannot let me ignore the promises I depend on.

Parnas's work on modularity makes a related distinction. His argument was not simply to divide a program into smaller processing steps. It was to organize modules around design decisions that could be hidden from other modules, so those decisions could change without forcing changes everywhere else.[^parnas]

That is the independence I want. Hide the implementation. Make the externally significant assumptions legible.

Harmony is an extension of that discipline, not a reason to abandon it.

## The contract between the contracts

Consider a simple, hypothetical job-processing system.

The client may retry a request for up to 24 hours. It uses the same request identifier each time. The service remembers completed identifiers for at least that long, so it can recognize a repeat instead of performing the work again.

Now shorten the retention window to 15 minutes to reduce storage.

The service faithfully expires its records after 15 minutes. Its tests pass. The client faithfully retries within its 24-hour window. Its tests pass too.

But a retry arriving after the record expires can be treated as new work.

The implementation of each local rule may be correct. The rules no longer support the shared promise.

{{< harmony-contracts >}}

The relationship that mattered was not merely the shape of the request. It was the relationship between the retry window and the lifetime of the service's memory.

For this design, the deduplication window has to cover the retry window. That is a necessary condition for the promise, not a complete proof of correctness. Losing records, changing identifiers, and concurrent requests would still need their own treatment.

This is not foreign to Unix, either. GNU's documentation for `sort` and `join` explicitly requires consistent sorting conventions when their outputs and inputs are composed: the relevant fields, comparison options, and locale have to agree.[^join]

A common transport makes connection possible. It does not supply every agreement the connection needs.

The same problem can occur in a specification, before any code exists. A requirement permits retries for 24 hours. A constraint permits retaining the necessary records for only 15 minutes. No amount of faithful implementation reconciles that conflict on its own.

Someone has to change the design, change the promise, or reject the proposed optimization.

## Untouched does not mean unaffected

The dangerous part of the retry example is the client.

Nobody changed it.

A review focused on the storage change might examine memory usage, expiration behavior, and cleanup performance. All relevant. None sufficient to establish whether the client can still rely on the service.

The client's previous validation rested on an assumption about how long the service remembered requests. When that assumption changed, the justification changed too.

> **An unchanged component can lose its justification.**

I think the same way about conclusions in a design discussion.

We decide a requirement is feasible because a constraint holds. We settle an ownership question because a team has a particular capability. We accept a risk because a fallback exists.

Later, we change the constraint, remove the capability, or discard the fallback. The earlier conclusion may remain untouched in the document, marked as settled.

It is no longer settled for the same reasons.

This is why checking the changed paragraph is not enough. We have to revisit conclusions that depend on it, including ones that are no longer receiving attention.

Harmony is partly a discipline for invalidating stale confidence.

## The rule that runs on every pass

This is what I built into Socrates, my workflow for developing specifications through dialogue.

Socrates is not just a reviewer that looks for defects in a finished plan. It interrogates the interpretation of the task: what problem we are solving, which assumptions we are making, what counts as success, what is excluded, and who has authority to decide unresolved questions. It is meant to sharpen my understanding as well as the agent's.[^socrates]

A plausible specification is not enough. It has to represent the intended problem, rather than an adjacent problem the agent finds easier to solve.

Most of the workflow's checks are revisited when the conversation touches them. Harmony is different. The instructions require it on every interrogation pass, whether or not consistency is the topic under discussion.

Its central question is:

> **What would this change break somewhere else in the spec that nobody is currently discussing?**[^socrates]

That last part is the point.

If we check consistency only when we already suspect a contradiction, we have made the check depend on noticing the very problem it is supposed to find.

The process records the assessment on each pass, along with its rationale and remaining uncertainty. Unresolved low-confidence items are supposed to come back into the dialogue, not disappear into an assumption the agent silently adopts. The specification has an explicit freeze state and a path for reopening it when later evidence undermines its premises.[^socrates]

{{< harmony-review >}}

There is an important limit here. These are instructions for a reasoning process, not a proof system.

The verification procedure calls for checking that every pass has a Harmony entry and that required escalations have a recorded resolution. That makes omissions auditable from the specification itself.[^verify]

It does not establish that the assessment was good. A complete table proves that a review was recorded, not that the reviewer found every contradiction. A confidence score is a judgment, not a calibrated probability of correctness.

The benefit is narrower and useful: the workflow makes the whole specification an explicit object of attention, and leaves a record of what remains uncertain.

## The tools have to agree too

The change that introduced Harmony also corrected an inconsistency in the tooling itself.

The specification workflow represented an approved, frozen specification with a status of `Validated` and a separate `Frozen: true` flag. The orchestration instructions used a different vocabulary: they treated `Frozen` as the status to wait for.

The producer and consumer were not describing the same state transition.

That commit aligned the orchestration instructions with the specification lifecycle. It also repaired an active-session pointer that downstream commands expected but the upstream workflow did not write.[^harmony-change]

These were small defects. They illustrate a larger problem.

The files were separate because the tools had different jobs. That was reasonable. But the shared protocol still needed one meaning.

There is also a useful restraint in the same change: the full Harmony assessment was not copied into the orchestration command. Specification work owned the reasoning; critique and verification received checks appropriate to their roles; orchestration kept its narrower job.[^harmony-change]

Preserving the whole does not mean making every part do everything.

It means assigning responsibility for the relationships, as deliberately as we assign responsibility for the parts.

## Harmony is not uniformity

The name can sound softer than the rule.

Harmony is not asking everyone to agree, standardizing every tool, or insisting that every service use the same architecture. Different parts can have different requirements. An explicit tradeoff is not a contradiction simply because it makes one local metric worse.

In the retry example, shortening retention might be the right decision. Perhaps the product no longer needs a 24-hour retry promise. Perhaps a different mechanism can preserve it.

But that is a change to the system's contract. It needs to be made deliberately, reflected in the affected clients and documentation, and introduced with an appropriate transition.

It cannot be smuggled in as storage cleanup.

The distinction is between an intentional change to an agreement and an accidental violation of it.

Nor does Harmony mean preserving every historical behavior. Some assumptions should be retired. Some interfaces should break. Some capabilities should disappear.

The obligation is to reconcile the consequences, not to forbid the change.

And coherence is not the same as correctness. A system can be entirely consistent about doing the wrong thing. Harmony does not replace validating the goal or observing what actually happens.

## Make the review cheaper, not optional

An obvious objection is cost. If every change requires reviewing the entire system, independent development disappears.

I do not want that either.

The practical answer is to make the important relationships explicit enough that most changes can be checked narrowly.

Start with the promise. In the retry example, that is not "the expiration worker ran." It is "a permitted retry must not repeat completed work."

Name the assumptions that support it. Identify which client behavior, stored state, and timing rules have to remain compatible.

Then give the relationship a check. A test can complete a request, advance a controlled clock beyond the proposed retention window, retry within the client's allowed window, and verify that the work is not repeated. A configuration check can catch incompatible window settings earlier. Neither replaces the other.

Once that relationship is explicit, it is no longer necessary to rediscover it in every review. The system can make a previously subtle contradiction conspicuous.

The harder part is finding relationships we have not yet represented. That is where I want people and AI to reason across the changed boundary: which promises depend on this decision, which earlier conclusions may no longer hold, and who can authorize a revision?

Every-pass assessment does not mean exhaustive re-proving. It means not treating the untouched parts as automatically irrelevant. The depth of investigation should follow the consequences of the change, not just the size of its diff.

This is where Harmony connects back to Close the Loop. Use judgment to discover an important relationship. Turn the stable, testable part into a check. Keep judgment for what the check cannot settle.

If every small change genuinely affects everything, repeated review is not the root-cause fix. The boundaries themselves may need to change.

## The organizational version

The same reasoning applies to how I think about organizations.

Suppose a company wants teams to own outcomes, but retains central approval for every consequential decision. Each manager may follow the process correctly. The accountability promise and the authority model still do not fit together.

Or suppose a company promises faster delivery while adding review stages whose waiting time nobody includes in the delivery target.

Those are hypothetical examples, but they expose the same design question as the retry window: what has to be true elsewhere for this local rule to work?

The answer is not necessarily a central committee. It might be a clearer decision boundary, an explicit service commitment, or a shared measure of the outcome that crosses teams.

Local autonomy is more useful when teams know which promises they are free to change and which promises other teams rely on.

Decomposition should reduce unnecessary coordination. It should not make necessary coordination ownerless.

## Preserve the whole

The amendment I would add to my working version of the Unix philosophy is not a rejection of small tools.

It is a condition on finishing a change:

> **Do one thing well. Compose through clear interfaces. Preserve the coherence of the whole as the parts change.**

That applies to code, specifications, agent workflows, and organizations.

The question is not only whether this component works. It is whether its behavior still supports the agreements around it, whether previously settled conclusions remain justified, and whether any changed promises have actually been reconciled.

Close the loop so the system can detect failure.

Preserve harmony so its parts are not faithfully implementing incompatible ideas of success.

[^unix]: M. D. McIlroy, E. N. Pinson, and B. A. Tague, *UNIX Time-Sharing System: Foreword*, Bell System Technical Journal 57(6), 1978, especially the Style section. [Original paper](https://www.tuhs.org/Archive/Documentation/Papers/BSTJ/bstj57-6-1899.pdf); [HTML transcription](https://danluu.com/mcilroy-unix/). The original explicitly discusses both narrow-purpose tools and composition.
[^parnas]: D. L. Parnas, *On the Criteria To Be Used in Decomposing Systems into Modules*, Communications of the ACM 15(12), 1972. [Publication](https://doi.org/10.1145/361598.361623); [transcription](https://www.cs.lafayette.edu/~gexia/cs301/resources/parnas.html), especially The Criteria and Conclusion.
[^join]: GNU Coreutils manual, [Pre-sorting for join](https://www.gnu.org/software/coreutils/manual/coreutils.html#Sorting-files-for-join). The manual requires consistent locales, fields, separators, and comparison options between the sorting and joining operations.
[^socrates]: My [Socrates instructions](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/commands/socrates.md), particularly the purpose, Harmony commandment, Commandment Scoring, and freeze/reopen semantics. These specify intended behavior; they do not themselves enforce every requirement.
[^verify]: My [verification instructions](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/commands/verify.md), Step 5: Harmony Cadence and Deferral. This is an audit procedure described in a command, not a claim of formal verification.
[^harmony-change]: [Add Harmony and per-commandment confidence scoring](https://github.com/lanej/dotfiles/commit/6d8710ec4151ddfc67b2995c87273fc2513ff260), September 3, 2026. The diff also aligns the orchestration vocabulary and adds the missing session-pointer writes. The article describes those recorded changes, not a new execution of that historical workflow.
