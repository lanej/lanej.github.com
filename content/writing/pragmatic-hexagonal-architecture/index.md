+++
title = "Pragmatic Hexagonal Architecture"
description = "A small Rust reference: pure decisions, explicit effects, a thin internal model, and boundaries that justify their cost."
date = "2026-11-05T12:00:00-08:00"
draft = false
unlisted = true
essay_visual = "architecture"
+++

A reviewer leaves feedback on an infrastructure plan. We need to decide whether that feedback still applies, then publish it as a GitHub comment identifying the exact plan.

The rule and the publication call have different reasons to change. A review policy can change while GitHub's API stays the same. GitHub can change while the policy remains valid. I want a reader to find either responsibility without understanding the other first.

> Keep decisions easy to challenge, effects explicit, and each boundary accountable for the complexity it adds.

I call this **pragmatic hexagonal architecture**: functional core, imperative shell, a thin internal model, and selective ports and adapters. It combines existing ideas with a judgment about how much separation the problem needs.

The [runnable Rust reference](https://github.com/lanej/lanej.github.com/tree/master/examples/review-publication) uses a hypothetical slice of Statecraft's infrastructure-review workflow. It is a teaching example, separate from Statecraft's implementation. Start with `policy.rs` and `workflow.rs`; the durable-delivery extension can wait until those boundaries are clear.

## Give the rule a home

The application owns a few values. A review identifies an immutable plan artifact. A commit alone is insufficient: two plans produced from the same commit may differ.

```text
pub struct Review {
    pub id: String,
    pub plan_id: String,
    pub text: String,
}

pub struct Publication {
    pub review_id: String,
    pub plan_id: String,
    pub body: String,
}

pub enum SkipReason {
    StalePlan,
    EmptyReview,
}

pub enum Decision {
    Skip(SkipReason),
    Publish(Publication),
}
```

The rule skips feedback for another plan, skips empty feedback, and otherwise prepares a publication naming the reviewed artifact:

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

`format_review` is another ordinary pure function. It returns the review identity, plan identity, and a body beginning with `Review of plan ...`.

These functions receive values and return values. They perform no I/O or mutation outside themselves. The same inputs produce the same decision. If a rule needs the time, pass the relevant timestamp in; reading the clock is an effect too.

Gary Bernhardt's *Functional Core, Imperative Shell* describes this separation between functional decisions and interaction with the world.[^functional-core] Here, a stale-plan test needs two identifiers and a review. It needs no server, database, or mocks.

Rust does not enforce purity. The small module makes its absence of I/O inspectable. Its enums give us a different guarantee: a `match` must handle every variant. The reference also rejects wildcard enum arms in Clippy, so adding a decision forces its consumers to be considered.

## Let the shell perform the effects

The basic shell is short:

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

The shell selects the consequence of a decision and executes it. Authentication, input parsing, and obtaining an authoritative current-plan snapshot belong to its caller. The policy stays independent of those mechanisms.

The application owns `Review`, `Publication`, and `Decision`. The GitHub integration owns its API response types. It translates a provider response into a small application outcome. That is the thin internal model: preserve the concepts our rules need, while containing representations we do not control.

The workflow can know that it publishes GitHub issue or pull-request conversation comments. The rule deciding which plan a review concerns has no reason to know the GitHub API. Creating a universal `Message` abstraction for GitHub, chat threads, and email would add promises this capability does not need.

Hexagonal architecture supplies the broader inside/outside boundary. Alistair Cockburn's account emphasizes running an application independently of its external devices through ports and adapters.[^hexagonal] A pure core is a further choice: calling a database through a trait still performs I/O.

## Invert the dependency that matters

The consuming workflow defines `GitHubComments`. Its `create` operation returns a typed `WriteOutcome`; its `find` operation supports the recovery extension. The GitHub adapter implements that contract.

At runtime, the workflow calls the adapter. In source, the adapter imports the workflow's contract. Those directions are different.

{{< review-boundaries >}}

The boundary earns its cost by making provider behavior reproducible, including a write accepted by the provider whose response never arrives. The real adapter uses **octorust**, generated from GitHub's OpenAPI description.[^octorust] SDK types, request construction, and pagination stay inside that integration.

The journal remains a concrete SQLite implementation. The function deriving a publication key remains a function. Neither gets a trait for symmetry. A storage migration or a demonstrated isolation need could justify another boundary later.

Composition is ordinary Rust constructing collaborators and passing references. Static dispatch needs no dependency-injection container. The modules live together under `review-publication`, so reading the capability does not require visiting application-wide directories for every architectural layer.

| Change | Where it belongs | What stays independent |
| --- | --- | --- |
| Review eligibility changes | Pure policy | GitHub requests and storage |
| A provider response changes | GitHub integration | Review rules |
| Delivery must survive restart | Recovery and journal | The pure decision |
| A small formatting rule changes | A function | No new interface is required |

## Extend delivery when the promise requires it

`publish_once` makes one attempt. It has no restart or retry guarantee. Its outcome model preserves the distinction we need before adding either:

```text
pub enum WriteOutcome {
    Published(NonZeroU64),
    Rejected { reason: String },
    Unknown { reason: String },
}
```

A confirmed authentication rejection and a lost response describe different knowledge. Treating both as `false` or swallowing both into `unknown` loses information the caller needs.

The optional `recovery.rs` extension adds a durable journal. It canonicalizes the destination, checks for an existing receipt before applying current eligibility rules, and reserves an attempt before calling GitHub. A previously published review remains published when a newer plan appears. Reusing its identity with different content is rejected.

An unconfirmed write stays unknown across restart. Repeating the request does not issue another create. Reconciliation reads all comment pages and checks the publishing account and entire expected body. A marker helps correlate evidence; it is not a provider-enforced idempotency key.[^github]

A definite rejection retains its cause and permits an explicit retry after the problem is corrected. An unknown write requires evidence. Absence from a read never authorizes another create.

There is a cost: a crash after reservation but before sending can leave an unsent comment unknown indefinitely. This extension gives up automatic eventual delivery to avoid issuing a second create through the same journal. Workers must share that journal, and losing its records loses that protection.

That delivery promise justifies the extra machinery. The pure-core boundary alone does not provide it.

## Challenge the promises at their boundaries

Pure tests challenge stale-plan rejection, empty feedback, and the identity in the publication. Workflow tests check which effects occur. Recovery tests reopen SQLite, race independent connections, advance the current plan between requests, and distinguish rejection from uncertainty.

Adapter tests run the generated client against a local HTTP fixture. They exercise request mapping, pagination, author matching, definite authentication rejection, and response loss without an automatic second POST. The dependency disables its default retry middleware.

Those tests establish bounded properties. They do not establish live GitHub behavior, authorization correctness, or durability under a real disk failure. The current-plan value is a snapshot; publishing feedback about an artifact does not authorize applying it. Applying infrastructure would require binding authorization to the exact artifact at execution.

For an existing Rails application, the first useful change might be extracting one decision from an ActiveRecord callback into a function over explicit values. Keep loading and saving in the caller. Add an integration module when provider details spread. Add durable outcome handling when a side effect requires it.

Each boundary should make an actual rule, change, or failure easier to reason about. Stop adding boundaries when they stop doing that.

[^functional-core]: **[Functional Core, Imperative Shell](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)**\
    Gary Bernhardt · 2012

    Describes a functional core surrounded by imperative code handling input, output, database, and network interaction. The recovery policy here is a separate application choice.

[^hexagonal]: **[Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)**\
    Alistair Cockburn · 2005

    Explains the inside/outside boundary, ports and adapters, and running an application independently of external devices. It does not require every internal function to be pure or every dependency to receive an interface.

[^octorust]: **[octorust](https://docs.rs/octorust/0.10.0/octorust/)**\
    Oxide Computer · Client documentation

    A client generated from GitHub's OpenAPI description. The reference pins its version and disables default middleware, which otherwise includes retries. It uses generated endpoint methods and pagination rather than a handwritten HTTP client.

[^github]: **[REST API endpoints for issue comments](https://docs.github.com/en/rest/issues/comments)**\
    GitHub documentation

    Documents creation and listing of issue and pull-request conversation comments. Inline pull-request review comments use a different API. The journal and recovery policy are application choices, not delivery guarantees supplied by this documentation.
