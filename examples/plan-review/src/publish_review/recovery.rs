//! Optional durable delivery extension; the basic shell is in workflow.rs.
use sha2::{Digest, Sha256};

use super::{
    journal::{Error, PublicationJournal, Request},
    policy::{Decision, Review, decide, format_review},
    workflow::{GitHubComments, GitHubTarget, Outcome, WriteOutcome},
};

pub fn publication_key(target: &GitHubTarget, review_id: &str) -> String {
    let target = target.canonical();
    // Length-prefix strings so delimiters in an identifier cannot alias keys.
    let mut hash = Sha256::new();
    for part in [target.owner.as_str(), target.repo.as_str(), review_id] {
        hash.update((part.len() as u64).to_le_bytes());
        hash.update(part.as_bytes());
    }
    hash.update(target.issue_number.to_le_bytes());
    format!("{:x}", hash.finalize())
}

pub async fn publish(
    current_plan: &str,
    review: &Review,
    target: &GitHubTarget,
    journal: &PublicationJournal,
    github: &impl GitHubComments,
) -> Result<Outcome, Error> {
    run(current_plan, review, target, journal, github, false).await
}

/// A caller explicitly requests another attempt after a definite rejection.
pub async fn retry_rejected(
    current_plan: &str,
    review: &Review,
    target: &GitHubTarget,
    journal: &PublicationJournal,
    github: &impl GitHubComments,
) -> Result<Outcome, Error> {
    run(current_plan, review, target, journal, github, true).await
}

async fn run(
    current_plan: &str,
    review: &Review,
    target: &GitHubTarget,
    journal: &PublicationJournal,
    github: &impl GitHubComments,
    retry_rejected: bool,
) -> Result<Outcome, Error> {
    let key = publication_key(target, &review.id);
    let request = Request {
        target: target.canonical(),
        body: format!(
            "<!-- statecraft-review:{key} -->\n{}",
            format_review(review).body
        ),
    };
    // Existing receipts are historical facts, independent of current eligibility.
    if let Some(entry) = journal.read(&key)? {
        if entry.request != request {
            return Err(Error::IdentityConflict);
        }
        match (&entry.outcome, retry_rejected) {
            (WriteOutcome::Rejected { .. }, true) => {}
            (WriteOutcome::Published(_) | WriteOutcome::Unknown { .. }, _)
            | (WriteOutcome::Rejected { .. }, false) => {
                return Ok(Outcome::Attempted(entry.outcome));
            }
        }
    }
    match decide(current_plan, review) {
        Decision::Skip(reason) => return Ok(Outcome::Skipped(reason)),
        Decision::Publish(_) => {}
    }
    let (acquired, entry) = journal.reserve(&key, &request, retry_rejected)?;
    if !acquired {
        return Ok(Outcome::Attempted(entry.outcome));
    }
    let outcome = github.create(&request.target, &request.body).await;
    journal.record(&key, &outcome)?;
    Ok(Outcome::Attempted(outcome))
}

pub async fn reconcile(
    target: &GitHubTarget,
    review_id: &str,
    journal: &PublicationJournal,
    github: &impl GitHubComments,
) -> Result<WriteOutcome, Error> {
    let key = publication_key(target, review_id);
    let entry = journal.read(&key)?.ok_or(Error::MissingAttempt)?;
    match entry.outcome {
        WriteOutcome::Published(_) | WriteOutcome::Rejected { .. } => Ok(entry.outcome),
        WriteOutcome::Unknown { .. } => {
            match github
                .find(&entry.request.target, &entry.request.body)
                .await
                .map_err(Error::Lookup)?
            {
                Some(comment_id) => {
                    let outcome = WriteOutcome::Published(comment_id);
                    journal.record(&key, &outcome)?;
                    Ok(outcome)
                }
                None => Ok(entry.outcome),
            }
        }
    }
}
