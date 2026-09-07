+++
title = "Minimum Effective Dose"
description = "Do enough to learn what matters. Build one complete path, resist speculative scope, and let evidence determine the next investment."
date = "2026-09-06T18:42:54-07:00"
draft = false
toc = true
diagrams = true
+++

Suppose a customer asks for a report every Monday morning.

Before anyone sends it, the work expands. We need configurable schedules. Different file formats. Saved views. A place to manage all of it. Each addition is reasonable if we are building a reporting product.

But we do not yet know whether the report helps the customer make a better decision.

That is the question I want answered first. Not whether we can build a reporting system. Whether this particular information, delivered to this person at this time, changes something worth changing.

I want the smallest intervention that gives us a credible answer. Then I want to make the next decision with that answer, rather than keep building the original plan.

**That is what I mean by minimum effective dose: enough intervention to resolve the uncertainty that matters, without accumulating obligations around an answer we do not yet have.**

The thing to minimize is the cost of reaching the next informed decision. Not the ambition of the eventual result.

## Information that changes a decision

A team can learn a great deal without getting any closer to deciding what to do.

Benchmarking databases might be useful. It does not answer whether anyone needs the report. Interviews might establish that people dislike their current process. They do not establish that our integration can obtain the required data before Monday morning.

I care about decision-relevant information: what we need to know to choose the next action. Not an abstract score for how much we learned.

Dan North's *Deliberate Discovery* makes this distinction useful for engineering. Identify the ignorance constraining progress, then deliberately reduce it enough to proceed.[^north] Eric Ries's original account of the minimum viable product similarly centers validated learning, not merely shipping a smaller product.[^ries] Wes Kao applies minimum effective dose directly to doing enough work to obtain the insight needed for a business decision.[^kao]

The questions I want answered before we start are simple:

**What do we not know? Which decision does that prevent us from making? What would we do differently depending on the result?**

For the report, we might be deciding whether to invest in recurring delivery. The first useful evidence is whether the customer can use the information, in time, to make the decision they described. If they cannot, we need to understand why before expanding the offering.

An enthusiastic response is not the same as use. Use is not the same as a better outcome. And one customer's result is not proof of a market. Each observation supports a different next step.

If every possible result leads to “continue building the original plan,” I would question whether we are running an experiment at all.

## A path through positive space

A project can become an inventory of everything that might be required. Every possible customer, exception, dependency, failure mode, and future extension gets a place in the design.

Some of those constraints are real. We still need a way through them.

I think of *positive space* as the part of the problem where we have evidence that useful action is possible. A concrete route from a need to an outcome, under conditions we understand. Not optimism, and not a complete map of the eventual system.

For the Monday report, that route might be one data source, one agreed calculation, one recipient, and one decision. It gives us somewhere to stand. We can then ask what prevents that path from being dependable, repeatable, or useful to someone else.

A failed attempt also helps locate the path. If the customer receives correct information and does nothing differently, that is a reason to revisit the value claim. Perhaps the report answers the wrong question. Perhaps it arrives too late. Perhaps the person receiving it cannot act.

“Positive” describes the useful path we are trying to find. It does not mean accepting only positive results.

**The objective is to find a workable route, not to defend our first route.**

## Narrow does not mean incomplete

The steel thread is a practical way to do this in software. Build a thin slice through the relevant parts of the real system, rather than building each component extensively and connecting them at the end. Jade Rubick describes the technique as a narrow use case that crosses system boundaries and provides a working foundation for later changes.[^thread]

In our example, the thread runs from the source data to the customer's decision. A working query is only part of it. So is an email arriving on time. We need enough of the path to find out whether the information can do the job.

{{< minimum-dose-thread >}}

This does not require every report format or a scheduling interface. It does require the correct data, appropriate access, intelligible output, and delivery early enough to matter. We also need to observe what happens after delivery. An open notification tells us less than seeing whether the report changed the intended decision.

Choose the thread for the uncertainty it encounters, not merely because it is easy to demonstrate. If the external data source is the risk, replacing it with a convenient stub avoids the question. If customer value is the risk, perfecting the integration before anyone sees the result may be the wrong order.

Sometimes the minimum intervention is not software. A manually prepared report can test whether the information is useful. It cannot establish that the automated service is reliable or inexpensive to operate. A technical thread can establish integration behavior without demonstrating willingness to pay.

The test has to reach the thing we claim to be testing. “It worked” is incomplete unless we can say what worked, for whom, and under which conditions.

## Scope creep spends the answer before we have it

This is why I resist scope creep so strongly.

Adding custom schedules to the first report is not just another task. It postpones the value question and commits more effort to an assumption the report was supposed to test. If the trial disappoints, the expanded interface may also leave us with more competing explanations for the result.

Martin Fowler's account of YAGNI includes the cost of carrying speculative capability: even before it is useful, its complexity makes other changes harder.[^yagni] That cost applies here, but so does the delay in obtaining evidence that could redirect the work altogether.

I would put each proposed addition through this question:

> Does this help us answer the question in front of us, or is it something we expect to need after that question is answered?

Correctness checks may be necessary to interpret the result. Access controls may be necessary to run the trial responsibly. Instrumentation may be necessary to know whether anything changed. None of those is optional merely because we want a small scope.

Multiple export formats, a configuration interface, and support for other departments need a different argument. “We will probably need them eventually” is not enough.

Nor should the first answer automatically become the permanent plan. Suppose the recipient explains that they do not need a weekly report. They need to know when one condition changes. Replacing the report with a targeted notification is a response to evidence, even if it changes the scope.

**Changing scope because we learned something is adaptation. Expanding scope before learning anything is speculation.**

A useful boundary protects the question long enough to answer it. It should not protect the original solution from what we discover.

## Make it work before making it hard to change

Kent Beck writes:

> Make it run, make it right, make it fast.[^beck]

He places that sequence alongside slicing work, short feedback cycles, and making difficult changes easier before attempting them. I read it as a discipline for ordering investment, not three giant project phases.

For the report, establish one useful path. Then make its behavior and implementation appropriate for the recurring commitment. Optimize the measured constraint when there is a reason to do so. We might need a faster query. We might instead need a simpler approval process.

Musk describes a related order in his Starbase interview with Everyday Astronaut: question requirements, remove unnecessary parts or steps, simplify what remains, accelerate it, and automate last.[^sequence] The useful connection is that optimization comes after deciding whether the work should exist.

I think of it as keeping the machinery movable while we discover the sequence. In software, we can bolt things down with public interfaces, a deep dependency chain, or a general-purpose framework built around an unsettled requirement. In a business, we can do it with a service promise, a specialized team, or a contract that assumes the current process will continue.

The implementation may be small while the commitment is large.

That is why the dose includes the cost of changing our minds. A narrow boundary around an uncertain integration, tests around the behavior we need, and enough observability to understand failures can make the next change cheaper. They may be part of the minimum, rather than overhead to remove.

And “make it run” still has a standard. If the result arrives too late to be useful, performance is already a requirement. If the trial handles sensitive data or moves money, the relevant safeguards belong in the trial. Reducing breadth does not remove those obligations.

**Sequence the investment, not the obligation to meet the standard.**

## The business needs a complete path too

The engineering path might end with a correct response. The business path does not necessarily end there.

If we are testing a paid service, we may also need to know whether the customer understands the offer, can adopt it, receives the promised benefit, and will pay enough to justify delivering it. Those are separate uncertainties. A single successful demonstration does not settle all of them.

For an initial trial, an existing sales process, a straightforward agreement, a standard invoice, and explicit manual work may be sufficient. There is no requirement to build a new commercial organization around the first customer.

But count the manual work. If every report needs an hour of intervention, the trial has demonstrated delivery with an hour of labor attached. Hiding that effort does not establish good economics.

This is where minimum effective dose can be misused as local cost-cutting. We eliminate an engineering task, but move it into Operations. We remove a process, but make the customer coordinate the handoffs. One budget improves while the same obligation survives elsewhere.

**A system has not become simpler just because its complexity moved into a person.**

The sensible dose changes as the evidence changes. Manual delivery may be the cheapest credible way to test usefulness. Once delivery is understood and recurring, automation may be the smaller continuing burden. A reusable capability can be worth more initial work when it removes repeated effort we now know exists.

The same reasoning applies to an internal operating process. Suppose decisions stall because nobody knows who can make them. Start by making ownership and escalation explicit for the affected decisions. Check whether that reduces the delay. Do not assume the first response must be a new committee, reporting system, and weekly review.

If the remaining delay comes from conflicting priorities, a clearer role description has exposed another problem; it has not solved that one. The next intervention should address what we learned.

## Make the next commitment earn its place

In [Lead With Problems](/writing/lead-with-problems/), I argued for a named owner accountable for the outcome, with functions supplying the capabilities needed to achieve it.

That owner also needs to sequence the learning. Otherwise each function can build out its part of the imagined final system while nobody resolves the uncertainty that could invalidate the whole effort.

I want an owner to be able to explain the next test, the resources it needs, and the commitment it could justify. Dependencies, authority, and the conditions for stopping should be explicit. This should be a short working agreement, not a new reporting bureaucracy.

{{< minimum-dose-decision >}}

After the test, return to the claim. What changed? What remains uncertain? What is the strongest conclusion the evidence supports? What did the intervention cost, including the work done by other people?

That is where [closing the loop](/writing/close-the-loop/) matters. The result has to change the next action. Learning that a report is not useful may justify stopping. Learning that it is useful but routinely arrives late may justify a delivery fix, not a reporting platform.

This is also not a license for endless experiments. Once the relevant uncertainty is sufficiently resolved, act. A team should not keep asking for another prototype when the evidence already supports a commitment. Nor does a well-understood maintenance task need to masquerade as discovery.

The rigor of the evidence should follow the consequences of the decision. One reversible trial may justify another. It is a weaker basis for a broad customer promise or a difficult-to-reverse architecture. Some questions require more cases, more time, or a more controlled comparison to answer credibly. Minimum does not mean choosing a sample too small to tell us anything.

## Concentration, not austerity

Minimum effective dose does not mean permanently doing less. It means refusing to make every possibility a prerequisite for progress.

Once the original outcome is achieved, additional investment may still be worthwhile. Greater reliability, lower operating cost, or a broader offering can justify substantial work. But that work needs an argument of its own. An already-solved problem should not fund indefinite expansion by default.

I want a steel thread through the problem, not a miniature version of every system we might eventually need. Enough of the real path to obtain credible evidence. Enough care to meet the standard of the commitment. Little enough speculative machinery that the answer can still change what we do.

Establish the path. Learn what makes it work. Make the next investment with that knowledge.

**Start narrow. Finish the path. Expand for a reason.**

[^north]: **[Introducing Deliberate Discovery](https://dannorth.net/blog/introducing-deliberate-discovery/)**  
    Dan North · 2010

    Argues for identifying and reducing the specific ignorance that constrains delivery. The decision-oriented scope test in this article is my application of that principle, not a quantitative information-gain formula.

[^ries]: **[What Is an MVP?](https://leanstartup.co/resources/articles/what-is-an-mvp/)**  
    Eric Ries · Lean Startup Co.

    Defines the minimum viable product around validated learning about customers with the least effort, rather than simply making a small product. This is a republication of Ries's essay from Startup Lessons Learned.

[^kao]: **[Use the minimum effective dose](https://www.weskao.com/blog/use-the-minimum-effective-dose)**  
    Wes Kao · 2020

    Applies the phrase directly to obtaining enough insight to decide whether to continue. The extension here includes end-to-end engineering, business obligations, and the cost of reversing a commitment.

[^thread]: **[Steel threads are a technique that will make you a better engineer](https://www.rubick.com/steel-threads/)**  
    Jade Rubick · 2023

    Describes thin, integrated slices through important use cases. The report example and extension to a business's customer-to-outcome path are illustrative applications, not a case study from Rubick's article.

[^yagni]: **[Yagni](https://martinfowler.com/bliki/Yagni.html)**  
    Martin Fowler · 2015

    Explains the build, delay, carrying, and repair costs of speculative capability. The argument is not against tests, refactoring, or other work needed to keep the current system healthy and changeable.

[^beck]: **[Mastering Programming](https://newsletter.kentbeck.com/p/mastering-programming)**  
    Kent Beck · 2024

    Contains the quoted sequence and places it alongside slicing, feedback cycles, baseline measurement, and concrete hypotheses. The business application here is my extension.

[^sequence]: **[Starbase Tour and Interview with Elon Musk](https://everydayastronaut.com/starbase-tour-and-interview-with-elon-musk/)**  
    Everyday Astronaut · 2021

    The interview publisher's account records the five-step sequence of questioning, deletion, simplification, acceleration, and automation. The movable-machinery passage is a metaphor, not a claim about a specific Tesla factory anecdote.
