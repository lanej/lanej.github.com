+++
title = "Lead With Problems"
description = "A problem statement is not enough. Ownership, authority, and accountability have to follow it."
date = "2026-09-06T23:29:00Z"
lastmod = "2026-09-07T00:06:30Z"
draft = false
toc = false
+++

If I ask a team to build a dashboard, I have already made several decisions.

I have decided that the problem is missing information. That a dashboard is the right way to provide it. That someone will use the information to make a better decision. And that building software is worth more than the other things the team could do.

Perhaps all of that is true. But if I only communicate the solution, those assumptions arrive as instructions.

The team can execute perfectly without testing any of them.

I want the organization to distinguish what we know needs to change from what we currently think might change it.

Marty Cagan makes this distinction in his writing about empowered product teams: their responsibility is to find a solution that produces a useful outcome, not merely implement a feature someone else selected.[^teams]

That requires more than a better problem statement. The funding, decision rights, and definition of success cannot still belong to a predetermined solution.

**The problem has to become the unit of ownership, not just the opening paragraph of a project brief.**

## A missing solution is not a problem statement

“We don't have a dashboard” describes an absence. It does not establish that the absence matters.

Consider a hypothetical business where new customers stall between signing a contract and completing their first successful transaction. Someone asks for an onboarding dashboard.

The delay could come from unclear requirements, slow access approvals, an unreliable integration, or a handoff nobody owns. A dashboard could make it more visible without making it shorter.

Start with who is getting stuck, where they wait, and what we have observed. The dashboard is a hypothesis. So are changing a policy, improving documentation, and eliminating a handoff.

There is a line commonly attributed to Charles Kettering:

> A problem well stated is a problem half solved.[^kettering]

Defining the problem is productive work. Finding that a customer is waiting for an approval, rather than struggling to use the software, can change both the solution and who needs to be involved.

But the clearer definition only matters if the team can act on it.

**If a team cannot reject the proposed solution while remaining accountable for the problem, it has been assigned a solution.**

Putting “improve onboarding” above “build dashboard” does not change that.

## Leadership still has to choose

There are more real problems than a company can afford to solve. Reframing a feature roadmap as outcomes does not establish that it contains the most important problems.[^selection]

My responsibility is to identify the smallest set whose solution would materially improve the company's position, then concentrate resources on them. Why this problem? Why now? What are we choosing not to do?

“Grow revenue” and “improve efficiency” name desirable results without explaining the obstacle or a credible way through it. Richard Rumelt's distinction is useful here: strategy connects a diagnosis to a guiding policy and coordinated actions. A target alone does not do that work.[^strategy]

Teams should surface problems leadership has missed and challenge a diagnosis when the evidence contradicts it. I want the observation early, not only once someone has a solution. Leadership still has to make the choices and resolve competing claims on resources.

## Put the problem where it can be solved

A proposed solution can quietly determine which department receives the work.

“Build a dashboard” goes to a software team. “Hire more implementation engineers” becomes a staffing request. “Train the customer better” goes to customer success. Each narrows the diagnosis before anyone has established where the problem lives.

In the onboarding example, the relevant system runs from what Sales promises to what the customer can successfully do. The owner needs to follow that whole path, not just the part inside one department.

The operating model I want separates two responsibilities: **functions develop capabilities and maintain standards; a named problem owner stays accountable for the complete outcome.**

That owner needs capacity commitments from contributing functions, authority within agreed constraints, and a named leader to resolve conflicts beyond that authority.

“Own onboarding” is an empty assignment if the owner can change a page but cannot get a decision about the approval process causing the delay. Leadership has to commit the necessary capacity, provide that decision path, or place ownership where the conflict can be resolved.

Individual teams can own bounded contributions. Someone must still own the complete outcome. Every department finishing its task does not help a customer who remains stuck.

The people manager and problem owner can be different people. Their commitments must not create two competing priority queues. Capacity, decision rights, and escalation need to be agreed—not negotiated by individual contributors every morning.

## Discover the solution together

Problem ownership is not unilateral solution ownership.

In a product team, Product is responsible for value and business viability, Design for usability, and Engineering for feasibility. Those responsibilities support joint discovery; they are not a sequence in which Product decides, Design decorates, and Engineering implements.[^risks]

Engineers should help determine what is worth building. Designers should question whether the workflow makes sense. Product needs to understand what can be sold, supported, funded, and operated—not just what a customer requested. Functions outside the team contribute business constraints and access to customers and data, not merely a list of features to build.[^stakeholders]

A named owner makes accountability clear. It does not make one person's judgment sufficient.

## Make the assignment useful

A problem brief should make the next decision easier. For the hypothetical onboarding problem, it might look like this:

**Problem.** New customers stall between signing a contract and their first successful transaction. We need to establish where they wait and why.

**Why now.** Customers cannot use what they bought. Establish the frequency and cost of the delay before committing to the requested dashboard.

**Evidence and uncertainty.** We have stalled onboarding cases to investigate. We do not yet know whether missing information, approvals, or integration failures explain the delay.

**Outcome and guardrails.** Reduce time to a successful first transaction without increasing errors or shifting manual work onto customers. Establish a baseline before setting a target.

**Ownership and authority.** Name an onboarding owner and agree on capacity from the teams needed to investigate. Let the owner choose the approach within those commitments; name the leader who resolves policy or priority conflicts.

**Next decision.** Trace recent onboarding attempts and review the findings in one week. Decide what to test, who must act, or whether the problem warrants further investment.

Suppose that investigation shows most of the delay sits in an approval queue with no clear owner. The onboarding owner brings the evidence to the policy owner and agrees on a named approver and an escalation deadline for a limited trial. If the functions cannot agree on capacity, the designated leader resolves the tradeoff.

Engineering does not build the dashboard merely because it was the original request. The owner now has a different answer to test against the same outcome.

## Change the review, not just the brief

If every review asks only whether the feature shipped, the practical definition of success is still delivery.

Deployment does not end the responsibility. The team still needs to establish whether the intended benefit occurred and respond when it did not.[^results] That is the same discipline I described in [Close the Loop](/writing/close-the-loop/): test the result against reality, not just the completion of the work.

For the onboarding trial, assigning an approver is an action; shorter customer waits are the intended result. Compare those waits with the baseline, check errors and support effort, and investigate cases still getting stuck. Then continue, change, or stop the approach.

Outcome measures can move for unrelated reasons. The owner is responsible for distinguishing evidence of improvement from coincidence, escalating blockers, and changing an approach that is not working. Sound process supports that responsibility; it does not replace the result. Neither does a better metric excuse an unsafe or unmaintainable implementation.

Stopping is also a decision. The problem may be smaller than expected, the economics may not work, or another problem may deserve the resources. The owner should be able to make that case without defending the continued existence of a project.

## Keep the answer open

Leaders can propose solutions. Constraints can be fixed. Routine maintenance does not require elaborate discovery.[^stakeholders] The requirement is to distinguish what is genuinely constrained from what is merely someone's preferred answer.

“I think a dashboard would help because teams cannot see where customers are waiting” is useful: the explanation makes the idea testable. If the dashboard is mandatory, say so. Do not ask a team to discover a solution while privately expecting it to rediscover yours.

The discipline matters most when substantial effort is at stake. Choose the problem deliberately, put it where it can be solved, and keep the answer open to evidence.

**If you ask someone to own a problem, leadership must make it possible for them to change the answer—and resolve the dependencies that stand between them and the result.**

[^teams]: Marty Cagan, [Product vs Feature Teams](https://www.svpg.com/product-vs-feature-teams/), August 29, 2019. The distinction concerns outcome accountability and authority to discover solutions, not merely team composition.
[^kettering]: Robert W. Lucky, [When the Problem Is the Problem](https://spectrum.ieee.org/when-the-problem-is-the-problem), IEEE Spectrum. Attributes the quotation to Charles Franklin Kettering; this is a secondary attribution, not a verified original Kettering source.
[^selection]: Jon Moore and Marty Cagan, [Changing How You Decide Which Problems To Solve](https://www.svpg.com/changing-how-you-decide-which-problems-to-solve/), September 23, 2022.
[^strategy]: Richard Rumelt, [The perils of bad strategy](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/the-perils-of-bad-strategy), June 1, 2011.
[^risks]: Marty Cagan, [The Four Big Risks](https://www.svpg.com/four-big-risks/), December 4, 2017; and [Value and Viability](https://www.svpg.com/value-and-viability/), February 7, 2022.
[^stakeholders]: Chris Jones and Marty Cagan, [Stakeholders and the Product Model](https://www.svpg.com/stakeholders-and-the-product-model/), December 1, 2025. Covers problem framing, sharing potential solutions, business constraints, access to customers and data, and proportionate treatment of operational work.
[^results]: Marty Cagan, [Product Model Concepts](https://www.svpg.com/product-model-concepts/), January 17, 2024, especially Product Delivery.
