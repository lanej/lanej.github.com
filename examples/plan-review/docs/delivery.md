# Optional durable review delivery

The basic two-slice example is described in [the README](../README.md).
Run this separate, offline failure demonstration with:

```sh
cargo run --locked --bin recovery
```

## Durable delivery is an extension

`publish_once` makes one attempt and promises no automatic retry or durability.
`src/publish_review/recovery.rs` and the concrete `src/publish_review/journal.rs` add those concerns explicitly:

- The destination is canonicalized once for identity, stored request, and delivery.
  Typed request comparison does not depend on JSON property order.
- Existing receipts are checked before current eligibility. A new current plan
  cannot turn an earlier success into a skip.
- The SQLite unique key reserves one writer before the external call. Every
  worker must share the same durable database.
- `Published(NonZeroU64)`, `Rejected { reason }`, and `Unknown { reason }` preserve
  distinct knowledge. A published outcome cannot contain a missing or zero ID.
- A rejected write retains its cause and permits an explicit `retry_rejected`
  after correcting the problem, subject to current eligibility. It is not an
  automatic retry loop.
- Unknown writes are never resent, including through `retry_rejected`. Only
  read-back evidence can confirm them; missing evidence leaves them unknown.
- A crash after reservation but before sending may leave an unsent write unknown
  indefinitely. Automatic eventual delivery is deliberately not promised.

The journal reads structured request values before comparing them. The marker
binds destination and immutable review identity; changed plan/content requires a
new review identity. Its hash length prefixes use fixed-width integers so keys
are stable across platforms.

The offline demo simulates a provider accepting a comment and losing its response,
repeats the request, reads back evidence, and finishes with one created comment.
Reconciliation checks the entire body and configured publisher account across all
pages. A copied marker by another author is not evidence of our publication.


Applying infrastructure is outside this example. An approval or publication receipt
is not execution authorization. Losing journal records loses duplicate protection.
