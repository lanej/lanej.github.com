+++
title = "Engineering Is Calibration"
description = "How working with complex systems teaches us what needs to change and how to make progress"
date = "2026-09-26T21:10:00-07:00"
draft = true
+++

<!--
Working document: revised prose draft, not publication-ready.

Series: Architecture Under Uncertainty (5/5)

Shared thesis:
Engineering is the discipline of making progress on problems we don't yet fully understand.

Series principle:
An inherited solution is evidence of a past decision, not proof of a present constraint. Goals, observed facts, and chosen means must remain distinguishable.

Complete thought:
Engineering maturity means taking responsibility not just for a proposed solution, but for discovering what actually needs to change and developing a way to make progress. Problem selection and problem solving are one continuous engagement with an evolving system. Calibration joins that judgment to a realistic model of systemic exposure: what a change can affect, how failure will present, and which next commitment is useful and affordable.

Role in the progression:
Synthesize the earlier essays' dependency, timing, and migration arguments into the judgment required to change complex systems. Return to the locally reasonable decisions that created the original Rails problem. Career progression illustrates the argument; it does not organize it.

Relationship to the companion essay:
Cheap Construction Is Not Progress applies this discipline to lower-cost software construction. Keep AI out of this capstone's central argument.

Editorial boundaries:
- Ground the personal lens in lab work for the electrical/computer engineering degree, professional QA involving hardware and software together, and mature business applications. Keep degree coursework distinct from employment. Do not frame this as CS versus engineering.
- The lab anecdote is Josh's recollection. Preserve uncertainty about the project (possibly a counter); do not invent the wiggle-test procedure, measurements, chip type, or physical failure mode.
- Use relationships to explain sustained engagement, evolving context, and reassessment, not an obligation to preserve every implementation.
- Treat shared frustration with legacy systems and attachment to architectural purity as symmetrical ways means can displace ends; do not impute motives to specific people.
- Respect the legacy architecture as a historically useful adaptation without assuming it remains the right tool. The horse that got us here may need care or replacement; appreciation is not permanent obligation.
- Brontes and Engine Yard anecdotes are grounded in the Career Canon; avoid claiming precise technical mechanisms or outcomes beyond the recorded account.
- Separate disagreement about outcomes, beliefs about reality, and proposed means. Refer to the published Lead With Problems essay without reproducing it.
- Preserve the distinction between genuine constraints and assumptions inherited from a previous solution; show how bounded mess can be a rational price of progress.
- Do not imply that difficulty or neglect establishes value, or make other engineers' supposed lack of perseverance the contrast.
- The transaction/retry example is hypothetical, not a claim about an employer or a particular incident.
- Review overlap with article 4: migration mechanisms belong there; this piece explains how to choose and evaluate an intervention.

Publication gate:
Keep draft = true. Complete and refine all five drafts, conduct the corpus-level review, then finish and publish sequentially. Remove this working block before publication.
-->

During lab work for my electrical and computer engineering degree, I spent a long time trying to make a circuit work. I no longer remember exactly what we were building, possibly a counter. It seemed as though it should work, but it didn't.

The wiggle test exposed an assumption I hadn't realized I was making: that the chip supplied by the course was functioning. It wasn't.

I had let where the component came from stand in for evidence about how it behaved. The chip was part of the system, but I had treated its condition as something already settled. I needed the circuit to behave as specified. The fact that the course supplied the chip did not establish that it worked, yet I had allowed that assumption to limit which explanations I would consider.

I learned a great deal in the time it took to find that defect. Looking back, the durable lesson was about what belonged in the investigation. When observation contradicts expectation, the assumptions behind that expectation need to be examined too. Some concern the thing I built. Others concern things I was given and had no reason to expect I would need to question. The defective chip was not an explanation I had eliminated with evidence. I had excluded it by assumption.

The boundaries of the assignment were not necessarily the boundaries of the problem.

## What counts as failure

My early quality-assurance work involved hardware and software together. That reinforced an essential prerequisite: I needed to establish what I expected the combined system to do before a failure could tell me much. Saying that a system was broken was not enough. What should it have done? Under which conditions? What observation would distinguish the expected behavior from the behavior we had?

The circuit failing had told me that something was wrong. It had not told me that the chip was defective. Getting from one observation to the other required questioning the explanation I had been using. The same distinction mattered in QA: reproducing a failure gave me something to investigate, and a useful test helped distinguish possible explanations.

That is what made mistakes useful. Repeating an unexplained failure could consume a great deal of time. Learning required a result that changed what I understood or what I would try next.

At Brontes, the validation cycle took roughly two days. Much of the delay came from reconstructing the state that tests depended on. I built orchestration that modeled those dependencies and automated the setup and recovery work, reducing the cycle to about twenty minutes. I had been hired into QA, but the higher-leverage problem was the cost of getting feedback. Shortening that loop made it possible to learn much faster.

I brought those habits into large business applications, including aging Rails codebases. At Engine Yard, I encountered an unstable monolith that few people wanted to work on. I did not start by proposing a replacement. I worked from its edges inward, using local repairs to understand more of its behavior and constraints. That eventually supported changes across reliability, persistence, and the surrounding platform.

The difficult parts of systems like these were rarely isolated algorithms. They were business rules interacting with other business rules, assumptions spread across components, and years of decisions whose reasons were no longer immediately visible. I needed to understand the system in front of me well enough to change it while it continued serving the business.

Existing behavior tells you what a system does; it does not, by itself, settle what the system should do. Some behavior is a requirement nobody wrote down. Some is a workaround. Some is a bug that another component has learned to accommodate. Before changing it, you need to understand which distinction matters to the people relying on it.

Consider a hypothetical checkout operation that updates an order in a database and asks a separate payment service to charge the customer. The payment succeeds, but the local operation fails before it records the result. A database rollback cannot undo a charge the payment service has already accepted.

The local code might look straightforward. Understanding the failure requires a larger view: which system owns the payment state, what the caller knows, what a retry will do, and how an uncertain result gets reconciled. Calling the operation a transaction does not tell us which effects are actually inside its boundary.

A useful test might arrange for the payment to succeed while its reply is lost, then check whether recovery produces one charge and a consistent order state. The expected behavior makes the failure interpretable. Without it, a green test could mean only that the method returned without raising an exception.

This is why I find transactional reasoning useful when assessing engineering judgment. It requires following state and effects across time, ownership, and failure boundaries rather than stopping at the edge of the function being edited.

I think of calibration as bringing my explanations and predictions closer to the system's actual behavior. The requirement might remain one charge per order; what changes is my understanding of what must be controlled to achieve it. That includes recognizing where my understanding is weak enough that I should narrow the change or gather more evidence first.

## Systems do not stay solved

A homework problem normally supplies a question and some boundary on what counts as completion. A company keeps changing both.

New customers arrive with different requirements. A process that used to be manual becomes automated. Two teams acquire separate responsibilities for behavior that once lived comfortably together. An assumption can stop being useful without ever having been unreasonable.

I try to appreciate the horse that brought us here. It might be dirty and thin, but it got us this far. The monolith that now slows the business may once have been exactly what allowed it to find customers and survive. That history deserves respect. It does not oblige us to keep riding the same horse indefinitely, and it does not make every decision along the way correct. It means judging the old system against the circumstances in which it was built as well as the outcomes we need now.

That is why I think of a mature codebase as an ongoing relationship. You develop context through sustained attention: what it does reliably, where it surprises you, what its users depend on, and which compromises have outlived their purpose. You can get frustrated with it without treating frustration as evidence that the whole thing should be discarded.

The relationship can also stagnate. Familiarity makes it easier to navigate a constraint without questioning it. A release requiring coordination across several teams can become routine. So can a manual reconciliation step that everyone knows how to perform. The organization gets better at living with the problem, which can make the problem less visible.

An aging codebase can become a convenient common enemy. Complaining about it gives a team something to agree on, but shared frustration does not establish a shared goal. "Get rid of the monolith" may sound decisive while saying very little about which business outcome will improve, or at what cost.

The opposite attachment is just as limiting. An architecture can become so associated with the people who created it that preserving its consistency starts to look like success in its own right. I do not need to speculate about anyone's motives to recognize the danger: both hostility to the old system and devotion to a purer replacement can turn the implementation into the objective.

Cultivating the system means revisiting those arrangements as the business changes. It includes leaving working parts alone when changing them would buy little. Sometimes it requires replacing or retiring an implementation. The commitment is to the business's ability to function and change, not to preserving a particular body of code.

There is no final architecture that releases us from that attention. There can be finished projects, removed dependencies, and retired systems. The surrounding business still presents new questions.

## Learning what needs to change

Return to the checkout example. Suppose the assignment is to make retries reliable. Following one failed operation might reveal that several entry points can initiate the same charge, each with a different understanding of what has already happened.

The stated problem concerns retry handling. The more consequential problem may be ownership: there is no single place responsible for deciding whether this payment operation should happen again. Adding another exception handler could make one path look healthier while leaving that ambiguity intact.

You do not need a complete map of the business to discover this. You need enough context to follow the operation beyond the point where the local explanation stops accounting for its behavior. The investigation may justify routing one class of operation through an explicit owner before trying to replace the rest of the payment flow. It may instead show that the existing owner is adequate and one caller is violating its contract. Those findings call for different work.

Sometimes understanding the larger system reveals that a small change will solve most of the practical problem. Sometimes a small investigation exposes a larger constraint. Neither direction can be prescribed in advance. The problem is what it is, not what would fit most comfortably into the solution I already know how to build.

I find it useful to separate three kinds of disagreement before arguing about architecture. Do we disagree about the outcome? Do we disagree about the facts of the system, including which constraints are real? Or do we agree on those things but differ about the means? The second kind invites investigation and a test. The third invites comparison of tradeoffs. Neither will resolve a disagreement about the goal that nobody has acknowledged.

This is an extension of what I argued in [Lead With Problems](/writing/lead-with-problems/). A team asked to replace a monolith has already been given a solution. Before committing to that solution, we should establish what must improve and which constraints actually bind us. An inherited implementation is evidence of a past decision, not proof of a permanent constraint.

This is where problem selection and problem solving become inseparable. Engaging with a problem changes my understanding of its importance, and attempting a bounded improvement tests whether I have identified the right cause. New evidence can justify expanding the work, narrowing it, or stopping.

A senior engineer can make progress on a poorly defined problem. At staff and principal levels, I expect responsibility to include discovering which problems deserve the organization's attention and bringing the relevant people together to address them. That is the same discipline applied before there is an agreed assignment. It requires enough engagement to understand both the consequence of the problem and the cost of doing something about it.

Some consequential problems are ones people have learned to live with. Neglect alone does not establish their importance. A difficult subsystem might be stable and rarely changed; an unremarkable ownership ambiguity might affect every release. Judgment means distinguishing those situations, including recognizing when a persistent inconvenience is cheaper than its proposed cure.

## Make a commitment you can learn from

An incomplete understanding does not excuse indefinite investigation. At some point, you need to decide what to do next and what you expect to learn from it.

In the checkout example, reproducing an ambiguous payment outcome with a controlled substitute for the payment service may be the right first step. It lets you test recovery without exposing a customer to a second charge. If the behavior cannot be observed reliably, improving that visibility may be more useful than beginning the replacement.

The size of the code change is secondary. What matters is the scope of its possible effects, whether you can detect a bad result, and what recovery would require. Reverting code does not necessarily reverse what it has already done. A useful risk budget has to account for that difference.

Progress often leaves some mess behind. A temporary adapter might be awkward and still be preferable to a clean replacement that delays the benefit for a year. Equally, a quick fix can create a dependency that costs more than it saves. The judgment is not whether the result looks pure; it is whether the compromise improves the outcome without consuming more future options than it buys.

Small interventions make learning affordable when they bound those consequences. They are not automatically informative. A change that cannot distinguish competing explanations may consume time without improving the next decision. Nor does learning require deliberately causing every possible failure. Existing incidents, operational knowledge, and careful reasoning can eliminate experiments we do not need to run.

Code review, controlled tests, shadow execution, and progressive delivery can each contribute different evidence. None removes the need to say what uncertainty it is meant to reduce. The migration techniques in the preceding essay put that discipline into practice; choosing among them depends on what we still need to understand.

An organization needs to make these commitments too. Someone must be accountable for the next increment, with a clear expectation of what it should change and when the result will be reviewed. Otherwise, uncertainty becomes a reason to keep reopening the decision rather than a condition the work is designed to manage.

Keep the destination revisable, but make a real commitment to the next useful step. The result may change the plan. That is different from never committing to a plan that could be tested.

## Back to the local decision

The first essay begins with reasonable local choices that compose into a system nobody intended. The response cannot simply be a better set of permanent rules. A boundary that is worth maintaining now may have been needless expense earlier. Two representations that look redundant may keep unrelated responsibilities from becoming coupled. A replacement that appears necessary may become smaller once its actual constraints are understood.

The chip was already defective while I was treating it as a given. My understanding had to change before I could address the problem in front of me. Calibration is how I bring that same attention to architectural decisions. Their assumptions remain open to investigation even after the decisions have become familiar. I do not need to defend an inherited implementation or replace it on principle. I need to know whether it still serves the outcome, and what evidence would change my mind.

Engineering is the discipline of making progress on problems we do not yet fully understand. Maturity means taking responsibility not just for a proposed solution, but for discovering what actually needs to change and developing a way to make progress.
