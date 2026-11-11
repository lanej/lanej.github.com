use std::{future::Future, num::NonZeroU64};

use serde::{Deserialize, Serialize};

use super::policy::{Decision, Publication, Review, SkipReason, decide};

/// Publication needs only an artifact ID, not the approval slice's Plan type.
pub trait CurrentPlan {
    fn current_plan_id(&self) -> Result<String, String>;
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum WriteOutcome {
    Published(NonZeroU64),
    Rejected { reason: String },
    Unknown { reason: String },
}

#[derive(Debug, PartialEq, Eq)]
pub enum Outcome {
    Skipped(SkipReason),
    Attempted(WriteOutcome),
}

/// Publish review feedback to the code-review destination configured in the adapter.
pub trait ReviewPublisher: Sync {
    fn publish(&self, publication: &Publication) -> impl Future<Output = WriteOutcome> + Send;
}

/// One attempt, with no automatic retry or durability promise.
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
