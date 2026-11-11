//! GitHub-specific read-back contract used by the optional recovery extension.
use super::workflow::WriteOutcome;
use serde::{Deserialize, Serialize};
use std::{future::Future, num::NonZeroU64};

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
