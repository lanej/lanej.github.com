+++
title = "Systems That Remember"
description = "Failure becomes useful when its lesson stops depending on memory."
date = 2026-09-08T06:15:00-07:00
draft = false
toc = false
+++

On August 27, EasyPost's public status page recorded a brief degradation of the Core APIs during a deployment. At 10:26 AM, the change was identified and rolled back. By 10:40, the APIs were back to normal.[^status]

The useful part of that incident is not that somebody reacted quickly.

EasyPost's public reliability guide describes a deployment system built around canary traffic, retained previous versions, and immediate rollback.[^reliability] The incident still happened. The mechanism did not make failure impossible. It changed what happened after failure.

That distinction matters to me.

I do not want an incident-response culture where the lesson is "be more careful next time." People will forget. Teams will change. Context will disappear. Under pressure, somebody will make the same reasonable decision again.

The useful outcome of an incident is a system that has changed because the incident happened.

## The people aren't wrong; the system is broken

For incident analysis, this is usually my starting assumption.

It does not mean people never make mistakes, judgment does not matter, or performance problems should be ignored. It means that blaming the person who happened to trigger a failure is usually a poor way to understand why the failure was possible.

A deploy reaches too much traffic before anyone can see the effect. A dependency can stall every request thread. An operator has to remember an unusual recovery sequence. A dangerous state is technically valid because nothing rejects it.

The person nearest the failure is visible. The conditions that made the failure likely are less visible.

Google's SRE practice makes blamelessness part of the mechanics of learning, not just a preference about tone. Its postmortem guidance starts from the assumption that people acted in good faith with the information available to them, then looks for changes to systems, procedures, and training that reduce recurrence.[^google]

I like that framing because blame destroys signal. If surfacing a mistake is personally expensive, people become rationally selective about which mistakes they surface. Near misses stay private. Ambiguous evidence gets cleaned up before it is shared. The organization learns less precisely because it has made learning risky.

Blamelessness is useful because it lets you investigate the system honestly.

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

## The learning loop

In [Close the Loop](/writing/close-the-loop/), I separated two kinds of feedback.

The execution loop is short: act, observe, correct, verify.

The learning loop takes longer: failure, reflection, lesson, mechanism, future behavior.

Incident response sits between them. During the incident, the objective is to restore a safe operating state. Afterward, the objective changes. Now the failure is evidence about the design.

A good postmortem asks what happened and why. A good engineering organization then asks a harder question:

> **What should be different in the system when the next person encounters this situation?**

That can result in a test. It can result in a new metric. It can result in changing a deployment system, removing an unsafe option, reducing coupling, or deleting a procedure entirely.

The important property is that the lesson survives the people who learned it.

## Reliability is accumulated memory

This changes how I think about reliability over time.

A perfectly monotonic uptime graph would be nice, but it is not how complex systems usually improve. Systems change, traffic changes, dependencies change, and new failure modes appear. A better system can still have an incident tomorrow.

What I want to see is accumulation.

EasyPost's public release history repeatedly records work on shipment-purchase performance, database-query performance, connection stability, USPS fallback handling, carrier timeout behavior, and other reliability or latency paths.[^releases] The public record cannot tell you which of those changes came from a specific incident or postmortem, and I would not infer that causal chain from release notes alone.

What it does show is the shape of reliability work: many small changes to the mechanisms that determine how the system behaves when reality differs from the happy path.

The same is true of the rollback path from the August incident. The important fact is not that rollback was invented during the outage. It was already there. Some earlier decision had made recovery a capability of the system instead of an improvisation by the operator.[^reliability]

That is what compounding looks like in operations. Yesterday's hard-earned lesson becomes today's default behavior.

## Make the lesson cheaper than the incident

Incidents already cost something: customer trust, engineering attention, interrupted work, lost sleep, sometimes money.

Restoring service stops the immediate cost. It does not recover it.

The return comes from learning something that changes the next failure. Maybe the next incident is detected earlier. Maybe its blast radius is smaller. Maybe recovery takes one action instead of twelve. Maybe the entire class of failure becomes impossible.

That is why I care more about the action that survives the postmortem than the postmortem itself.

People forget. Systems do not have to.

[^status]: EasyPost, [public status page](https://www.easypoststatus.com/), incident history for August 27, 2026.
[^reliability]: EasyPost, [Shipping API Reliability Guide](https://www.easypost.com/blog/easypost-api-reliability-guide/), July 14, 2025.
[^google]: Google SRE, [Postmortem Culture: Learning from Failure](https://sre.google/sre-book/postmortem-culture/) and the [SRE Workbook chapter on postmortem culture](https://sre.google/workbook/postmortem-culture/).
[^releases]: EasyPost, [public release history](https://docs.easypost.com/releases).