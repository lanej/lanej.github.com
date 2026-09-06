+++
title = "Lead With Problems"
description = "A problem statement is not enough. Ownership, authority, and accountability have to follow it."
date = "2026-09-06T23:29:00Z"
draft = false
toc = false
+++

If I ask a team to build a dashboard, I have already made several decisions.

I have decided that the problem is missing information. That a dashboard is the right way to provide it. That someone will use the information to make a better decision. And that building software is worth more than the other things the team could do.

Perhaps all of that is true. But if I only communicate the solution, those assumptions arrive as instructions.

The team can execute perfectly without testing any of them.

This is why I want to lead with problems. Not because leaders should stop having ideas, or because every request needs a discovery workshop. Because I want the organization to distinguish what we know needs to change from what we currently think might change it.

Marty Cagan makes this distinction in his writing about empowered product teams: their responsibility is to find a solution that produces a useful outcome, not merely implement a feature someone else selected.[^teams]

The part I care about is what that requires of leadership. A better problem statement accomplishes little if the funding, decision rights, and definition of success still belong to a predetermined solution.

**The problem has to become the unit of ownership, not just the opening paragraph of a project brief.**

## A missing solution is not a problem

“We don't have a dashboard” describes an absence. It does not establish that the absence matters.

Consider a hypothetical business where new customers stall between signing a contract and completing their first successful transaction. Someone asks for an onboarding dashboard.

That might help. But the delay could come from unclear requirements, slow access approvals, an unreliable integration, or a handoff nobody owns. A dashboard could make the delay more visible without making it shorter.

I would rather start with the customers who are getting stuck, where they wait, what the delay costs them and us, and what we have actually observed. The explanation can remain uncertain. We need to separate the evidence from the diagnosis, not pretend the diagnosis is complete.

The dashboard is then a hypothesis. So are changing an approval policy, improving documentation, fixing the integration, and eliminating a handoff.

There is a line commonly attributed to Charles Kettering:

> A problem well stated is a problem half solved.[^kettering]

Defining the problem is productive work. Finding that a customer is waiting for an approval, rather than struggling to use the software, can change both the solution and who needs to be involved. A policy change may do more than a dashboard.

But the clearer definition only matters if the team can act on it.

**If a team cannot reject the proposed solution while remaining accountable for the problem, it has been assigned a solution.**

Putting “improve onboarding” above “build dashboard” does not change that.

## Leadership still has to choose

Giving teams problems does not remove the need for strategy. There are more real problems than a company can afford to solve.

Cagan and Jon Moore make this explicit: converting a feature roadmap into an outcome-based roadmap can improve how teams work, but it does not establish that the resulting problems are the most important ones. Selecting those problems is a separate leadership responsibility.[^selection]

My version of that responsibility is to identify the smallest set of problems whose solution would materially improve the company's position, then concentrate resources on them.

That requires an argument. Why this problem? Why now? Why are we positioned to solve it? What are we choosing not to do?

“Grow revenue” is not that argument. Neither is “improve efficiency.” They name desirable results without explaining the obstacle or a credible way through it. Richard Rumelt's distinction is useful here: strategy connects a diagnosis to a guiding policy and coordinated actions. A target alone does not do that work.[^strategy]

This is not a one-way handoff in which executives define reality and teams accept it. Teams should surface problems leadership has missed and challenge a diagnosis when the evidence contradicts it. Leadership remains accountable for making the portfolio choices and resolving competing claims on resources.

Nor would I require someone to arrive with a complete solution before raising a problem. The person who notices a failure may not have the authority, context, or expertise to fix it. I want the observation early. We can decide who needs to investigate it.

## Put the problem where it can be solved

A proposed solution can quietly determine which department receives the work.

“Build a dashboard” goes to a software team. “Hire more implementation engineers” becomes a staffing request. “Train the customer better” goes to customer success.

Each request may be reasonable. Each also narrows the diagnosis before anyone has established where the problem lives.

In the onboarding example, the relevant system runs from what Sales promises to what the customer can successfully do. The cause may cross commercial, operational, and technical boundaries. Assigning an interface improvement to Product does not automatically give anyone responsibility for that whole path.

The arrangement I want is straightforward: functions develop capabilities and maintain professional standards; important problems determine how those capabilities are applied.

That does not mean dissolving departments or assembling a new temporary team for every request. Durable teams, service ownership, and people management still matter. But the boundary of an important problem should not be determined solely by the existing reporting lines.

I want one accountable owner for the outcome, explicit commitments from the contributing functions, and a clear path for resolving decisions the owner cannot make alone.

“Own onboarding” is an empty assignment if the owner can change a page but cannot get a decision about the approval process causing the delay. Either give the owner the necessary authority and support, or narrow the outcome to something they can meaningfully influence.

One people manager and one problem owner can be different people. That distinction must not create two competing priority queues. Capacity, decision rights, and escalation need to be agreed—not negotiated by individual contributors every morning.

## Own the problem, discover the solution together

This is also how I think about Product.

The job is not to administer a queue of solutions. It is to understand a valuable problem, establish the evidence behind it, and stay accountable for whether the response creates value.

But problem ownership is not unilateral solution ownership.

Cagan's division of responsibilities is helpful: Product is responsible for value and business viability, Design for usability, and Engineering for feasibility. Those responsibilities support joint discovery; they are not a sequence in which Product decides, Design decorates, and Engineering implements.[^risks]

Engineers should help determine what is worth building. Designers should help question whether the proposed workflow makes sense. Product needs to understand what can be sold, supported, funded, and operated—not just what a customer requested.

The same applies to the functions outside the product team. Chris Jones and Cagan describe stakeholders as contributors of business context, constraints, and access to customers and data. They can propose solutions without making those proposals binding instructions.[^stakeholders]

A named owner makes accountability clear. It does not make one person's judgment sufficient, give Product exclusive authority over company priorities, or exempt the work from engineering and operational standards.

## Make the assignment useful

For a consequential problem, I want enough shared context to make the next decision. Not a long document completed for its own sake.

The assignment should answer a few questions:

| Question | What it establishes |
| --- | --- |
| Who is affected, and what can they not do? | The problem, rather than the requested feature. |
| What have we observed, and what remains uncertain? | The evidence and the assumptions. |
| Why is this worth addressing now? | Its importance relative to other work. |
| What should change, and what must not get worse? | The intended outcome and its guardrails. |
| Who owns it, and what can they decide? | Accountability, authority, and dependencies. |
| What will we learn next, and when will we review it? | The next action and a decision point. |

For onboarding, success might mean less time to a successful first transaction without increasing failure rates or moving hidden manual work onto the customer. We would need a baseline before selecting a credible target.

The first step might simply be tracing a small set of recent onboarding attempts. If most of the elapsed time is waiting for an approval, that evidence should change the plan before we commit to building a dashboard.

The question is not whether we have eliminated uncertainty. It is whether the next action is proportionate to what we know and likely to help us decide.

## Change the review, not just the brief

If the assignment is a problem but every review asks only whether the feature shipped, the practical definition of success is still delivery.

I want reviews to return to the original claim: what changed for the people affected? What evidence connects that change to our work? Which assumption was wrong? What should we continue, change, or stop?

Delivery dates, quality, reliability, and cost remain important. An outcome does not excuse an implementation that is unsafe to operate or impossible to maintain. But shipping is one part of the result, not the substitute for it.

This is consistent with Cagan's description of product delivery: the team must observe whether the product produces the intended benefits and respond when it does not. Deployment does not end the responsibility.[^results]

I would not interpret outcome accountability as a promise to control everything. Markets change. Other teams make decisions. Measures can improve for unrelated reasons. An owner should be accountable for sound decisions, honest evidence, timely escalation, and adapting the approach—not manufacturing certainty about a noisy metric.

Nor does ownership mean pursuing the same problem forever. Evidence may show that it is smaller than expected, that the economics do not work, or that another problem deserves the resources. Stopping can be the correct decision.

The owner should be able to make that case without having to defend the continued existence of a project.

## Leading with problems does not forbid solutions

I still want leaders to bring ideas, technical judgment, and concrete proposals.

“I think a dashboard would help because teams cannot see where customers are waiting” is useful. The explanation makes the idea testable. The team can investigate whether visibility is actually the limiting factor.

If a decision is already fixed, say so. Name the constraint and what remains open. Do not ask a team to discover a solution while privately expecting it to rediscover yours.

And do not turn this into a requirement that every bug fix, routine maintenance task, or established obligation needs a strategy brief. The amount of discovery should follow the uncertainty and consequences of the decision. Cagan and Jones explicitly distinguish ordinary operational work from larger problems that require discovery.[^stakeholders]

The discipline matters most when we are deciding where substantial effort goes: which customer problem to pursue, which system to replace, which capability to build, or which part of the organization needs to change.

In those decisions, I want the problem to survive longer than our first answer.

Choose it deliberately. Put it where it can be solved. Give someone ownership of the result and enough authority to act. Keep the solution open to evidence.

**That is what I mean by leading with problems.**

[^teams]: Marty Cagan, [Product vs Feature Teams](https://www.svpg.com/product-vs-feature-teams/), August 29, 2019. The distinction concerns outcome accountability and authority to discover solutions, not merely team composition.
[^kettering]: Robert W. Lucky, [When the Problem Is the Problem](https://spectrum.ieee.org/when-the-problem-is-the-problem), IEEE Spectrum. Attributes the quotation to Charles Franklin Kettering; this is a secondary attribution, not a verified original Kettering source.
[^selection]: Jon Moore and Marty Cagan, [Changing How You Decide Which Problems To Solve](https://www.svpg.com/changing-how-you-decide-which-problems-to-solve/), September 23, 2022.
[^strategy]: Richard Rumelt, [The perils of bad strategy](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/the-perils-of-bad-strategy), June 1, 2011.
[^risks]: Marty Cagan, [The Four Big Risks](https://www.svpg.com/four-big-risks/), December 4, 2017; and [Value and Viability](https://www.svpg.com/value-and-viability/), February 7, 2022.
[^stakeholders]: Chris Jones and Marty Cagan, [Stakeholders and the Product Model](https://www.svpg.com/stakeholders-and-the-product-model/), December 1, 2025. Covers problem framing, sharing potential solutions, business constraints, access to customers and data, and proportionate treatment of operational work.
[^results]: Marty Cagan, [Product Model Concepts](https://www.svpg.com/product-model-concepts/), January 17, 2024, especially Product Delivery.
