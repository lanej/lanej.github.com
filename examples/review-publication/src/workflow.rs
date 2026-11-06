use std::{future::Future, num::NonZeroU64};

use serde::{Deserialize, Serialize};

use crate::policy::{Decision, Review, SkipReason, decide};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct GitHubTarget {
    pub owner: String,
    pub repo: String,
    pub issue_number: i64,
}

impl GitHubTarget {
    pub fn canonical(&self) -> Self {
        Self {
            owner: self.owner.to_ascii_lowercase(),
            repo: self.repo.to_ascii_lowercase(),
            issue_number: self.issue_number,
        }
    }
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

// The consuming workflow owns this contract. Static dispatch needs no container.
pub trait GitHubComments: Sync {
    fn create(
        &self,
        target: &GitHubTarget,
        body: &str,
    ) -> impl Future<Output = WriteOutcome> + Send;
    fn find(
        &self,
        target: &GitHubTarget,
        body: &str,
    ) -> impl Future<Output = Result<Option<NonZeroU64>, String>> + Send;
}

/// One attempt, with no automatic retry or durability promise.
pub async fn publish_once(
    current_plan: &str,
    review: &Review,
    target: &GitHubTarget,
    github: &impl GitHubComments,
) -> Outcome {
    match decide(current_plan, review) {
        Decision::Skip(reason) => Outcome::Skipped(reason),
        Decision::Publish(publication) => {
            Outcome::Attempted(github.create(target, &publication.body).await)
        }
    }
}
