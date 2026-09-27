+++
title = "How to Rewrite a System You Can't Stop"
description = "A practical migration model for replacing critical systems without stopping delivery"
date = "2026-09-26T21:10:00-07:00"
draft = true
+++

<!--
Working document: outline, not publication-ready prose.

Series: Architecture Under Uncertainty (4/5)

Complete thought:
A mature application rewrite should be run like a live migration, not a construction project. Move capability and state ownership incrementally, keep one authoritative writer, use strangler/delegation patterns, replay and shadow real behavior, and structure the work so each increment is net-positive even if the migration stops before completion.

Role in the progression:
Practice. Show how to act after the timing problem has already been missed, without requiring a heroic stop-the-world rewrite.

Relationship to the next piece:
Engineering Is Calibration generalizes the migration discipline into a model for individual and organizational decision-making under uncertainty.

Keep this block until the article's argument is stable; remove it before publication.
-->

A mature application rewrite should be run like a live migration, not a construction project. Move capability and state ownership incrementally, keep one authoritative writer, use strangler/delegation patterns, replay and shadow real behavior, and structure the work so each increment is net-positive even if the migration stops before completion.

## The system cannot stop

- The old application is usually important precisely because replacing it is difficult.
- A complete specification rarely exists; production behavior carries undocumented rules, ordering, retries, bugs, and assumptions.

## Strangler with delegation

- Introduce the new service as a client or delegate around the legacy system.
- Move operations one at a time until the legacy application becomes a proxy.
- Repoint callers last.

## One authoritative owner

- For each capability identify the authoritative implementation, state owner, and writer.
- Avoid shared database ownership; temporary compatibility reads are different from permanent shared mutation.
- Prefer CDC/outbox propagation over casual dual writes when possible.

## Treat behavior like data

- Use shadow execution, record/replay, dark launches, behavioral diffs, and progressive cutovers.
- Compare effects as well as responses: writes, events, jobs, and intended external calls.
- Production behavior is part of the specification when nobody fully understands the old business rules.

## The migration must pay rent early

- Useful milestones are safer deployments, replay capability, clearer ownership, independent rollback, or a removed dependency—not percent complete.
- If stopping halfway leaves only two systems instead of one, the migration was structured badly.

## Hand-off

- The hard question becomes how to choose the next increment when every intervention changes the system and can create non-local failure.
- That is a calibration problem.
