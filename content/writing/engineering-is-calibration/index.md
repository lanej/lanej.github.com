+++
title = "Engineering Is Calibration"
description = "How working with complex systems teaches us what needs to change and how to make progress"
date = "2026-09-26T21:10:00-07:00"
draft = true
+++

<!--
Working document: first prose draft, not publication-ready.

Series: Architecture Under Uncertainty (5/5)

Shared thesis:
Engineering is the discipline of making progress on problems we don't yet fully understand.

Complete thought:
Engineering maturity means taking responsibility not just for a proposed solution, but for discovering what actually needs to change and developing a way to make progress. Problem selection and problem solving are one continuous engagement with an evolving system. Calibration joins that judgment to a realistic model of systemic exposure: what a change can affect, how failure will present, and which next commitment is useful and affordable.

Role in the progression:
Synthesize the earlier essays' dependency, timing, and migration arguments into the judgment required to change complex systems. Return to the locally reasonable decisions that created the original Rails problem. Career progression illustrates the argument; it does not organize it.

Relationship to the companion essay:
Cheap Construction Is Not Progress applies this discipline to lower-cost software construction. Keep AI out of this capstone's central argument.

Editorial boundaries:
- Ground the personal lens in electrical/computer engineering labs, early QA, and mature business applications. Do not frame this as CS versus engineering.
- Use relationships to explain sustained engagement, evolving context, and reassessment, not an obligation to preserve every implementation.
- Do not imply that difficulty or neglect establishes value, or make other engineers' supposed lack of perseverance the contrast.
- The transaction/retry example is hypothetical, not a claim about an employer or a particular incident.
- Review overlap with article 4: migration mechanisms belong there; this piece explains how to choose and evaluate an intervention.

Publication gate:
Keep draft = true. Complete and refine all five drafts, conduct the corpus-level review, then finish and publish sequentially. Remove this working block before publication.
-->

In electrical and computer engineering labs, I would build something, measure its behavior, change something, and measure again. When the result disagreed with my expectations, I had something to investigate. The circuit did not become more cooperative because I preferred the theory.

My first job in software was in quality assurance. That sharpened a prerequisite I had not fully appreciated: before a failure can teach you anything, you need to establish what you expected to happen.

I brought those habits into large business applications, including aging Rails codebases. The difficult parts were rarely isolated algorithms. They were business rules interacting with other business rules, assumptions spread across components, and years of decisions whose reasons were no longer immediately visible. Much of the work was careful observation, engineering hygiene, and iteration.

I had not arrived expecting the problems to take one particular form. They were the systems in front of me, and they needed to change while continuing to serve the businesses that depended on them.

## What counts as failure

QA gave me a way to turn an impression into a question I could investigate. Saying that a system was broken was not enough. What should it have done? Under which conditions? What observation would distinguish the expected behavior from the behavior we had?

That also matters when the implementation is unfamiliar. Existing behavior tells you what the system does; it does not, by itself, settle what the system should do. Some behavior is a requirement nobody wrote down. Some is a workaround. Some is a bug that another component has learned to accommodate. Before changing it, you need to understand which distinction matters to the people relying on it.

Consider a hypothetical checkout operation that updates an order in a database and asks a separate payment service to charge the customer. The payment succeeds, but the local operation fails before it records the result. A database rollback cannot undo a charge the payment service has already accepted.

The local code might look straightforward. Understanding the failure requires a larger view: which system owns the payment state, what the caller knows, what a retry will do, and how an uncertain result gets reconciled. Concurrent requests can make the same uncertainty visible in another way. Counting changed lines tells you little about that exposure.

A useful test might arrange for the payment to succeed while its reply is lost, then check whether recovery produces one charge and a consistent order state. The expected behavior makes the failure interpretable. Without it, a green test could mean only that the method returned without raising an exception.

This is why transactional reasoning is such a useful test of engineering judgment. It requires you to follow state and effects across time, ownership, and failure boundaries rather than stop at the edge of the function you are editing.

I think of calibration as improving the correspondence between those expectations and what actually happens. It includes knowing where my understanding is weak enough that I should narrow the change or gather more evidence first.

## Systems do not stay solved

A homework problem normally supplies a question and some boundary on what counts as completion. A company keeps changing both.

New customers arrive with different requirements. A process that used to be manual becomes automated. Two teams acquire separate responsibilities for behavior that once lived comfortably together. An assumption can stop being useful without ever having been unreasonable.

That is why I think of a mature codebase as an ongoing relationship. You develop context through sustained attention: what it does reliably, where it surprises you, what its users depend on, and which compromises have outlived their purpose. You can get frustrated with it without treating frustration as evidence that the whole thing should be discarded.

The relationship can also stagnate. Familiarity makes it easier to navigate a constraint without questioning it. A release requiring coordination across several teams can become routine. So can a manual reconciliation step that everyone knows how to perform. The organization gets better at living with the problem, which can make the problem less visible.

Cultivating the system means revisiting those arrangements as the business changes. It includes leaving working parts alone when changing them would buy little. Sometimes it requires replacing or retiring an implementation. The commitment is to the business's ability to function and change, not to preserving a particular body of code.

There is no final architecture that releases us from that attention. There can be finished projects, removed dependencies, and retired systems. The surrounding business still presents new questions.

## Learning what needs to change

Return to the checkout example. Suppose the assignment is to make retries reliable. Following one failed operation might reveal that several entry points can initiate the same charge, each with a different understanding of what has already happened.

The stated problem concerns retry handling. The more consequential problem may be ownership: there is no single place responsible for deciding whether this payment operation should happen again. Adding another exception handler could make one path look healthier while leaving that ambiguity intact.

You do not need a complete map of the business to discover this. You need enough context to follow the operation beyond the point where the local explanation stops accounting for its behavior. The investigation may justify routing one class of operation through an explicit owner before trying to replace the rest of the payment flow. It may instead show that the existing owner is adequate and one caller is violating its contract. Those findings call for different work.

Sometimes understanding the larger system reveals that a small change will solve most of the practical problem. Sometimes a small investigation exposes a larger constraint. Neither direction can be prescribed in advance. The problem is what it is, not what would fit most comfortably into the solution I already know how to build.

This is where problem selection and problem solving become inseparable. Engaging with a problem changes my understanding of its importance, and attempting a bounded improvement tests whether I have identified the right cause. New evidence can justify expanding the work, narrowing it, or stopping.

A senior engineer can make progress on a poorly defined problem. At staff and principal levels, I expect responsibility to include discovering which problems deserve the organization's attention and bringing the relevant people together to address them. That is the same discipline applied before there is an agreed assignment. It requires enough engagement to understand both the consequence of the problem and the cost of doing something about it.

Some consequential problems are ones people have learned to live with. Neglect alone does not establish their importance. A difficult subsystem might be stable and rarely changed; an unremarkable ownership ambiguity might affect every release. Judgment means distinguishing those situations, including recognizing when a persistent inconvenience is cheaper than its proposed cure.

## Make a commitment you can learn from

An incomplete understanding does not excuse indefinite investigation. At some point, you need to decide what to do next and what you expect to learn from it.

In the checkout example, reproducing an ambiguous payment outcome with a controlled substitute for the payment service may be the right first step. It lets you test recovery without exposing a customer to a second charge. If the behavior cannot be observed reliably, improving that visibility may be more useful than beginning the replacement.

The size of the code change is secondary. What matters is the scope of its possible effects, whether you can detect a bad result, and what recovery would require. Reverting code does not necessarily reverse what it has already done. A useful risk budget has to account for that difference.

Small interventions make learning affordable when they bound those consequences. They are not automatically informative. A change that cannot distinguish competing explanations may consume time without improving the next decision. Nor does learning require deliberately causing every possible failure. Existing incidents, operational knowledge, and careful reasoning can eliminate experiments we do not need to run.

Code review, controlled tests, shadow execution, and progressive delivery can each contribute different evidence. None removes the need to say what uncertainty it is meant to reduce. The migration techniques in the preceding essay put that discipline into practice; choosing among them depends on what we still need to understand.

An organization needs to make these commitments too. Someone must be accountable for the next increment, with a clear expectation of what it should change and when the result will be reviewed. Otherwise, uncertainty becomes a reason to keep reopening the decision rather than a condition the work is designed to manage.

Keep the destination revisable, but make a real commitment to the next useful step. The result may change the plan. That is different from never committing to a plan that could be tested.

## Back to the local decision

The first essay begins with reasonable local choices that compose into a system nobody intended. The response cannot simply be a better set of permanent rules. A boundary that is worth maintaining now may have been needless expense earlier. Two representations that look redundant may keep unrelated responsibilities from becoming coupled. A replacement that appears necessary may become smaller once its actual constraints are understood.

The series follows those decisions through their consequences. Calibration is what lets us return to them with better information: revise an abstraction, recognize that the economics have changed, or choose the next part of a migration. It also helps us recognize that the requested change is not the change the system needs.

Engineering is the discipline of making progress on problems we do not yet fully understand. Maturity means taking responsibility not just for a proposed solution, but for discovering what actually needs to change and developing a way to make progress.
