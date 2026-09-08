+++
title = "Minimum Effective Dose"
description = "Do enough to learn what matters. Build one complete path, resist speculative scope, and let evidence determine the next investment."
date = "2026-09-06T18:42:54-07:00"
lastmod = "2026-09-07T14:46:00-07:00"
draft = false
+++

Suppose a customer asks for a report every Monday morning.

Before anyone sends it, the work expands. We need configurable schedules. Different file formats. Saved views. A place to manage all of it. Each addition is reasonable if we are building a reporting product.

But we do not yet know whether the report helps the customer make a better decision.

That is the question I want answered first. Not whether we can build a reporting system. Whether this particular information, delivered to this person at this time, changes something worth changing.

I want the smallest intervention that gives us a credible answer, then I want the answer to determine the next investment.

> That is what I mean by minimum effective dose: enough intervention to resolve the uncertainty that matters, without accumulating obligations around an answer we do not yet have.

The thing to minimize is the cost of reaching the next informed decision, not the ambition of the eventual result.

## Information that changes a decision

A team can learn a great deal without getting any closer to deciding what to do.

Benchmarking databases might be useful. It does not answer whether anyone needs the report. Interviews might establish that people dislike their current process. They do not establish that our integration can obtain the required data before Monday morning.

I care about decision-relevant information: what we need to know to choose the next action.

Dan North's *Deliberate Discovery* frames engineering work around identifying the ignorance constraining progress and deliberately reducing it.[^north] Wes Kao uses *minimum effective dose* for a closely related business idea: do enough work to obtain the insight needed for the decision.[^kao]

Before starting, I want three things to be clear: what we do not know, which decision that prevents us from making, and what we would do differently depending on the result.

For the report, we might be deciding whether to invest in recurring delivery. The first useful evidence is whether the customer can use the information, in time, to make the decision they described.

An enthusiastic response is not the same as use. Use is not the same as a better outcome. One customer's result is not proof of a market. Each observation justifies a different next step.

If every possible result leads to “continue building the original plan,” we are not really running an experiment.

## A path through positive space

A project can become an inventory of everything that might eventually be required. Every customer, exception, dependency, failure mode, and future extension gets a place in the design before we have established a useful path through any of them.

I think of *positive space* as the part of the problem where we have evidence that useful action is possible: a concrete route from a need to an outcome under conditions we understand.

For the Monday report, that route might be one data source, one agreed calculation, one recipient, and one decision. It gives us somewhere to stand. We can then ask what prevents that path from being dependable, repeatable, or useful to someone else.

A failed attempt can locate the path too. If the customer receives correct information and does nothing differently, perhaps the report answers the wrong question, arrives too late, or reaches someone who cannot act.

Positive space is not positive results. It is evidence about where useful action is possible.

## Narrow does not mean incomplete

A steel thread is a useful implementation pattern here: build a narrow slice through the relevant parts of the real system rather than building each component extensively and connecting them later.[^thread]

For the report, the thread runs from source data to customer decision. A working query is only part of it. So is an email arriving on time. We need enough of the real path to find out whether the information can do the job.

{{< minimum-dose-thread >}}

This does not require every report format or a scheduling interface. It does require correct data, appropriate access, intelligible output, and delivery early enough to matter. We also need to observe what happens after delivery.

Choose the thread for the uncertainty it encounters, not because it is easy to demonstrate. If the external source is the risk, replacing it with a convenient stub avoids the question. If customer value is the risk, perfecting the integration before anyone sees the result may be the wrong order.

Sometimes the minimum intervention is not software. A manually prepared report can test whether the information is useful. It cannot establish that an automated service is reliable or inexpensive to operate. A technical thread can establish integration behavior without demonstrating willingness to pay.

The test has to reach the thing we claim to be testing.

## Follow the constraint

Once a path produces a useful result, what prevents it from doing so reliably or at the required scale?

Goldratt's Theory of Constraints gives a useful rule for choosing the next intervention: improve what limits the system's objective rather than whichever component is easiest to optimize.[^toc]

Suppose the report proves useful but repeatedly arrives after the customer's decision. Tracing the path suggests that corrections and a shared review queue cause the delay.

The next dose could be a bounded trial with clearer input requirements and checks that prevent avoidable rework before review. That uses the reviewer's existing capacity better and changes the work upstream. It does not justify a reporting platform or a faster query.

Then measure the path again. Did usable reports reach decisions sooner without worsening errors or delaying other necessary work? Moving this report to the front of the queue may simply transfer the delay.

A steel thread makes the path observable. Constraint thinking helps choose where to intervene. Minimum effective dose keeps that intervention proportionate to what the evidence can justify.

## Scope creep spends the answer before we have it

Adding custom schedules to the first report is not just another task. It postpones the value question and commits more effort to an assumption the report was supposed to test.

Martin Fowler's account of YAGNI includes the carrying cost of speculative capability: even before it is useful, its complexity makes later changes harder.[^yagni] Here there is another cost too: speculative scope delays the evidence that could redirect the work altogether.

I use a simple test for proposed additions:

> Does this help us answer the question in front of us, or is it something we expect to need after that question is answered?

Correctness checks may be necessary to interpret the result. Access controls may be necessary to run the trial responsibly. Instrumentation may be necessary to know whether anything changed. Those belong in the minimum when the experiment depends on them.

Multiple export formats, a configuration interface, and support for other departments need a different argument. “We will probably need them eventually” is not enough.

The boundary protects the question long enough to answer it. It should not protect the original solution from what we discover.

## Keep the machinery movable

Kent Beck's “make it run, make it right, make it fast” is useful to me as an ordering rule, especially when paired with small slices and short feedback cycles.[^beck]

For the report, establish one useful path. Make it dependable enough for the commitment being tested. Then invest where the evidence says improvement matters.

I think of this as keeping the machinery movable while the requirements are still moving. In software, we can bolt an unsettled answer down with a public interface, a deep dependency chain, or a general-purpose framework. In a business, we can do it with a service promise, a specialized team, or a contract built around the current process.

The implementation may be small while the commitment is large.

That is why the dose includes the cost of changing our minds. A narrow boundary around an uncertain integration, tests around the behavior we need, and enough observability to understand failures can all make the next change cheaper. They may be part of the minimum rather than overhead to remove.

Reducing breadth does not reduce the standard. If the result arrives too late to be useful, performance is already a requirement. If the trial handles sensitive data or moves money, the relevant safeguards belong in the trial.

## The business needs a complete path too

The engineering path might end with a correct response. The business path usually does not.

If we are testing a paid service, we may also need to know whether the customer understands the offer, can adopt it, receives the promised benefit, and will pay enough to justify delivering it. Those are separate uncertainties.

For an initial trial, an existing sales process, a straightforward agreement, a standard invoice, and explicit manual work may be enough. There is no reason to build a new commercial system around the first customer.

But count the manual work. If every report needs an hour of intervention, the trial has demonstrated delivery with an hour of labor attached. Hiding that effort does not establish good economics.

Minimum effective dose becomes local cost-cutting when complexity is merely moved into Operations or onto the customer. A system has not become simpler because the obligation changed owners.

Manual delivery may still be the cheapest credible way to test usefulness. Once delivery is understood and recurring, automation may become the smaller continuing burden. The dose changes as the evidence changes.

## Make the next commitment earn its place

In [Lead With Problems](/writing/lead-with-problems/), I argued for a named owner accountable for the outcome, with functions supplying the capabilities needed to achieve it.

That owner also needs to sequence the learning. Otherwise each function can build its part of the imagined final system while nobody resolves the uncertainty that could invalidate the whole effort.

I want the owner to explain what currently limits the outcome, the evidence behind that diagnosis, and the next test. What commitments does it require? What would the result justify? What would cause us to stop?

{{< minimum-dose-decision >}}

After the test, return to the claim. What changed? What remains uncertain? What is the strongest conclusion the evidence supports? What did the intervention cost, including work done by other people?

That is where [closing the loop](/writing/close-the-loop/) matters. The result has to change the next action: stop, strengthen the path, or move attention to a different limitation.

This is not a license for endless experiments. Once the relevant uncertainty is sufficiently resolved, act. The rigor of the evidence should follow the consequences of the decision: one reversible trial may justify another, while a broad customer promise or difficult-to-reverse architecture needs stronger evidence.

## Concentration, not austerity

Minimum effective dose does not mean permanently doing less. It means refusing to make every possibility a prerequisite for progress.

Once the original outcome is achieved, additional investment may be worthwhile. Greater reliability, lower operating cost, or a broader offering can justify substantial work. But that work needs an argument of its own.

I want a steel thread through the problem, not a miniature version of every system we might eventually need. Enough of the real path to obtain credible evidence. Enough care to meet the standard of the commitment. Little enough speculative machinery that the answer can still change what we do.

**Start narrow. Finish the path. Expand for a reason.**

[^north]: **[Introducing Deliberate Discovery](https://dannorth.net/blog/introducing-deliberate-discovery/)**  
    Dan North · 2010

    Identifies and reduces the specific ignorance constraining delivery. The decision-oriented scope test here is my application of that principle.

[^kao]: **[Use the minimum effective dose](https://www.weskao.com/blog/use-the-minimum-effective-dose)**  
    Wes Kao · 2020

    Applies the phrase directly to doing enough work to obtain the insight needed for a business decision.

[^thread]: **[Steel threads are a technique that will make you a better engineer](https://www.rubick.com/steel-threads/)**  
    Jade Rubick · 2023

    Describes thin, integrated slices through important use cases.

[^toc]: **[Introduction to Theory of Constraints](https://www.goldrattresearchlabs.com/introduction-to-toc)**  
    Goldratt Research Labs

    Explains Goldratt's system-level focus and five focusing steps.

[^yagni]: **[Yagni](https://martinfowler.com/bliki/Yagni.html)**  
    Martin Fowler · 2015

    Explains the build, delay, carrying, and repair costs of speculative capability.

[^beck]: **[Mastering Programming](https://newsletter.kentbeck.com/p/mastering-programming)**  
    Kent Beck · 2024

    Includes “make it run, make it right, make it fast” alongside slicing and feedback-oriented programming practices.