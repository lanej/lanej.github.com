# Plan review: two slices, small boundaries

A hypothetical Statecraft application with two capabilities:

- **Publish a review:** reject stale or empty feedback, then create a GitHub comment.
- **Approve a plan:** reject stale requests and self approval, then record approval
  for the exact artifact.

This teaching reference is separate from Statecraft's implementation. Each slice
owns its policy, workflow, values, and effect contracts. Neither imports the other.
The core modules use only the standard library; they contain no storage or SDK calls.

```sh
cd examples/plan-review
cargo run --locked
cargo test --locked
cargo test --locked --all-features
cargo fmt --all --check
cargo clippy --locked --all-targets --all-features -- -D warnings
```

The pinned toolchain is in `rust-toolchain.toml`. The demo runs the same two
workflows with SQLite and memory storage. Both publish a review, reject approval
by the author, and record approval by another person. Comments remain in memory;
the demo reads no credentials and makes no live GitHub requests.

## Read across one slice first

| Source | Responsibility |
| --- | --- |
| `src/publish_review/policy.rs` | Review eligibility, formatting, and application-owned values |
| `src/publish_review/workflow.rs` | Load the current artifact, decide, and attempt publication |
| `src/publish_review/github.rs` | Implement the comment contract with generated octorust types |
| `src/approve_plan/policy.rs` | Approval eligibility, independently of publication rules |
| `src/approve_plan/workflow.rs` | Load approval context, decide, and request a record |
| `src/sqlite.rs`, `src/memory.rs` | Implement the two slices' different storage contracts |
| `src/main.rs` | Construct adapters and run the same use cases with each backend |

Then compare the three ports:

| Consuming slice | Port | What crosses it |
| --- | --- | --- |
| Publication | `CurrentPlan` | Only the current artifact ID |
| Publication | `GitHubComments` | A destination, formatted text, and a typed write outcome |
| Approval | `ApprovalRecords` | The artifact and author needed for the rule; a prepared approval and record outcome |

Both storage adapters implement `CurrentPlan` and `ApprovalRecords`. This shares
one external integration without sharing either policy or an ORM entity. The
`GitHub` and `MemoryComments` adapters implement `GitHubComments`. `github` remains
an optional Cargo feature, so the default demo and slice tests compile without
the SDK.

Composition is ordinary Rust passing references. There is no container, registry,
global policy module, or generic repository interface. A second transport can call
the same application functions; this reference does not include a webhook server.

## The changes these boundaries contain

| Change | Where to look | What does not need the change |
| --- | --- | --- |
| Reject self approval | `approve_plan/policy.rs` and its tests | Publication's rule and GitHub mapping |
| Replace SQLite with memory | Construction in `main.rs` | Both workflows and both pure decisions |
| Upgrade the GitHub client | `publish_review/github.rs` and HTTP-fixture tests | Approval, storage, and review eligibility |
| GitHub becomes unavailable | Publication returns an uncertain write | Approval can still record through storage |

`tests/slices.rs` exercises these observable boundaries. It runs the same use cases
with both stores, injects plan-lookup and record failures, and shows approval
succeeding after publication encounters an unavailable provider. The generated
client's HTTP-fixture tests remain in `tests/github.rs`.

Shared storage remains a shared dependency. A SQLite schema change can affect both
implementations, and a storage outage can stop both slices. The boundaries make
that coupling explicit; they do not make all changes or failures independent.

## Keep the guarantees precise

The host authenticates users, supplies trusted principal and artifact identities,
loads the authoritative current plan, and chooses the GitHub destination. An
artifact's author is immutable in this example. One workspace uses one database.
The storage adapters atomically recheck the current artifact when recording an
approval and keep repeated approvals unique. SQL errors remain errors.

Publication uses a current-plan snapshot and makes one attempt. Its outcome keeps
confirmed success, definite rejection, and uncertainty separate. The generated
client's default retry middleware is disabled. An optional [durable delivery
extension](docs/delivery.md) retains the earlier SQLite journal and recovery tests
inside the publication slice, outside the main reading path.

This application records decisions about exact plan artifacts. It does not apply
infrastructure. Execution would need its own authorization bound to the artifact
at execution time. The fixtures establish bounded local behavior, including
restart and concurrency cases; they do not establish live GitHub behavior or
durability under real disk failure.
