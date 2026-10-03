+++
title = "Cheap Construction Is Not Progress"
description = "Cheaper output is not an outcome. Informative failure, meaningful success, and deliberate simplification help distinguish useful results from merely plausible artifacts."
date = "2026-10-02"
draft = true
+++

*Make it fail. Make it work. Make it simple. Make it fast.*

In Statecraft, a working approval screen would not, by itself, establish that the infrastructure someone reviewed is what gets applied. Recording a decision is an output. The outcome I want is for a reviewer to understand a proposed change and trust that execution respects the decision.[^statecraft-product]

That is the distinction I care about: output versus outcomes. Expensive construction does not establish progress either. Cheaper construction changes how many candidates I can afford to try, not what counts as a useful result.

> **When output becomes cheaper, the ability to distinguish useful results from merely plausible artifacts becomes more consequential.**

When producing a candidate solution is expensive, there is a strong incentive to reason carefully before committing to construction. When that cost falls, construction itself can become a way of reasoning. Build the smallest useful experiment, observe what it establishes, and use the result to decide what to try next.

That does not mean software costs only compute. Integration, review, migration, operations, and the consequences of mistakes still belong in the bill. The useful change is narrower: when a candidate is cheap enough to construct and safely discard, we can afford to use implementations as experiments.

The extra attempts help only if we can distinguish evidence of progress from the appearance of it.

## The murky middle

The result I find hardest to evaluate is something that works well enough to keep investing in, but has not established that the investment is worthwhile. That is the murky middle.

A working demo and a passing test suite can establish that particular behavior is possible without establishing that it improves the problem we intended to solve. The danger is treating evidence for that narrower claim as permission to invest in the whole approach. We add supporting infrastructure and polish the interface while the consequential assumption remains untested.

For Statecraft, an experiment showing that an old approval can authorize a different plan would give me a specific reason to reject the current design. A convincing demo that never attempts that transition gives me less reason for confidence, even if it looks more successful.

Clear, informative failure can be more useful than ambiguous success. It changes the next decision. Ambiguous success can instead let the original assumption survive without earning confidence.

This is an argument for decisive evidence, not perfection. A read-only slice that demonstrably helps someone understand an infrastructure change could be a useful partial success, even without approval or execution. Its scope is limited; its value need not be ambiguous. The problem is not that a solution does only part of the job. It is that we cannot say whether the part it does matters.

Failure is not the outcome, either. Learning counts as progress when it changes a consequential decision: which approach to pursue, what requirement to revise, or whether to continue. “We learned something” is not an indefinite substitute for improving the problem.

The iteration I want moves us out of that ambiguity. Early attempts challenge the approach. A first meaningful success establishes something worth preserving. Simplification and performance work then improve how we deliver it.

## Make wrongness observable

My shorthand for this has been:

> I don’t need the model to know that it’s right. I need the system to know when it’s wrong.

The second sentence needs a boundary. I am not assuming an evaluator that can recognize every possible failure. What I want is to make specific, consequential claims rejectable by evidence.

“Build a good approval workflow” is an instruction. “An approval for one infrastructure plan must not authorize a different plan” is a property I can challenge.

“Improve this layout” is an aspiration. “Keep the required alternatives visible and legible at this viewport” gives me something I can inspect.

This is the practical meaning of falsifiability here: before accepting a claim, identify an observation that would force us to reject it. Tests are one way to do that. So are measurements, external responses, operational observations, and human review. Falsification is not a replacement for testing; it is a way of deciding what the tests should be capable of contradicting.

Viewrule, a tool I’m building for design guidance and executable UI constraints, makes this distinction explicit. It checks rendered interfaces against declared requirements and reports evidence. It also separates executed checks from unassessed design requirements. A pass means the configured checks passed—not that the design has been proven good.[^viewrule]

That limitation is useful. It lets me delegate a bounded claim without pretending I have delegated all judgment.

It also makes failure useful to the next attempt. “The layout is bad” does not tell an agent much. “Only five of the eight required alternatives are fully visible” identifies a discrepancy it can investigate.

Failure earns its cost when it informs the next decision. Repetition can help measure reliability. But repeating a known failure without changing our understanding or our approach is a loop that has not learned how to use its feedback.

## Find the first useful failure

Before I have a working solution, the most valuable question is often: **which assumption is most likely to make this approach unworkable?**

This is where a steel thread is useful: a narrow end-to-end path through the parts of a system needed for a real use case.[^steel-thread] I want that path to expose an important uncertainty before I invest in everything around it.

For Statecraft, my experimental infrastructure-review workbench, the intended workflow includes approving the exact plan that will be applied. Its current prototype exercises that workflow with simulated evidence and execution; it is not a production approval service.[^statecraft]

Consider the integration question behind that requirement: can the execution system apply the exact artifact the reviewer inspected, or does it produce something new at execution time?

That question should shape an early experiment. It should not wait behind a finished graph browser, a generalized integration framework, and a polished approval screen. If the execution boundary cannot preserve the required identity, an important part of the design has to change.

The goal is not to make something fail arbitrarily. A missing semicolon is a fast failure, but it tells me little about whether the approach is viable. I am optimizing for the first *informative* failure: evidence that exposes a consequential mistaken assumption.

Sometimes the cheapest experiment is a steel thread. Sometimes it is a single API call, a contract inspection, or a small disposable program. The experiment needs to cross the boundary where the uncertainty lives. Mocking that boundary can help test our own logic, but it cannot establish that the real dependency behaves as assumed.

Nor do I need to manufacture a failure. If a serious attempt to challenge the assumption succeeds, that is useful evidence too.

“Make it fail” is shorthand for **give the idea an early opportunity to be disproved**. Do that in an environment where the cost of being wrong is bounded.

## Reach the first meaningful success

Once an approach survives those initial challenges, the objective changes. I want one complete path that demonstrably improves the problem under stated conditions. The outcome can be narrow; the evidence should make clear what it establishes.

Not a collection of components that each look reasonable. Not a demonstration that succeeds only because the interesting behavior was mocked out. An end-to-end result, with an honest account of what it establishes and what remains untested.

This is how I want to organize vertical slices. A slice should answer a user’s question or complete an action. “Build the persistence layer” is enabling work. “Record a review decision and retrieve it with its original evidence after a restart” is a result we can evaluate.

In Statecraft’s simulated workflow, a new plan invalidates earlier approvals even when the commit has not changed. It also records agreement with the simulated resulting state separately from command success.[^statecraft]

Those distinctions make useful acceptance conditions. In a corresponding live slice, I would want to challenge them directly: approve one proposal, produce another, and attempt to use the old decision. The wrong transition should be rejected, with enough evidence to explain why.

A first success is not production readiness. One successful run does not establish reliability, security, or behavior under concurrency. But it gives us a demonstrated path and a body of evidence to extend.

That evidence is the important asset. Keep the inputs, the conditions, the result, and the checks that distinguish success from the failure we were worried about.

The implementation may be disposable. The lesson should not be.

## Remove what success does not require

After the first success, continuing to add machinery is not necessarily progress. The next useful question is often: **what can I remove while preserving the properties that matter?**

This is where “make it good” becomes “make it simple.” If I can preserve the outcome while removing code, configuration, or layers, less output is progress.

Conceptually:

\[
\min \operatorname{Complexity}(x)
\quad\text{subject to the required behavior and constraints still holding.}
\]

That is not a claim that complexity has one objective numerical score. It is a direction for the next set of experiments. Remove a translation. Collapse a layer. Eliminate an unnecessary configuration option. Replace a generalized mechanism with the direct operation the workflow actually needs.

Then challenge the result again.

This is also how I want to approach pragmatic hexagonal architecture. The useful question is not whether the core has been insulated from every named external system. It is whether the boundaries make the whole workflow easier to understand, change, and evaluate.

In a Statecraft review-comment slice, I would be comfortable with an application workflow knowing that it is publishing to GitHub. The rule governing which plan the comment refers to does not need to know the GitHub API. Those are different responsibilities, but separating them does not require a universal abstraction for every possible discussion platform.

The opposite mistake is deleting a useful boundary because the happy-path test still passes. An authorization check may look unnecessary until an unauthorized caller arrives. An adapter may earn its place by making a failure reproducible. A layer may contain a dependency that would otherwise spread throughout the application.

So subtraction needs design judgment as well as tests. **The smallest implementation is not necessarily the simplest system to operate or change.** Nor do passing checks prove that a deletion is safe; they establish only that the deletion survived those checks.

The exercise is to make each piece of machinery justify its cost against an actual requirement—not an imagined future need, and not an architectural slogan.

If an abstraction exists to make substitution easier, try a representative substitution. If it exists to isolate failure, demonstrate that isolation. Inspect the orchestration and translation costs as well as the clean core.

A boundary earns its place when it helps the whole system, not merely when it makes one part look better.

## Optimize what remains

Once the behavior is established and avoidable complexity has been challenged, performance becomes a more focused problem.

Now I can ask whether an implementation reduces latency, memory use, or operating cost while preserving the properties established earlier. I have a baseline to compare against and a clearer understanding of what cannot be traded away.

This is a change in emphasis, not a waterfall. If the required latency determines whether the product is viable, latency belongs in the first experiment. If handling a particular volume is essential, a single-item demonstration is not a meaningful first success.

Likewise, the simplest implementation may not meet the performance requirement. Additional machinery can be justified. It should buy a measured benefit rather than satisfy a speculative concern.

The sequence is therefore not “ignore performance until the end.” It is **do not optimize an implementation before you know which properties make it worth keeping**.

Each new vertical slice can move through these phases again. A new dependency introduces uncertainty. A new behavior requires a first success. That success creates another opportunity to simplify.

## We are changing the optimization problem

I initially thought about this as driving error toward zero. That is useful, but incomplete. The objective changes as the work progresses.

Early on, I care about reducing consequential uncertainty per unit of time and risk. Then I care about finding a feasible solution. After that, I care about reducing unnecessary complexity. Finally, I optimize operational properties within the constraints I have established.

These are related optimization problems, not one fixed score that improves monotonically. A failed experiment may make the current implementation worse while improving the next decision. A simplification may leave every user-visible behavior unchanged and still reduce the burden of maintaining it.

There is a family resemblance to model training. Reinforcement-learning fine-tuning uses feedback to update model parameters. An agent’s development loop can instead update the candidate implementation and retained context, without changing the model’s weights. Feedback-driven improvement without weight updates is also explored explicitly in work such as Reflexion.[^reward][^reflexion]

The resemblance includes a failure mode: optimizing the measurement instead of the intended outcome. Research on reward-model overoptimization has demonstrated that, in a controlled synthetic setup, improving a proxy reward can eventually degrade the reference reward it was meant to represent.[^reward]

For an engineering example, imagine requiring eight visible rows. An agent could satisfy a count while making the labels unreadable. The count was not the purpose. The purpose was to let someone compare eight alternatives.

The evaluator therefore needs scrutiny too. I want known-bad cases that it rejects, representative good cases that it accepts, and explicit limits on what it assesses. When requirements change, that should be a visible decision—not an implementation quietly making its own test easier to pass.

Some requirements should not be folded into a score at all. Faster execution cannot compensate for applying an unapproved infrastructure change. That is a constraint, not a penalty to average away.

Falsifiability tells me how a claim can lose. It does not guarantee that the next attempt will be better, that the search will converge, or that the thing I am measuring is the thing I actually need.

In practice, I need an acceptable outcome within a finite budget. If the loop stops producing useful evidence, I need to change the experiment, revisit the assumptions, or stop—not purchase more repetitions of the same mistake.

## The question before the construction

A system can converge beautifully on an irrelevant objective. A test suite can become entirely green while the user’s actual problem remains unsolved. Nothing about cheaper construction resolves that gap.

For Viewrule, the point is not to maximize visible rows or fill a viewport. It is to help someone use the interface to make a decision. Its measurements are bounded checks in support of that purpose, not a universal aesthetic score.[^viewrule]

That purpose determines what evidence is worth collecting. It also tells me when a technically successful experiment is answering the wrong question.

This does not make implementation expertise obsolete. Understanding how systems work helps us choose revealing experiments, recognize incomplete evidence, and distinguish an essential constraint from an accidental limitation.

What changes is its leverage. When I can cheaply construct several candidates, knowing how to build one is no longer enough to decide which deserves to survive.

I need to know what problem I am solving, why it matters, what would invalidate my approach, and what evidence would justify the next investment.

I want each attempt to do one of two things: improve the outcome or improve a consequential decision about how to reach it. When it does neither, producing it faster is not progress.

[^viewrule]: [Viewrule README](https://github.com/lanej/viewrule/blob/main/README.md), especially “What it detects,” “Define boundaries before building,” and the scope of composition measurements. The repository describes the tool as experimental.

[^steel-thread]: Jade Rubick, [“Steel threads are a technique that will make you a better engineer”](https://www.rubick.com/steel-threads/). Used here for the narrow end-to-end construction technique; the emphasis on seeking an informative failure is this article’s framing.

[^statecraft]: [Statecraft mock review workbench](https://github.com/lanej/statecraft/blob/main/docs/steel-thread.md), especially “Evidence and decisions” and “Production work still required.” All execution and evidence in this workbench are simulated; it is not a deployable approval service.

[^statecraft-product]: [Statecraft README](https://github.com/lanej/statecraft/blob/main/README.md), especially the product intent, lifecycle, and distinction between command success and verification.

[^reward]: Leo Gao, John Schulman, and Jacob Hilton, [“Scaling Laws for Reward Model Overoptimization”](https://proceedings.mlr.press/v202/gao23h.html), ICML 2023. The experimental reference reward is another model, not a direct measurement of real-world human outcomes.

[^reflexion]: Noah Shinn and colleagues, [“Reflexion: Language Agents with Verbal Reinforcement Learning”](https://arxiv.org/abs/2303.11366), 2023. The framework uses feedback and retained reflective text rather than updating model weights.
