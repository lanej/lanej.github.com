+++
title = "When Simplicity Stops Being Cheap"
description = "Why the architecture that speeds discovery can become expensive after success"
date = "2026-09-26T21:10:00-07:00"
draft = true
+++

<!--
Working document: outline, not publication-ready prose.

Series: Architecture Under Uncertainty (3/5)

Complete thought:
Simple, collapsed architectures are often correct when product uncertainty is high. The failure is not starting simple; it is missing the inflection point where durable business behavior, integrations, and organizational scale make dependency reduction worth the cost. Architectural investment is asymmetric: too early wastes options, too late makes them expensive to buy.

Role in the progression:
Timing. Explain why both premature architecture and indefinitely deferred architecture are mistakes, and why startups systematically miss the transition.

Relationship to the next piece:
How to Rewrite a System You Can't Stop starts from the common case where the inflection point was missed and the migration must happen under load.

Keep this block until the article's argument is stable; remove it before publication.
-->

Simple, collapsed architectures are often correct when product uncertainty is high. The failure is not starting simple; it is missing the inflection point where durable business behavior, integrations, and organizational scale make dependency reduction worth the cost. Architectural investment is asymmetric: too early wastes options, too late makes them expensive to buy.

## Simple is often right at the beginning

- Early startups should optimize for learning and collapse distinctions that have not earned permanence.
- Do not retroactively condemn the architecture that enabled product discovery.

## Success changes the optimization function

- Customers, integrations, teams, and durable business rules increase the value of explicit boundaries.
- There is no event that announces the exact moment when the economics flip.

## The asymmetry

- Too early: pay for flexibility that may never be exercised.
- Too late: correct behavior, callers, jobs, APIs, and operational assumptions accumulate around early shortcuts.
- Technical debt does not merely accumulate; correct behavior accumulates around it.

## Why organizations miss it

- Delivery pressure remains visible while architectural ROI is deferred.
- Ownership is often ambiguous and infrastructure is undercapitalized.
- "Not yet" can be locally defensible every quarter and globally disastrous over years.

## A practical phase model

- Discovery: optimize for learning.
- Evidence: buy boundaries around concepts that have become real.
- Scale: extend boundaries rather than excavating them from a mature system.

## Hand-off

- End with the common reality: the transition was missed, the system is mission-critical, and stopping feature work is not credible.
- That creates the migration problem.
