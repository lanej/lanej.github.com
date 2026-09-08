+++
title = "Harmony"
description = "How Socrates keeps a specification coherent as its assumptions change."
date = "2026-09-06T18:22:16Z"
lastmod = "2026-09-07T14:40:00Z"
draft = false
+++

A specification can become incoherent one reasonable answer at a time.

I built **Socrates**, a Claude skill, to turn ambiguous intent into an execution-ready specification through dialogue. It investigates the problem, challenges assumptions, tests interpretations, and makes success criteria and decision boundaries explicit. The goal is a shared understanding that lets an agent do the intended work rather than execute the wrong task correctly.[^socrates]

Harmony is one of the properties Socrates evaluates: whether the problem, requirements, assumptions, constraints, success criteria, and verification strategy still describe the same task as the conversation changes.[^socrates]

A requirement can be clear while its acceptance test rewards the wrong behavior. A risk can look acceptable while depending on a fallback another decision removed. Each answer can make sense in isolation. Together, they may no longer describe a viable task.

In [Close the Loop](/writing/close-the-loop/), I argued for feedback that tests a result against reality. Harmony asks a complementary question inside the specification:

> **Do our requirements and checks still describe compatible ideas of success?**

## What Unix already got right

Unix already gives us narrow purpose and composition together. The 1978 foreword by McIlroy, Pinson, and Tague tells programmers to make each program do one thing well and to expect its output to become input to another program.[^unix]

The useful amendment for my own practice is temporal: composition has to remain coherent as its parts change.

A useful interface lets me ignore how another component works. It cannot let me ignore the promises I depend on.

That distinction matters in specifications too. The sections are separate because they serve different purposes, but the promises crossing those sections still have to agree.

## The contract between the contracts

Consider a simple job-processing system.

The client may retry a request for up to 24 hours. It uses the same request identifier each time. The service remembers completed identifiers for at least that long, so it can recognize a retry instead of performing the work again.

Now shorten the retention window to 15 minutes to reduce storage.

The service faithfully expires its records after 15 minutes. Its tests pass. The client faithfully retries within its 24-hour window. Its tests pass too.

But a retry arriving after the record expires can be treated as new work.

Both local rules are implemented correctly. The shared promise is broken.

{{< harmony-contracts >}}

The relationship that mattered was not the request shape. It was the relationship between the retry window and the lifetime of the service's memory.

Interface theory gives this distinction a formal counterpart. In *Interface Automata*, Luca de Alfaro and Thomas Henzinger model both a component's assumptions and guarantees, then reason about whether components are compatible.[^interfaces] I am borrowing the distinction, not claiming Socrates implements that formalism.

In the retry example, the deduplication window has to cover the retry window. Losing records, changing identifiers, and concurrent requests introduce other requirements, but the timing relationship alone is enough to show why two locally valid decisions can conflict.

The same conflict can exist before any code does. A requirement permits retries for 24 hours. A constraint permits retaining the necessary records for only 15 minutes. Someone has to change the design, change the promise, or reject the optimization.

## Untouched does not mean unaffected

The dangerous part of the retry example is the client. Nobody changed it.

A review focused on storage might examine memory usage, expiration behavior, and cleanup performance. All relevant. None tells us whether the client can still rely on the service.

The client's previous validation depended on an assumption about how long the service remembered requests. When that assumption changed, the justification changed too.

An unchanged component can lose its justification.

I think about conclusions in a design discussion the same way. We decide a requirement is feasible because a constraint holds. We accept a risk because a fallback exists. Later, the constraint changes or the fallback disappears, while the earlier conclusion remains marked as settled.

That conclusion is no longer settled for the same reasons.

Jon Doyle's *A Truth Maintenance System* records the reasons behind beliefs so they can be revised when assumptions change.[^doyle] Socrates does not implement Doyle's algorithm, but the practical obligation is similar: conclusions should not outlive the premises that justified them.

That is the part of Harmony I care about most. It is not terminology consistency. It is preserving the dependency between a decision and the reasons it was safe to make.

## The property and the check

Harmony names the property. The recurring review is how Socrates tries to preserve it.

Requirements engineering has treated inconsistency as useful information rather than merely a defect to erase. Nuseibeh, Easterbrook, and Russo describe evolving specifications, code, tests, and other descriptions that can disagree in ways that expose missing knowledge.[^inconsistency]

That fits the behavior I want from Socrates. A contradiction should reopen the discussion, not be smoothed over so the plan reads cleanly.

Most checks in the workflow are revisited when the conversation touches them. Harmony runs on every interrogation pass. Its useful question is:

> **What would this change break somewhere else in the spec that nobody is discussing?**[^socrates]

In the retry example, shortening retention should reopen the retry promise, its acceptance tests, and migration assumptions—not just the storage paragraph. Socrates should ask whether the promise changes or another mechanism must preserve it.

The process records a Harmony assessment on each pass, including rationale and uncertainty. Contradictions are resolved, bounded, or explicitly left open; a frozen specification can be reopened when later evidence undermines its premises.[^socrates]

{{< harmony-review >}}

That does not turn the process into a proof system. The verification procedure can check that Harmony was assessed and that required escalations have a recorded resolution.[^verify] It cannot prove that the assessment found every contradiction.

The benefit is narrower: the whole specification remains an explicit object of attention, and uncertainty is left visible instead of being converted into false consistency.

## The tools have to agree too

The change that introduced Harmony also corrected an inconsistency in the tooling itself.

The specification workflow represented an approved specification with a status of `Validated` and a separate `Frozen: true` flag. The orchestration instructions used a different vocabulary: they treated `Frozen` as the status to wait for.

The producer and consumer disagreed about the same state transition.

The same change aligned that vocabulary and repaired an active-session pointer expected downstream but not written upstream.[^harmony-change]

Those defects were small. They made the abstraction concrete: separate tools can each do their own job correctly while disagreeing about the protocol between them.

The fix did not copy the entire Harmony process into every command. Specification work kept the reasoning; critique and verification received checks appropriate to their roles; orchestration stayed narrow.[^harmony-change]

Preserving the whole does not mean making every part do everything. It means making responsibility for the relationships explicit.

## Make the review cheaper

If every small change required re-proving the entire system, independent development would disappear.

The practical answer is to make important relationships explicit enough that most checks can stay narrow.

Start with the promise. In the retry example, that is not "the expiration worker ran." It is "a permitted retry must not repeat completed work."

Name the assumptions that support it, then give the relationship a check. A test can complete a request, advance a controlled clock beyond the proposed retention window, retry within the client's allowed window, and verify that the work is not repeated. A configuration check can reject incompatible windows earlier.

Once the relationship is explicit, we do not have to rediscover it in every review.

The harder work is finding relationships we have not represented yet. That is where I still want people and AI reasoning across the changed boundary: which promises depend on this decision, which earlier conclusions may no longer hold, and who can authorize a revision?

Every-pass assessment does not mean exhaustive re-proving. The depth of investigation should follow the consequences of the change, not just the size of its diff.

If every small change genuinely affects everything, Harmony is not the root-cause fix. The boundaries probably need to change.

## The organizational version

The same failure appears in organizations.

Suppose a company wants teams to own outcomes but retains central approval for every consequential decision. Each manager can follow the process correctly. The accountability promise and authority model still do not fit together.

Or suppose a company promises faster delivery while adding review stages whose waiting time is excluded from the delivery target.

The question is the same as in the retry example: what has to remain true elsewhere for this local rule to work?

Local autonomy is more useful when teams know which promises they are free to change and which ones other teams rely on. Decomposition should reduce unnecessary coordination. It should not make necessary coordination ownerless.

## Preserve the whole

Harmony starts as a property of a Socrates specification. The broader rule I would add to my working version of the Unix philosophy is:

> **Do one thing well. Compose through clear interfaces. Preserve the coherence of the whole as the parts change.**

A new answer can reopen an old conclusion. A locally correct change can invalidate a neighboring promise. A component can remain untouched while the reasoning that justified it disappears.

The useful discipline is to make those relationships visible enough that stable ones become checks and unstable ones remain subjects for judgment.

Close the loop to detect whether the system worked. Use Harmony to keep its parts from pursuing incompatible definitions of success.

[^unix]: M. D. McIlroy, E. N. Pinson, and B. A. Tague, *UNIX Time-Sharing System: Foreword*, Bell System Technical Journal 57(6), 1978, especially the Style section. [Original paper](https://www.tuhs.org/Archive/Documentation/Papers/BSTJ/bstj57-6-1899.pdf); [HTML transcription](https://danluu.com/mcilroy-unix/).
[^socrates]: My [Socrates instructions](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/commands/socrates.md), particularly the purpose, Harmony commandment, Commandment Scoring, and freeze/reopen semantics. These specify intended behavior; they do not themselves enforce every requirement.
[^verify]: My [verification instructions](https://github.com/lanej/dotfiles/blob/74f56988ad1fa6debf3702c8b848e352e063761f/claude/commands/verify.md), Step 5: Harmony Cadence and Deferral.
[^harmony-change]: [Add Harmony and per-commandment confidence scoring](https://github.com/lanej/dotfiles/commit/6d8710ec4151ddfc67b2995c87273fc2513ff260), September 3, 2026.
[^interfaces]: Luca de Alfaro and Thomas A. Henzinger, *Interface Automata*, ESEC/FSE 2001, pp. 109–120. [Publication](https://doi.org/10.1145/503209.503226); [author-institution record and abstract](https://research-explorer.ista.ac.at/record/4622).
[^doyle]: Jon Doyle, *A Truth Maintenance System*, Artificial Intelligence 12(3), 1979, pp. 231–272. [Publication and abstract](https://doi.org/10.1016/0004-3702(79)90008-0).
[^inconsistency]: Bashar Nuseibeh, Steve Easterbrook, and Alessandra Russo, *Leveraging Inconsistency in Software Development*, IEEE Computer 33(4), 2000, pp. 24–29. [Publication](https://doi.org/10.1109/2.839317); [author-hosted paper](https://www.cs.toronto.edu/~sme/papers/2000/IEEEComputer2000.pdf).