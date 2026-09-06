+++
title = "Harmony"
description = "How Socrates keeps a specification coherent as its assumptions change."
date = "2026-09-06T18:22:16Z"
lastmod = "2026-09-06T18:58:54Z"
draft = false
diagrams = true
toc = false
+++

A specification can become incoherent one reasonable answer at a time.

I built **Socrates**, a Claude skill, to turn ambiguous intent into an execution-ready specification through dialogue. It investigates the problem, challenges my assumptions, tests interpretations, and makes success criteria and decision boundaries explicit. The goal is not a polished plan. It is a shared understanding that lets an agent do the intended work rather than execute the wrong task correctly.[^socrates]

**Harmony is one of the properties Socrates evaluates:** whether the specification avoids contradicting itself or creating inconsistency elsewhere. It concerns the relationships among the problem, requirements, assumptions, constraints, success criteria, and verification strategy—not just the quality of each section on its own.[^socrates]

A requirement can be clear while its acceptance test rewards the wrong behavior. A risk can appear acceptable while depending on a fallback that another decision removed. Each answer can sound reasonable in isolation. Together, they may no longer describe a viable task.

Socrates works on alignment with intent. Harmony asks whether the pieces of that understanding still fit together as the conversation changes. Coherence is necessary, but not sufficient: a consistent specification can still represent the wrong problem.

In [Close the Loop](/writing/close-the-loop/), I argued for feedback that tests the result against reality. Harmony addresses a complementary question inside the specification:

> **Do our requirements and checks still describe compatible ideas of success?**

This is not a new claim that systems need consistency. Modularity, interface theory, requirements engineering, and truth maintenance give us established ways to reason about different parts of the problem. Harmony is the name I use for bringing that concern into every pass of Socrates.

## What Unix already got right

There is an easy version of this argument that says Unix taught us to build small parts but forgot to make them work together.

That would be wrong.

The 1978 Unix foreword by McIlroy, Pinson, and Tague puts narrow purpose and composition next to each other. It says to make each program do one thing well, then immediately asks programmers to expect their output to become input to another, potentially unknown program. Composition was part of the idea, not an afterthought.[^unix]

I am not proposing that we add integration to a philosophy built around it.

What Harmony adds to my practice is a recurring obligation: **revisit the coherence of the composition as its parts evolve**. The amendment is to how I apply Unix's design discipline, not a claim that Unix's authors overlooked composition.

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

Interface theory gives this distinction a precise counterpart. In *Interface Automata* (2001), Luca de Alfaro and Thomas Henzinger model both a component's assumptions about incoming calls and its guarantees about outgoing calls, then check compatibility between components. Matching types alone does not establish that their interaction is valid.[^interfaces]

The retry example illustrates that concern; it is not an application of their formalism or a proof of this design.

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

There is a direct connection to Jon Doyle's *A Truth Maintenance System* (1979). Doyle's system records the reasons for beliefs so a reasoning program can revise them when discoveries contradict its assumptions. The dependency between a conclusion and its justification is part of what the system maintains.[^doyle]

Socrates does not implement Doyle's dependency-maintenance algorithm. It works through dialogue and a written specification. The related obligation is to reconsider an earlier conclusion when its supporting premise changes, rather than treating an old answer as permanently settled.

That is the role of Harmony here: keeping the specification's reasoning coherent, not merely keeping its terminology consistent.

## The property and the check

Harmony names the property. The recurring review is how the Socrates skill tries to preserve it.

Requirements engineering offers a particularly close antecedent. In *Leveraging Inconsistency in Software Development* (2000), Bashar Nuseibeh, Steve Easterbrook, and Alessandra Russo describe how specifications, code, tests, and other descriptions evolve separately. Inconsistencies can reveal missing knowledge and guide further elicitation; forcing immediate agreement can instead create premature commitment.[^inconsistency]

That is a useful distinction for Socrates. A contradiction is not something to smooth over so the plan reads well. It is something to bring back into the dialogue.

Most of the workflow's checks are revisited when the conversation touches them. Harmony is different. The instructions require it on every interrogation pass, whether or not consistency is the topic under discussion.

Its central question is:

> **What would this change break somewhere else in the spec that nobody is currently discussing?**[^socrates]

That last part is the point.

If we check consistency only when we already suspect a contradiction, we have made the check depend on noticing the very problem it is supposed to find.

In the retry example, shortening retention should reopen the retry promise, its acceptance tests, and any assumptions about migration—not just the storage paragraph. Socrates should ask whether the promise changes or another mechanism must preserve it. That decision belongs in the specification, not in an executor's silent interpretation.

The process records its assessment on each pass, along with the rationale and remaining uncertainty. Low-confidence items must be surfaced rather than silently assumed. Contradictions are to be resolved, bounded, or explicitly classified. The specification has an explicit freeze state and a path for reopening it when later evidence undermines its premises.[^socrates]

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

The inconsistency-management literature also permits deliberate deferral: detecting a conflict and deciding when to resolve it are different activities.[^inconsistency] For Socrates, recording an unresolved question is more honest than inventing agreement. It still needs a stated consequence and a decision about whether execution can safely proceed.

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

Harmony starts as a property of the specification Socrates is developing. Its broader lesson is a condition I would add to my working version of the Unix philosophy:

> **Do one thing well. Compose through clear interfaces. Preserve the coherence of the whole as the parts change.**

That applies to code, specifications, agent workflows, and organizations.

The question is not only whether this component works. It is whether its behavior still supports the agreements around it, whether previously settled conclusions remain justified, and whether any changed promises have actually been reconciled.

In Socrates, that means a new answer can reopen an old conclusion. Requirements, constraints, and acceptance criteria have to be reconciled before apparent clarity becomes execution commitment.

Close the loop so the system can detect failure. Use Harmony to keep the specification from sending its parts toward incompatible ideas of success.

[^unix]: M. D. McIlroy, E. N. Pinson, and B. A. Tague, *UNIX Time-Sharing System: Foreword*, Bell System Technical Journal 57(6), 1978, especially the Style section. [Original paper](https://www.tuhs.org/Archive/Documentation/Papers/BSTJ/bstj57-6-1899.pdf); [HTML transcription](https://danluu.com/mcilroy-unix/). The original explicitly discusses both narrow-purpose tools and composition.
[^parnas]: D. L. Parnas, *On the Criteria To Be Used in Decomposing Systems into Modules*, Communications of the ACM 15(12), 1972. [Publication](https://doi.org/10.1145/361598.361623); [transcription](https://www.cs.lafayette.edu/~gexia/cs301/resources/parnas.html), especially The Criteria and Conclusion.
[^join]: GNU Coreutils manual, [Pre-sorting for join](https://www.gnu.org/software/coreutils/manual/coreutils.html#Sorting-files-for-join). The manual requires consistent locales, fields, separators, and comparison options between the sorting and joining operations.
[^socrates]: My [Socrates instructions](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/commands/socrates.md), particularly the purpose, Harmony commandment, Commandment Scoring, and freeze/reopen semantics. These specify intended behavior; they do not themselves enforce every requirement.
[^verify]: My [verification instructions](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/commands/verify.md), Step 5: Harmony Cadence and Deferral. This is an audit procedure described in a command, not a claim of formal verification.
[^harmony-change]: [Add Harmony and per-commandment confidence scoring](https://github.com/lanej/dotfiles/commit/6d8710ec4151ddfc67b2995c87273fc2513ff260), September 3, 2026. The diff also aligns the orchestration vocabulary and adds the missing session-pointer writes. The article describes those recorded changes, not a new execution of that historical workflow.
[^interfaces]: Luca de Alfaro and Thomas A. Henzinger, *Interface Automata*, ESEC/FSE 2001, pp. 109–120. [Publication](https://doi.org/10.1145/503209.503226); [author-institution record and abstract](https://research-explorer.ista.ac.at/record/4622). This is a formal treatment of interaction assumptions, guarantees, and compatibility—not a claim that Socrates implements interface automata.
[^doyle]: Jon Doyle, *A Truth Maintenance System*, Artificial Intelligence 12(3), 1979, pp. 231–272. [Publication and abstract](https://doi.org/10.1016/0004-3702(79)90008-0). The connection is the maintenance of justifications as assumptions change, not an equivalence between a language-model review and Doyle's algorithm.
[^inconsistency]: Bashar Nuseibeh, Steve Easterbrook, and Alessandra Russo, *Leveraging Inconsistency in Software Development*, IEEE Computer 33(4), 2000, pp. 24–29. [Publication](https://doi.org/10.1109/2.839317); [author-hosted paper](https://www.cs.toronto.edu/~sme/papers/2000/IEEEComputer2000.pdf). See pp. 24–27 on evolving descriptions, useful inconsistency, and risk-based handling.
