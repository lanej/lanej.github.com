+++
title = "Pragmatic Hexagonal Architecture"
description = "A small reference architecture: pure decisions, explicit effects, a thin internal model, and boundaries that justify their cost."
date = "2026-11-05T12:00:00-08:00"
draft = false
unlisted = true
essay_visual = "architecture"
+++

Consider a reviewer leaving feedback on an infrastructure plan. We want to publish that feedback as a GitHub comment, preserving which exact plan it concerns.

The happy path is short: check the plan, format the feedback, call GitHub. Then a request times out. GitHub may have created the comment. Publishing again may create a duplicate. Meanwhile, a newer plan may have appeared.

That small workflow contains enough architecture to be useful. It has a consequential rule, an external dependency, persistent state, and an outcome we cannot always determine immediately.

> Keep decisions easy to challenge, effects explicit, and each boundary accountable for the complexity it adds.

I call this **pragmatic hexagonal architecture**: functional core, imperative shell, a thin internal model, and selective ports and adapters. The name describes a combination of existing ideas and my choices about where to stop applying them.

The [runnable reference](https://github.com/lanej/lanej.github.com/tree/master/examples/review-publication) uses a hypothetical slice of Statecraft's infrastructure-review workflow. It is a teaching example, separate from Statecraft's implementation. There is one capability, four implementation modules, and an offline demonstration. TypeScript makes the data shapes visible; the boundaries apply just as well in Ruby or Go.

## Give the rule a home

A review identifies an immutable plan artifact. A commit alone is insufficient: two plans produced from the same commit may differ.

The rule is small: skip feedback for a different plan, skip empty feedback, otherwise produce a publication decision whose body names the reviewed artifact.

```text
function decide(currentPlanId: string, review: Review): Decision {
  if (review.planId !== currentPlanId) {
    return { kind: "skip", reason: "stale-plan" };
  }
  const text = review.text.trim();
  if (!text) return { kind: "skip", reason: "empty-review" };
  return {
    kind: "publish",
    reviewId: review.id,
    planId: review.planId,
    body: `Review of plan \`${review.planId}\`:\n\n${text}`,
  };
}
```

This function receives values and returns a value. It performs no I/O and changes nothing outside itself. Given the same inputs, it produces the same decision. If a rule needs the time, pass the relevant timestamp in; reading the clock is an effect too.

Gary Bernhardt's *Functional Core, Imperative Shell* describes this separation between functional decisions and imperative interaction with the world.[^functional-core] Here, the result carries both the intended action and its explanation. A stale-plan test needs two plan identifiers and a review, with no server, database, or mocks.

The property belongs to the software: its rule can be evaluated independently. A development instruction to “write unit tests” would not establish that boundary.

## Keep the internal model thin

The application owns `Review`, `Decision`, and the identity of a plan artifact. GitHub owns its API response shape. SQLite owns its storage representation.

The GitHub adapter extracts the returned comment ID and handles pagination when looking for evidence of an earlier publication. The core never receives an Octokit response or a database row. An upstream controller would validate and authorize input before constructing a `Review`.

That is the thin internal model: the concepts our rules need, with their meanings preserved. It does not require a universal `Message` that pretends GitHub comments, chat threads, and email have interchangeable behavior.

| Code | Responsibility | Reason for the boundary |
| --- | --- | --- |
| `policy.ts` | Decide from owned values | Test and change the rule independently |
| `workflow.ts` | Sequence the operation | Keep effect order and uncertain outcomes visible |
| `journal.ts` | Reserve and record publication attempts | Preserve memory across restart and competing workers |
| `github.ts` | Integrate through official Octokit | Contain provider types and behavior |

The workflow is allowed to know it publishes a GitHub issue or pull-request conversation comment. Keeping that fact explicit makes the code easier to follow. The rule deciding which plan the review concerns has no reason to know the GitHub API.

Hexagonal architecture provides the broader inside/outside boundary. Alistair Cockburn's account emphasizes running an application independently of its external devices through ports and adapters.[^hexagonal] A pure core is a further choice: an interface to a database does not make a database call pure.

{{< review-boundaries >}}

## Make the shell tell the truth

The shell calls the rule, reserves a publication attempt, calls GitHub, then records a confirmed comment ID. Its order matters.

Before the external call, the SQLite journal commits an `unknown` record under a unique publication key. The key binds the destination and immutable review identity. Reusing that identity with changed content or a different plan is rejected.

Only the worker that reserves the key may create the comment. A repeated request reads the existing outcome. This requires workers to share the same durable journal.

| Observation | Recorded outcome | Next action |
| --- | --- | --- |
| Policy rejects the review | Skip, with reason | No publication attempt |
| GitHub returns a comment ID and the journal records it | Published | Return the known receipt |
| The write is unconfirmed, or the process crashes after reservation | Unknown | Reconcile through reads |
| Reconciliation finds the exact body from the configured publishing account | Published | Record the observed comment ID |
| Reconciliation finds nothing | Unknown | Keep the uncertainty visible |

A lost response cannot establish whether the write happened. GitHub's comment API supplies create and list operations; this example does not assume a provider-enforced idempotency key.[^github] A marker in the body helps correlate evidence, but the adapter also checks the publishing account and entire expected body. Another user's copied marker is insufficient.

There is a deliberate cost. A crash after reservation but before sending can leave an unsent comment unknown. The reference gives up automatic eventual delivery to avoid issuing a second create through this workflow. Absence from a read does not authorize another write. An operator resolution policy would be additional work.

Purity does not solve this problem. Explicit sequencing, durable memory, and an honest outcome model address it. A generic `Publisher` returning only `true` or `false` would hide the distinction the operator needs most.

## Add the interface that earns its cost

The workflow defines one small contract:

```text
interface GitHubComments {
  create(target: GitHubTarget, body: string): Promise<number>;
  find(target: GitHubTarget, body: string): Promise<number | undefined>;
}
```

This boundary lets us reproduce a provider accepting a comment while the response disappears. The real adapter uses the official Octokit SDK. We keep its HTTP client, authentication machinery, response types, and pagination support.[^octokit]

The direction of the dependency matters: the adapter implements a contract owned by the workflow consuming it. At runtime, the workflow calls the adapter. The pure policy depends on neither.

The SQLite journal stays concrete. So does the function deriving a publication key. Neither gets an interface merely for symmetry. A later storage migration or a demonstrated testing need could justify another boundary; an imagined second backend does not require one today.

Composition is ordinary code constructing the journal and GitHub adapter and passing them to the workflow. There is no dependency-injection container. The files live together under `review-publication`, so reading the capability does not require visiting application-wide directories for every architectural layer.

## Challenge the promises, then stop

The reference's tests attack different claims at the boundary where they could fail.

Pure tests reject stale and empty feedback and check the plan identity in the result. Workflow tests reopen the SQLite database after known and unknown writes, exercise competing connections, and verify that a repeat request does not create another comment. Adapter tests run the actual SDK against simulated HTTP responses, including pagination and a copied marker from the wrong author.

Those checks establish bounded properties. They do not establish live GitHub behavior, authentication correctness, or durability under a real disk failure. The host still needs input validation, authorization, credentials, diagnostics, and database operations.

The supplied current-plan value is also a snapshot. A newer plan can appear after the decision. This capability publishes feedback labeled with the reviewed artifact; it does not authorize an infrastructure apply. Applying a plan would require binding authorization to the exact artifact at execution.

For an existing Rails application, the first useful change might be extracting one decision from an ActiveRecord callback into a function over explicit values. Keep loading and saving in the caller. Add an integration module when SDK details start spreading. Add durable outcome handling when a side effect requires it.

Each choice should answer a concrete change or failure. A new publication rule changes the policy. A GitHub response change reaches the adapter. A timeout remains an inspectable outcome. A small utility remains a function.

That is enough architecture for this example.

[^functional-core]: **[Functional Core, Imperative Shell](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)**\
    Gary Bernhardt · 2012

    Describes a functional core surrounded by imperative code that handles input, output, database, and network interaction. The publication journal and conservative recovery policy here are choices made for this example.

[^hexagonal]: **[Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)**\
    Alistair Cockburn · 2005

    Explains the inside/outside boundary, ports and adapters, and running the application independently of external devices. It does not require every internal function to be pure or every dependency to receive an interface.

[^github]: **[REST API endpoints for issue comments](https://docs.github.com/en/rest/issues/comments)**\
    GitHub documentation

    Documents creation and listing of issue and pull-request conversation comments. Inline pull-request review comments use a different API. The recovery policy in this example is our application choice, not a delivery guarantee supplied by this documentation.

[^octokit]: **[Octokit REST.js](https://github.com/octokit/rest.js)**\
    Octokit documentation

    The official REST SDK supplies endpoint methods and pagination. The reference pins its dependency and checks a single create attempt under simulated response loss; adding retry middleware would change that behavior.
