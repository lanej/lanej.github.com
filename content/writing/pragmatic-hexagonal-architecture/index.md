+++
title = "Pragmatic Hexagonal Architecture"
description = "A small Rust reference showing where rules and effects separate, and how that separation contains change as requirements grow."
date = "2026-11-05T12:00:00-08:00"
draft = false
unlisted = true
essay_visual = "architecture"
+++

A reviewer leaves feedback on an infrastructure plan. One function could check whether the feedback still applies, format it, and post a GitHub comment. That is enough for the first request.

Now add another eligibility rule, a second way to submit reviews, a GitHub client upgrade, and delivery that survives a restart. If the rules, input formats, HTTP calls, and retry decisions all live together, understanding any one change requires understanding the others.

> As requirements accumulate, keep the amount of code needed to understand one change small.

The [runnable Rust reference](https://github.com/lanej/lanej.github.com/tree/48ece975c221442a3bd0d8e79d81a200d64f8e78/examples/review-publication) uses a hypothetical slice of Statecraft's infrastructure-review workflow. It demonstrates a functional core, an imperative shell, and a selective port to GitHub. I call the combination **pragmatic hexagonal architecture**. The useful property is that these responsibilities can grow for different reasons.

## Give the rule its own inputs and outputs

The rule needs a review and the identity of the current plan. A review contains its identity, the exact plan artifact it concerns, and its text. It needs no HTTP request, database connection, or GitHub SDK object.

The application owns those values and the possible decisions:

```text
pub enum Decision {
    Skip(SkipReason),
    Publish(Publication),
}
```

`Publication` contains the review identity, plan identity, and formatted body. It describes an intended effect; creating it sends nothing.

```text
pub fn decide(current_plan: &str, review: &Review) -> Decision {
    if review.plan_id != current_plan {
        return Decision::Skip(SkipReason::StalePlan);
    }
    if review.text.trim().is_empty() {
        return Decision::Skip(SkipReason::EmptyReview);
    }
    Decision::Publish(format_review(review))
}
```

This is the **functional core**: values in, a decision out. The same inputs produce the same decision. A test for stale feedback needs two plan identities and a review, with no server or mocks.

The **imperative shell** obtains those facts and acts on the result. It performs input parsing, loading, network calls, and persistence. Gary Bernhardt's *Functional Core, Imperative Shell* supplies this separation.[^functional-core] Calling a database through a trait would still be an effect.

The boundary limits what the rule must know. GitHub's representation of a comment cannot spread through the policy because it never enters it. These few application-owned types form a thin internal model; there is no need to reproduce the provider's entire schema.

Rust does not enforce purity. Keeping I/O out of this small module makes the property inspectable. Its enums provide a separate guarantee: exhaustive consumers must account for a new variant. The reference rejects wildcard enum arms in Clippy.

## Put effects behind a contract

The basic workflow translates a decision into an attempt:

```text
pub async fn publish_once(
    current_plan: &str,
    review: &Review,
    target: &GitHubTarget,
    github: &impl GitHubComments,
) -> Outcome {
    match decide(current_plan, review) {
        Decision::Skip(reason) => Outcome::Skipped(reason),
        Decision::Publish(publication) => {
            Outcome::Attempted(
                github.create(target, &publication.body).await,
            )
        }
    }
}
```

Its caller authenticates the request, supplies an authoritative current-plan snapshot, and chooses the destination. The workflow coordinates the rule and the effect. The GitHub adapter handles credentials, endpoint requests, pagination, and SDK responses.

The workflow owns the `GitHubComments` contract it consumes. The adapter implements it and translates provider responses into application outcomes. In the reference, that adapter uses **octorust**, generated from GitHub's OpenAPI description.[^octorust]

{{< review-boundaries >}}

At runtime the workflow calls the adapter. In source, the adapter depends on the workflow's contract. This inversion lets the application describe the operation it needs without importing the SDK.

That inside/outside relationship comes from Alistair Cockburn's hexagonal architecture.[^hexagonal] Functional core, imperative shell addresses the separation of decisions from effects; ports and adapters addresses dependencies across the application's external boundaries. A port does not make effectful code pure.

This boundary has a cost: a contract, response mapping, and tests that keep the mapping honest. It earns that cost here because provider failures must be reproducible without calling GitHub. It does not require a universal `Message` interface spanning email, chat, and issue comments.

## Watch requirements accumulate

Start with the stale-plan check. Adding the empty-review guard changes the policy and its tests. The existing `Publish(Publication)` contract still carries a body to GitHub. The adapter needs no knowledge of the new eligibility rule. A caller displaying each skip reason must handle `EmptyReview`; the enum makes that obligation visible.

Next, suppose reviews can arrive through a webhook as well as the demonstration's command-line entry point. The new entry point would authenticate and parse its payload, obtain the current plan, construct a `Review`, and call the same workflow. It would reuse the eligibility rule instead of copying it into a controller. This is an extension the boundaries permit; the reference does not implement a webhook server.

A GitHub client upgrade has a different scope. When request or response shapes change, the adapter's mapping changes. As long as it preserves the application's contract, neither entry point nor the eligibility rule needs the SDK's new representation.

| Requirement | Work introduced | Knowledge kept local |
| --- | --- | --- |
| Skip empty feedback | Policy guard, skip reason, tests | Eligibility rules |
| Accept webhook submissions | Entry point and composition | Transport, authentication, input shape |
| Change GitHub response handling | Adapter mapping and fixture tests | Provider protocol and SDK types |
| Survive a restart | Recovery coordinator and journal | Attempt history and delivery uncertainty |

Each addition has a place because each boundary hides a different decision. This follows Parnas's criterion of organizing modules around design decisions that other modules should not need to know.[^modularity]

The benefit is visible in the work a change avoids: a new input path does not duplicate the rule, and a provider change does not require reviewing the rule for accidental edits. Rule tests stay small even when the surrounding integrations grow.

The contracts can still change. If feedback must expire after an hour, the core needs timestamps and the shell must supply them. That requirement crosses the boundary because the rule needs a new fact. Explicit inputs make the coordination visible; they cannot eliminate it.

## Add coordination for a stronger delivery promise

`publish_once` makes one attempt. Restart-safe delivery introduces additional states and ordering constraints. The adapter preserves the information that coordination needs:

```text
pub enum WriteOutcome {
    Published(NonZeroU64),
    Rejected { reason: String },
    Unknown { reason: String },
}
```

An authentication rejection and a write whose response was lost permit different next actions. A boolean would erase that distinction.

The included `recovery.rs` extension adds a concrete SQLite journal. It records an attempt before calling GitHub, preserves confirmed receipts when a newer plan appears, and rejects reuse of an identity with different content. It reuses the same pure decision and GitHub contract.

An unknown attempt remains unknown across restart. Reconciliation looks for the publishing account and complete expected body across comment pages. A marker helps correlate evidence; GitHub does not enforce it as an idempotency key.[^github] An unsuccessful search never authorizes a second create. A definite rejection permits an explicit retry after correction. The SDK's default retry middleware is disabled.

This policy has a cost: a crash after reservation but before sending can leave an unsent comment unknown indefinitely. Workers must share the journal, and losing its records loses that protection. The extension trades automatic eventual delivery for avoiding another create through that journal.

The extra complexity follows from a stronger delivery requirement. It lives in a coordinator and persistence module, where its state transitions and failure cases can be examined together. Adding it does not make the stale-plan predicate harder to read.

## Keep the system understandable in parts

As the application gains other capabilities, give each its own nearby rules, workflow, and integrations. Plan approval need not join one application-wide policy module just because review publication already has a core. Group code by the capability a reader is changing; separate responsibilities within it.

Keep a contract narrow enough to preserve its meaning. Renaming GitHub comments to generic messages would create a broader promise without resolving a current source of coupling. The journal can remain concrete SQLite until an actual replacement or isolation requirement justifies another port. Composition is ordinary Rust constructing collaborators and passing references; static dispatch needs no dependency-injection container.

Tests follow the same knowledge boundaries. Pure tests challenge the decisions. Workflow tests check which effects are requested. Adapter tests exercise the generated client against a local HTTP fixture. Recovery tests reopen SQLite, race independent connections, and distinguish rejection from uncertainty. They establish bounded properties, including response loss without an automatic second POST; they do not establish live GitHub behavior or durability under a real disk failure.

These boundaries organize source and reasoning inside one application. They do not by themselves increase throughput or make deployment independent. The current plan is also a snapshot: publishing feedback about an artifact does not authorize applying it. Executing infrastructure would need authorization bound to the exact artifact at execution.

In an existing Rails application, the first step could be extracting one decision from an ActiveRecord callback into a function over explicit values. Leave loading and saving in the caller. Add a provider boundary when provider details spread, and durable coordination when an effect requires it.

Review the result against actual changes. If one eligibility rule repeatedly requires edits in controllers and adapters, its knowledge is leaking. If a boundary adds mapping and navigation without containing change or isolating a meaningful failure, simplify it.

[^functional-core]: **[Functional Core, Imperative Shell](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)**\
    Gary Bernhardt · 2012

    Separates functional decisions from code handling interaction with the world. The delivery policy in this reference is a separate application choice.

[^hexagonal]: **[Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)**\
    Alistair Cockburn · 2005

    Describes ports and adapters at the inside/outside boundary. It does not require every internal function to be pure or every dependency to receive an interface.

[^modularity]: **[On the Criteria To Be Used in Decomposing Systems into Modules](https://doi.org/10.1145/361598.361623)**\
    D. L. Parnas · 1972

    Compares decompositions by how changes propagate and how independently modules can be understood. The staged review-publication example here is my application of that criterion.

[^octorust]: **[octorust](https://docs.rs/octorust/0.10.0/octorust/)**\
    Oxide Computer · Client documentation

    The reference pins this generated client and disables default middleware, which otherwise includes retries. Request construction and pagination stay inside the adapter.

[^github]: **[REST API endpoints for issue comments](https://docs.github.com/en/rest/issues/comments)**\
    GitHub documentation

    Documents creation and listing of issue and pull-request conversation comments. The journal and conservative recovery policy are application choices.
