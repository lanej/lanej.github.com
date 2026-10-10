+++
title = "Cheap Construction Is Not Progress"
description = "When construction is cheap, progress depends on what each attempt establishes: a useful outcome, or a better-informed decision about how to reach it."
date = "2026-10-02"
draft = true
+++

*Make it fail. Make it work. Make it simple. Make it fast.*

In Statecraft, the infrastructure-review workbench I’m building, an approval screen could be finished before the question behind it is answered: will execution apply the exact plan the reviewer approved? I want someone to understand a proposed change, make an informed decision, and have execution respect that decision. Recording an approval is only part of that outcome.[^statecraft-product]

I could keep improving the graph browser while leaving that guarantee unresolved. The artifact would become more convincing without answering the question that determines whether its approval workflow can be trusted. That is the murky middle: enough apparent success to invite more investment, without enough evidence to know what that investment is buying.

An experiment that exposes why the guarantee fails would give me a better next decision than a demo that avoids testing it. An understood failure can be more valuable than an unexplained success—not because failure is preferable, but because it gives us a better basis for the next decision.

There is a limit to that comparison. A solution that genuinely helps someone has value even before we can fully explain why it works. Not understanding why it works is different from not knowing whether it helps. During development, I need enough understanding to say what the result establishes, what remains uncertain, and what I should do differently because of it. A narrow result with demonstrated value is a success.

When an agent makes candidate solutions cheaper to construct, I can afford more experiments. Integration, review, and the consequences of mistakes remain expensive; the useful change is that some implementations become cheap enough to build and safely discard. Expensive construction never established usefulness either.

> **When output becomes cheaper, the ability to distinguish useful results from merely plausible artifacts becomes more consequential.**

That changes what I ask of each attempt. Early on, I am trying to resolve an uncertainty. Once I have demonstrated a useful result, I can preserve it while questioning the machinery and cost of delivering it.

## Find the first useful failure

For the approval workflow, the consequential assumption is that the execution boundary can preserve the identity of the reviewed plan. I want to challenge that before building everything around it.

The Statecraft mock workbench already invalidates earlier approvals when a new plan is created. Its evidence, decisions, and execution are simulated; it is not a live approval service.[^statecraft] That lets me investigate the intended behavior, but does not establish what the real execution system will do.

A proposed integration experiment would retain plan A, record an approval for A, produce plan B, and attempt to execute B using A’s approval. I would run it in an isolated environment and inspect both the decision and the artifact submitted for execution. The required result is rejection before B can execute.

If B executes, the approval guarantee has failed. If the system rejects it because the approval belongs to A, the implementation has survived this check. A failure caused by missing credentials answers neither question. I want to expose a consequential mistaken assumption, not merely get an error as quickly as possible.

This is the practical use of falsifiability: identify an observation that would force us to reject a specific claim. “Build a good approval workflow” leaves too much implicit. “An approval for one plan must not authorize another” gives the experiment something to contradict.

A steel thread is a narrow end-to-end path through the parts needed for a real use case.[^steel-thread] It is useful here because the uncertainty crosses an integration boundary. Sometimes a single API call or contract inspection answers the question more cheaply. The experiment needs to reach the uncertainty; mocking that boundary cannot resolve it.

I want the result to retain the identities, observations, and failures needed to explain what happened. “Validation failed” tells an agent little. Evidence that approval A was accepted for plan B identifies a discrepancy the next attempt must address. An unknown execution outcome must remain unknown until reconciled, rather than becoming success because no error was observed.

The agent can propose a change, run the experiment, and revise against that evidence. It is revising an implementation, not necessarily learning new model weights.[^reflexion] The value comes from feedback outside the agent’s own account of why its work should be accepted.

An understood failure now changes the work. I might need an exact-artifact check at execution, a different integration path, or a narrower product commitment. More polishing would not resolve any of those decisions. Passing this experiment gives me a reason to continue, but it still leaves a separate question: does the resulting capability help a reviewer?

## Reach the first meaningful success

Correct behavior is necessary for this workflow, but it is not sufficient evidence of its usefulness. A system could prevent stale approvals and still make changes harder to understand.

I would evaluate that second claim with a bounded review task. Give reviewers representative changes and ask them to identify consequential effects, explain the evidence behind their conclusions, and decide what needs further investigation. Compare that with how they perform the same kind of work using their existing tools. Use different, comparable cases so simply remembering a change does not masquerade as an improvement.

Useful evidence might be a consequential change caught that the existing workflow missed, or a comparably sound decision reached with less effort. Faster approval alone would not establish improvement; it might mean the reviewer saw less. These are proposed evaluations for Statecraft, not results I have already demonstrated.

This is the distinction between testing a mechanism and evaluating an outcome. Both matter. The integration experiment tests whether execution respects the decision. The review task tests whether the workbench helps someone make that decision. Evidence for one cannot silently stand in for the other.

A read-only slice could therefore be a meaningful first success. It might help a reviewer understand changes without yet supporting approval or execution. That would not establish the complete product, but it could establish a useful result worth preserving. This is how I want to choose vertical slices: complete a bounded job, rather than finish a horizontal layer and assume its value will emerge later.

Viewrule, my tool for design guidance and executable UI constraints, illustrates why the evaluator must stay connected to that job. It checks rendered interfaces against declared requirements and separates executed checks from unassessed design requirements. A pass means the configured checks passed, not that the interface has been proven good.[^viewrule]

Suppose I require eight alternatives to be visible together. An agent might satisfy the count while making the labels unreadable. The purpose was to help someone compare alternatives, not put eight rectangles on screen. The check needs scrutiny as well as the implementation: known-bad cases it rejects, useful cases it accepts, and an explicit account of what remains for human assessment. Changing a requirement should be a visible decision, not a way for the implementation to grade itself more generously.

Understanding success does not require a complete causal explanation of every part of the system. It requires enough evidence about the task, conditions, and limits to use the result deliberately. One successful review does not establish reliability across all reviewers or changes. It gives us a starting point for repetition and variation.

Keep the cases, observations, and checks that support that result. If a later revision looks cleaner but causes a reviewer to miss an important change, the earlier evidence gives us a reason to reject it. We have something more useful than a version we happen to like: we know what the next version needs to preserve.

## Remove what success does not require

Once I have that baseline, I want to know how much of the implementation was necessary. A first success usually contains decisions made before I understood the problem this well.

This is where “make it good” often becomes “make it simple.” Remove machinery while preserving the useful result and its essential constraints. Less output can be progress.

In the Statecraft approval slice, imagine that the application translates a planner response into a generic execution record, then translates it again into the proposal a reviewer sees. I would try removing the intermediate representation and mapping directly to the review model. That is a proposed simplification, not a description of a refactoring already completed.

The experiment has obligations: preserve plan identity and source evidence, keep stale-approval rejection intact, and retain the information reviewers need. If the direct mapping does that with fewer concepts to trace, the intermediate model may not earn its cost. If removing it spreads provider-specific behavior through the review logic or makes failures harder to reproduce, the layer may be doing useful work.

This is the architectural question I care about here. A clean core is not enough if all the complexity has moved into translation around it. Nor does the shortest implementation necessarily make the whole system easier to change. The comparison has to include the complete workflow.

Passing the existing tests is evidence, not permission to delete anything they happen not to exercise. An authorization check may look unnecessary until an unauthorized caller arrives. Before removing a boundary, identify the property it is meant to protect and challenge the replacement on that property.

Understanding the successful path makes this subtraction more deliberate. I can distinguish a requirement from a workaround and test whether something I thought was necessary was merely incidental. When a simplification fails, restore the behavior and retain the case that explains why. When it succeeds, the system delivers the same value with less machinery to maintain.

## Optimize what remains

Now I have a useful result, evidence about its limits, and an implementation whose complexity I have questioned. Performance work has a clearer target.

Suppose reviewers can identify the relevant changes, but loading a large proposal takes long enough to interrupt the task. I can measure that delay and test a faster implementation against the same evidence. The objective is to reduce the cost of delivering the outcome, not improve a latency number by omitting part of the proposal. Faster execution cannot compensate for applying an unapproved plan, either; some requirements remain constraints rather than penalties to average away.

These phases change the emphasis of the work, not the order in which all requirements are considered. If the required latency determines whether a task is viable, it belongs in the first experiment. Additional machinery can be justified when it buys a measured improvement that the simpler version cannot deliver.

Each new slice can introduce uncertainty and send us back through the loop. Iteration does not guarantee convergence. When attempts stop changing our understanding or improving the result, I need to revisit the experiment, change the approach, or stop. Cheap compute does not remove the budget for time, attention, and consequences.

## What the next attempt is for

The approval screen is still an output. What matters is whether a reviewer can use it to make an informed decision and whether execution respects that decision. An understood failure helps by showing what must change. An understood success gives us a result we can preserve, repeat, and simplify with less guesswork.

Neither understanding nor a passing check makes the problem worth solving. That judgment determines which outcomes and uncertainties deserve our attention in the first place. Cheaper construction gives it more leverage, not less.

I want each attempt to do one of two things: improve the outcome or improve a consequential decision about how to reach it. When it does neither, producing it faster is not progress.

[^statecraft-product]: **[Statecraft README](https://github.com/lanej/statecraft/blob/main/README.md)**

    Product intent and the jobs of understanding a change, making a review decision, preserving approval identity, and verifying execution. These are intended capabilities; the repository identifies the workbench as an early prototype.

[^statecraft]: **[Statecraft mock review workbench](https://github.com/lanej/statecraft/blob/main/docs/steel-thread.md)**

    “Evidence and decisions” describes invalidation after replanning. The workbench’s evidence, identities, decisions, and execution are simulated. The integration and reviewer evaluations in this essay are proposed experiments, not production guarantees or reported study results.

[^steel-thread]: **[Steel threads are a technique that will make you a better engineer](https://www.rubick.com/steel-threads/)**  
    Jade Rubick

    The narrow end-to-end construction technique. Using it to seek an informative failure is this essay’s framing, not a requirement that every steel thread must fail first.

[^reflexion]: **[Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)**  
    Noah Shinn and colleagues · 2023

    A related example of feedback-guided iteration using retained reflective text rather than changes to model weights. It does not establish the effectiveness of the proposed Statecraft experiments.

[^viewrule]: **[Viewrule README](https://github.com/lanej/viewrule/blob/main/README.md)**

    “Why it exists,” “Define boundaries before building,” and “What it detects” describe configured UI checks and their limits. The tool distinguishes executed checks from unassessed design requirements; measurements are not a universal aesthetic score.
