+++
title = "Sometimes You Should Repeat Yourself"
description = "Why reducing dependencies sometimes requires duplicating representations"
date = "2026-09-26T21:10:00-07:00"
draft = true
+++

<!--
Working document: outline, not publication-ready prose.

Series: Architecture Under Uncertainty (2/5)

Complete thought:
DRY optimizes the number of representations; architecture often needs to optimize the dependency graph. Two similar representations can be desirable when they isolate boundaries. Functional core / imperative shell, a thin canonical model, and consumer-owned interfaces provide a more useful way to decide what should be shared.

Role in the progression:
Reframe. Replace concept reduction with dependency reduction as the primary architectural lens.

Relationship to the next piece:
When Simplicity Stops Being Cheap adds the missing timing dimension: these boundaries are valuable, but often premature at the beginning.

Keep this block until the article's argument is stable; remove it before publication.
-->

DRY optimizes the number of representations; architecture often needs to optimize the dependency graph. Two similar representations can be desirable when they isolate boundaries. Functional core / imperative shell, a thin canonical model, and consumer-owned interfaces provide a more useful way to decide what should be shared.

## The wrong graph

- Contrast minimizing representations with minimizing dependencies.
- Use OrderRecord, DomainOrder, CarrierOrder, and OrderPayload as an example where duplication buys isolation.

## Sometimes duplication is the price of decoupling

- Explain why explicit translation can be cheaper than a universal shared object.
- DRY is a useful local optimization, not an architectural law.

## Functional core, imperative shell

- Give business decisions a pure or mostly pure home.
- Let the shell own sequencing, I/O, transactions, retries, persistence, and external effects.
- Let integration modules own vendor semantics and translation.

## The thin waist

- Normalize only concepts the application genuinely owns.
- Do not force every provider capability into a common abstraction.
- Preserve provider-specific behavior when it is not meaningfully fungible.

## What Go changed for me

- Use Go as a contrast rather than a language-war conclusion.
- Consumer-owned interfaces, implicit satisfaction, composition, explicit mapping, and cheap structs make dependency boundaries easier to preserve.
- Key line: I used to see two similar structs and ask why they were not one thing; now I ask what dependency I would create by making them one thing.

## Hand-off

- Acknowledge that this architecture can be far too elaborate for an unproven idea.
- Lead into the question of when the economics change.
