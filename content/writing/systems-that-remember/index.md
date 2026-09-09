+++
title = "Systems That Remember"
description = "Failure becomes useful when its lesson stops depending on memory."
date = 2026-09-08T06:15:00-07:00
draft = false
essay_visual = "memory"
toc = false
+++

On August 27, a deployment briefly degraded EasyPost's Core APIs. At 10:26 AM, the change was identified and rolled back. By 10:40, the APIs were back to normal.[^status]

> The interesting part is that rollback was already available.

EasyPost deploys through a system built around canary traffic, retained previous versions, and immediate rollback.[^reliability] Those mechanisms did not make failure impossible. They changed what happened after failure.

They show what durable learning looks like once it has been encoded into the system, regardless of whether a particular mechanism came from an incident or deliberate design.

What matters after 10:40 is whether this incident leaves another durable change behind.

## Start with the system

When something goes wrong, my starting assumption is that the person nearest the failure is giving me evidence about the system around them.

That does not mean people never make mistakes, judgment does not matter, or performance problems should be ignored. It means that blaming the person who happened to trigger a failure is usually a poor way to understand why the failure was possible.

A deploy reaches too much traffic before anyone can see the effect. A dependency can stall every request thread. An operator has to remember an unusual recovery sequence. A dangerous state is technically valid because nothing rejects it.

The person is visible. The conditions that made the failure likely are less visible.

Google's SRE practice makes blamelessness part of the mechanics of learning, not just a preference about tone. Its postmortem guidance starts from the assumption that people acted in good faith with the information available to them, then looks for changes to systems, procedures, and training that reduce recurrence.[^google]

I like that framing because blame distorts signal. If surfacing a mistake is personally expensive, people become rationally selective about which mistakes they surface. Near misses stay private. Ambiguous evidence gets cleaned up before it is shared. The organization learns less because it has made learning risky.

Blamelessness is useful because it makes the system easier to investigate honestly.

## A postmortem can still forget

Writing down what happened is better than relying on memory. It is not the end state.

A postmortem can explain that a rollout needed better isolation. Six months later, a new engineer can ship without reading it. A runbook can explain the recovery sequence. At 3 AM, somebody can miss step seven. A document can say that a particular configuration is unsafe while the API continues to accept it.

The lesson still depends on a person remembering the lesson.

When possible, I want the learning to move closer to the place where the failure occurred.

| What we learned | What the system can remember |
| --- | --- |
| We could not see the failure early enough | Instrumentation, alerting, health checks |
| A change could affect too much traffic at once | Canarying, staged rollout, blast-radius controls |
| Recovery depended on a person remembering what to do | Automated rollback or recovery |
| A dependency can fail in a predictable way | Timeout, retry, fallback, isolation |
| An invalid state was allowed | Validation, invariant, test, policy |
| A procedure was repeatedly performed by hand | Automation |
| The interface made the wrong action easy | A simpler interface |

Not every lesson belongs in code. Some failures expose ambiguous goals, bad incentives, missing expertise, or genuinely contextual decisions. Those still require judgment.

But repeated mechanical corrections are a smell. If the same failure keeps producing the same reminder, the reminder is probably living at the wrong layer.

A postmortem records what happened. A system change records what was learned.

## Learning changes tools

Encoding a lesson changes more than the implementation. It changes the environment the next person operates inside.

A deployment tool that defaults to a canary makes gradual rollout ordinary. An API that rejects an unsafe configuration removes a decision somebody previously had to remember. Better instrumentation puts evidence in front of an operator before they have to remember to go looking for it.

The important mechanism is the default. People tend to take the path a system makes easiest, especially when they are busy, unfamiliar with it, or operating under pressure. A safer procedure that requires remembering an exception is weaker than a tool that makes the safer procedure ordinary.

This is the same idea behind a pit of success: do not merely tell people what the right action is. Shape the environment so that the right action is the natural action, and make the dangerous path harder or impossible when you can.

A postmortem can say, “canary this kind of change.” A deployment system can canary it by default. Training can say, “check this signal before proceeding.” A workflow can put that signal directly in the decision path. Documentation can say, “never create this state.” An API can refuse to create it.

The lesson changes the tool, and the tool changes the behavior that follows from it.

That gives me a useful test for whether an organization has really retained a mechanical lesson:

> A system remembers when someone who never learned the lesson still behaves differently because of it.

The next engineer does not need to know which incident produced a guardrail. They inherit the accumulated judgment embedded in the interface, the defaults, the automation, and the constraints around them.

Over time, the operating environment becomes a record of what the organization has learned.

## Reliability is accumulated memory

This is the part of incident response that compounds.

A perfectly monotonic uptime graph would be nice, but it is not how complex systems usually improve. Systems change, traffic changes, dependencies change, and new failure modes appear. A better system can still have an incident tomorrow.

What I want to see is accumulation.

EasyPost's release history includes repeated work on shipment-purchase performance, database-query performance, connection stability, USPS fallback handling, carrier timeout behavior, and other reliability or latency paths.[^releases]

Not every change is incident-driven. The important pattern is the accumulation of small changes to the mechanisms that determine how the system behaves when reality differs from the happy path.

The rollback path from the August incident shows the other side of that accumulation. The important fact is not that rollback was invented during the outage. It was already there. Some earlier decision had made recovery a capability of the system instead of an improvisation by the operator.[^reliability]

The capability was part of the system before anyone needed it that morning.

That is the operational version of the learning loop I described in [Close the Loop](/writing/close-the-loop/): failure produces evidence, but the loop is not really closed until that evidence changes future behavior.

## Make the lesson durable

Incidents already cost something: customer trust, engineering attention, interrupted work, lost sleep, sometimes money.

Restoring service stops the immediate cost. It does not recover it.

The return comes from learning something that changes the next failure. Maybe the next incident is detected earlier. Maybe its blast radius is smaller. Maybe recovery takes one action instead of twelve. Maybe the entire class of failure becomes impossible.

That is why I care more about the action that survives the postmortem than the postmortem itself.

People forget. Systems do not have to.

[^status]: EasyPost, [status page](https://www.easypoststatus.com/), incident history for August 27, 2026.
[^reliability]: EasyPost, [Shipping API Reliability Guide](https://www.easypost.com/blog/easypost-api-reliability-guide/), July 14, 2025.
[^google]: Google SRE, [Postmortem Culture: Learning from Failure](https://sre.google/sre-book/postmortem-culture/) and the [SRE Workbook chapter on postmortem culture](https://sre.google/workbook/postmortem-culture/).
[^releases]: EasyPost, [release history](https://docs.easypost.com/releases).
