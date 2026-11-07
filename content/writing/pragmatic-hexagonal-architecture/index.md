+++
title = "Pragmatic Hexagonal Architecture"
description = "Two Rust slices, interchangeable GitHub and GitLab publishers, and storage ports that keep provider changes separate from business rules."
date = "2026-11-05T12:00:00-08:00"
draft = false
unlisted = true
essay_visual = "architecture"
code_source = "https://github.com/lanej/lanej.github.com/blob/a14575118a9eb2bcbe15fe5360e52549882bca4b/examples/plan-review"
+++

A reviewer leaves feedback on an infrastructure plan. The application checks that the review concerns the current artifact, formats the text, and publishes it to a code-review thread. One function can handle the first request.

Then the application needs plan approval. Authors must not approve their own work. Approval belongs to an exact artifact and must be recorded, while feedback goes to GitHub or GitLab. These capabilities share storage, but their rules and effects differ. A GitHub outage should not prevent an otherwise valid approval.

> As requirements accumulate, keep the amount of code needed to understand one change small.

The [runnable Rust reference](https://github.com/lanej/lanej.github.com/tree/a14575118a9eb2bcbe15fe5360e52549882bca4b/examples/plan-review) implements both capabilities in a hypothetical Statecraft application. GitHub and GitLab implement one publication port; SQLite and memory implement the storage contracts. Tests exercise these choices through the same application workflows. I call this combination of a functional core, an imperative shell, and selective ports **pragmatic hexagonal architecture**.

## Give a decision its own inputs and outputs

Start with publication. `Review` contains the review identity, the exact plan artifact it concerns, and its text. The rule receives those values and the current artifact ID. It returns `Decision::Skip(reason)` or `Decision::Publish(publication)`:

```rust {filename="src/publish_review/policy.rs"}
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

`Publication` contains the review identity, plan identity, and formatted body. It describes an intended effect; constructing it sends nothing. Stale-plan and empty-feedback tests need ordinary values, with no server or mocks.

This is the **functional core**: the same inputs produce the same decision. The **imperative shell** obtains facts and acts on the result, handling loading, network calls, and persistence. Gary Bernhardt's *Functional Core, Imperative Shell* supplies this separation.[^functional-core]

The core imports no SDK or database types. A provider's representation cannot spread through a rule it never enters. Rust does not enforce purity; keeping I/O out of this small module makes the property inspectable. Its enums provide a different guarantee: exhaustive consumers must account for a new variant. The reference rejects wildcard enum match arms in Clippy.

## Give one port two real adapters

Publication needs the current artifact and a way to publish review feedback. `CurrentPlan` supplies the artifact ID. `ReviewPublisher` describes the delivery conversation:

```rust {filename="src/publish_review/workflow.rs"}
pub trait ReviewPublisher: Sync {
    fn publish(&self, publication: &Publication) -> impl Future<Output = WriteOutcome> + Send;
}
```

The destination belongs to adapter configuration. A GitHub adapter knows an owner, repository, and pull-request number; a GitLab adapter knows a project ID and merge-request IID. Those identifiers never enter this workflow:

```rust {filename="src/publish_review/workflow.rs"}
pub async fn publish_once(
    review: &Review,
    plans: &impl CurrentPlan,
    publisher: &impl ReviewPublisher,
) -> Result<Outcome, String> {
    let current_plan = plans.current_plan_id()?;
    match decide(&current_plan, review) {
        Decision::Skip(reason) => Ok(Outcome::Skipped(reason)),
        Decision::Publish(publication) => {
            Ok(Outcome::Attempted(publisher.publish(&publication).await))
        }
    }
}
```

Both providers implement the same port. GitHub delegates to the generated **octorust** client behind its adapter:[^octorust]

```rust {filename="src/publish_review/github.rs"}
impl ReviewPublisher for GitHubPublisher {
    async fn publish(&self, publication: &Publication) -> WriteOutcome {
        self.github.create(&self.target, &publication.body).await
    }
}
```

GitLab delegates to its implementation of the merge-request Notes API, using the existing HTTP dependency:[^gitlab]

```rust {filename="src/publish_review/gitlab.rs"}
impl ReviewPublisher for GitLabPublisher {
    async fn publish(&self, publication: &Publication) -> WriteOutcome {
        self.create_note(&publication.body).await
    }
}
```

These adapters have the same application purpose. Changing code hosts changes construction and provider mapping; the workflow still loads an artifact, makes the same decision, and passes the same `Publication` to its publisher. The port is specific to publishing plan-review feedback. It does not promise a universal interface for email, chat, and every kind of message.

A lookup remains an effect even behind a trait. A failed lookup returns before publication; a decision to skip also sends nothing. The pure decision and the external contract solve different problems: one separates rules from effects, while the other contains knowledge of external systems.

{{< review-boundaries >}}

At runtime the workflow calls its publisher. In source, each adapter imports and implements the consuming workflow's contract. That inside/outside relationship comes from Alistair Cockburn's ports and adapters architecture.[^hexagonal]

The callable workflow is also an input boundary. The offline CLI and tests drive the same function. An HTTP handler could call it after authentication and input mapping; this reference does not include a webhook server. An input boundary can be an ordinary function.

## Add a slice with a different reason to change

Plan approval has its own request, decision, workflow, and port under `approve_plan/`. Its rule needs an artifact's author as well as its identity:

```rust {filename="src/approve_plan/policy.rs"}
pub fn decide(plan: &Plan, request: &Request) -> Decision {
    if request.plan_id != plan.id {
        return Decision::Reject(Rejection::StalePlan);
    }
    if request.approver == plan.author {
        return Decision::Reject(Rejection::SelfApproval);
    }
    Decision::Record(Approval {
        plan_id: request.plan_id.clone(),
        approver: request.approver.clone(),
    })
}
```

This rule has no reason to know how review text is formatted or how GitHub represents a comment. Publication has no reason to import approval's `Plan` type or self-approval rule.

Approval owns a different storage conversation:

```rust {filename="src/approve_plan/workflow.rs"}
pub trait ApprovalRecords {
    fn current_plan(&self) -> Result<Plan, String>;
    fn record(&self, approval: &Approval) -> Result<RecordOutcome, String>;
}
```

The adapter supplies the context and records a prepared approval. Its record operation must atomically check that the artifact is still current, because the plan can change after the read. The workflow preserves that distinction:

```rust {filename="src/approve_plan/workflow.rs"}
pub fn approve(request: &Request, records: &impl ApprovalRecords) -> Result<Outcome, String> {
    let plan = records.current_plan()?;
    match decide(&plan, request) {
        Decision::Reject(reason) => Ok(Outcome::Rejected(reason)),
        Decision::Record(approval) => match records.record(&approval)? {
            RecordOutcome::Recorded => Ok(Outcome::Recorded(approval)),
            RecordOutcome::PlanChanged => Ok(Outcome::Rejected(Rejection::StalePlan)),
        },
    }
}
```

Each directory is a **vertical slice**: the code for one capability, with its own functional core and imperative shell. Neither slice imports the other. Both storage adapters implement `CurrentPlan` and `ApprovalRecords`, translating their stored representation into the different values each consumer needs.

{{< review-slices >}}

This is where sharing has a concrete purpose. GitHub and GitLab are alternatives for one port. SQLite has a different relationship: one adapter serves two narrow storage contracts. Neither capability has to accept a common repository interface or a shared ORM entity to use it. The code-host adapters serve publication alone.

## Make the benefit observable

The offline demonstration constructs the collaborators in `main.rs`. It passes the same store through the two different storage contracts, then swaps SQLite for memory:

```rust {filename="src/main.rs"}
let sqlite = SqliteStore::open(":memory:")?;
sqlite.replace_plan(&plan)?;
exercise("SQLite", &sqlite, &sqlite, &MemoryPublisher::default()).await?;
let memory = MemoryStore::new(plan);
exercise("Memory", &memory, &memory, &MemoryPublisher::default()).await?;
```

`exercise` calls both application workflows. With either store, publication succeeds, the author's approval is rejected, and another person's approval is recorded. `MemoryPublisher` keeps the demonstration offline; both real code-host adapters implement the same publisher port.

The useful evidence is the work each change avoids:

| Change or failure | Work it requires | Work it avoids |
| --- | --- | --- |
| Add the self-approval rule | Approval policy and its tests | Editing publication rules or GitHub mapping |
| Use GitLab instead of GitHub | Construct a different publisher | Changing the workflow, eligibility rule, or approval slice |
| Use memory instead of SQLite | Construct a different adapter | Changing either workflow or decision |
| Upgrade the GitHub client | Adapter mapping and HTTP-fixture tests | Importing SDK types into either rule |
| GitHub becomes unavailable | Publication reports an uncertain write | Preventing approval from recording |
| Current plan changes during approval | Storage reports `PlanChanged` | Recording approval against an obsolete current artifact |

The [slice tests](https://github.com/lanej/lanej.github.com/blob/a14575118a9eb2bcbe15fe5360e52549882bca4b/examples/plan-review/tests/slices.rs) run the same use cases against both stores. They show an approval succeeding after publication encounters an unavailable GitHub provider, verify that failed plan lookup sends nothing, and preserve storage failures as errors. The provider fixtures drive that same workflow through both real HTTP implementations, checking their different request paths and payloads, successful receipts, definite rejection, and response loss without another POST.

The rules and workflows stay the same when adapters change because they express the application's needs in its own values. Organizing modules around decisions that other modules should not need to know follows Parnas's criterion.[^modularity]

Shared storage remains a shared dependency. A schema change can require updating both SQLite projections, and a storage outage can stop both slices. If a new rule needs another fact, the relevant contract and adapters must supply it. Boundaries make that coordination visible; they cannot remove the dependency.

## Keep the files near the capability

The reference is one crate under `examples/plan-review/`. Read across a capability before following its adapters. The filenames above each excerpt link to complete source files:

| Location under `src/` | What belongs there |
| --- | --- |
| [`publish_review/`](https://github.com/lanej/lanej.github.com/tree/a14575118a9eb2bcbe15fe5360e52549882bca4b/examples/plan-review/src/publish_review) | Publication's rule, workflow, GitHub and GitLab adapters, and optional recovery extension |
| [`approve_plan/`](https://github.com/lanej/lanej.github.com/tree/a14575118a9eb2bcbe15fe5360e52549882bca4b/examples/plan-review/src/approve_plan) | Approval's rule, workflow, values, and storage contract |
| [`sqlite.rs`](https://github.com/lanej/lanej.github.com/blob/a14575118a9eb2bcbe15fe5360e52549882bca4b/examples/plan-review/src/sqlite.rs), [`memory.rs`](https://github.com/lanej/lanej.github.com/blob/a14575118a9eb2bcbe15fe5360e52549882bca4b/examples/plan-review/src/memory.rs) | Adapters implementing both slices' storage contracts |
| [`main.rs`](https://github.com/lanej/lanej.github.com/blob/a14575118a9eb2bcbe15fe5360e52549882bca4b/examples/plan-review/src/main.rs) | Construction and wiring for the offline demonstration |

A new capability gets nearby rules and workflow code. A shared adapter earns its shared location by serving existing consumers. Keep common code tied to an actual shared responsibility; a general `domain/`, `services/`, or `repositories/` directory would spread these two capabilities across the tree.

Composition is ordinary Rust constructing collaborators and passing references. Static dispatch needs no dependency-injection container. The application remains one process; these boundaries organize source and reasoning without promising independent deployment or more throughput.

## Add coordination when the delivery promise requires it

The basic publication workflow makes one attempt. Its contract preserves what the caller knows about the write:

`Published(id)`, `Rejected { reason }`, and `Unknown { reason }` remain distinct. Receipt IDs are scoped to the configured code host and destination.

An authentication rejection and a write whose response was lost permit different next actions. A boolean would erase that distinction. The SDK's default retry middleware is disabled.

The optional GitHub-specific [delivery extension](https://github.com/lanej/lanej.github.com/blob/a14575118a9eb2bcbe15fe5360e52549882bca4b/examples/plan-review/docs/delivery.md) adds a SQLite journal and recovery inside the publication slice. It records an attempt before sending, retains receipts across restart, and reconciles uncertain writes using the publishing account and complete expected body. A marker helps correlate evidence; GitHub does not enforce it as an idempotency key.[^github] Missing evidence never authorizes another create. A crash before sending can therefore leave an unsent attempt unknown indefinitely.

That state machine pays for a stronger delivery requirement. It reuses the publication decision and adds a GitHub-specific read-back contract; approval's rule stays separate. GitLab implements the portable one-attempt publisher without that recovery promise. Tests reopen SQLite and race connections, establishing bounded behavior rather than live GitHub or real disk-failure guarantees.

The host still authenticates users and supplies trusted artifact and principal identities. Recording an approval does not execute infrastructure; applying a plan needs authorization bound to the exact artifact at execution.

For an existing application, begin with one decision that is difficult to test or change. Extract its explicit values, then add an external contract where provider knowledge spreads. Review the result against actual changes: if a boundary adds navigation without containing change or isolating a meaningful failure, simplify it.

[^functional-core]: **[Functional Core, Imperative Shell](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)**\
    Gary Bernhardt · 2012

    Separates functional decisions from code handling interaction with the world. The delivery policy in this reference is a separate application choice.

[^hexagonal]: **[Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)**\
    Alistair Cockburn · 2005

    Describes ports and adapters at the inside/outside boundary. It does not require every internal function to be pure or every dependency to receive an interface.

[^modularity]: **[On the Criteria To Be Used in Decomposing Systems into Modules](https://doi.org/10.1145/361598.361623)**\
    D. L. Parnas · 1972

    Compares decompositions by how changes propagate and how independently modules can be understood. The two-slice example here is my application of that criterion.

[^octorust]: **[octorust](https://docs.rs/octorust/0.10.0/octorust/)**\
    Oxide Computer · Client documentation

    The reference pins this generated client and disables default middleware, which otherwise includes retries. Request construction and pagination stay inside the adapter.

[^github]: **[REST API endpoints for issue comments](https://docs.github.com/en/rest/issues/comments)**\
    GitHub documentation

    Documents creation and listing of issue and pull-request conversation comments. The journal and conservative recovery policy are application choices.

[^gitlab]: **[Merge-request Notes API](https://docs.gitlab.com/api/notes/#create-a-merge-request-note)**\
    GitLab documentation

    Documents the project ID, merge-request IID, authentication, and request body used by the second publisher adapter. Its quick-action behavior is handled inside that adapter; the application port only publishes feedback.
