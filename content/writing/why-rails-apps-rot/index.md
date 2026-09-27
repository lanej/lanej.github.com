+++
title = "Why Rails Apps Rot"
description = "How reasonable Rails conventions compound into architectural coupling"
date = "2026-09-26T21:10:00-07:00"
draft = true
+++

<!--
Working document: outline, not publication-ready prose.

Series: Architecture Under Uncertainty (1/5)

Complete thought:
Messy Rails applications are often the predictable result of several locally reasonable forces composing badly: object-oriented behavior placement, ActiveRecord collapsing persistence and domain identity, loose message coupling, fat-model guidance, and DRY. Nobody has to make an obviously bad decision for the global architecture to become hard to change.

Role in the progression:
Diagnosis. Establish that architecture can degrade through locally reasonable choices, which creates the need to reconsider what we are optimizing.

Relationship to the next piece:
Sometimes You Should Repeat Yourself asks whether minimizing duplicated concepts is the wrong architectural objective.

Keep this block until the article's argument is stable; remove it before publication.
-->

Messy Rails applications are often the predictable result of several locally reasonable forces composing badly: object-oriented behavior placement, ActiveRecord collapsing persistence and domain identity, loose message coupling, fat-model guidance, and DRY. Nobody has to make an obviously bad decision for the global architecture to become hard to change.

## Start with the observed pattern

- Open from repeated experience with mature Rails systems rather than a generic framework critique.
- Show how individual changes can each look reasonable while the dependency graph becomes progressively harder to see.

## Reasonable forces that compound badly

- OOP encourages putting behavior on the object it concerns.
- ActiveRecord makes the persistence representation look like the domain object.
- Loose message passing hides system-level dependencies behind clean local call sites.
- "Fat models, skinny controllers" gives business behavior a gravitational home.
- DRY rewards collapsing similar representations into one.

## The missing boundary

- Rails has strong homes for persistence, requests, and rendering, but no equally strong architectural home for business/application logic.
- Service objects, interactors, operations, and concerns are symptoms of that missing architecture; without a defined role they become new junk drawers.

## Why this is not a blame story

- Do not argue that Rails developers were careless or that Rails was the wrong startup choice.
- The point is that good local rules do not necessarily compose into good global architecture.

## Hand-off

- End by asking whether the deeper mistake was treating fewer representations as inherently better.
- That question leads directly into the dependency-versus-duplication argument.
