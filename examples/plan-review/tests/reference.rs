use plan_review::publish_review::{
    journal::{Error, PublicationJournal, Request},
    policy::{Decision, Review, SkipReason, decide},
    recovery,
    workflow::{GitHubComments, GitHubTarget, Outcome, WriteOutcome, publish_once},
};
use plan_review::{approve_plan::policy::Plan, memory::MemoryStore};
use std::{
    num::NonZeroU64,
    sync::{Arc, Barrier, Mutex},
};

fn plans(id: &str) -> MemoryStore {
    MemoryStore::new(Plan {
        id: id.into(),
        author: "sam".into(),
    })
}

fn review() -> Review {
    Review {
        id: "review-7".into(),
        plan_id: "plan-a".into(),
        text: "  Keep the backup.  ".into(),
    }
}
fn target() -> GitHubTarget {
    GitHubTarget {
        owner: "example".into(),
        repo: "infrastructure".into(),
        issue_number: 42,
    }
}
fn published() -> WriteOutcome {
    WriteOutcome::Published(NonZeroU64::new(101).unwrap())
}

struct FakeGitHub {
    outcome: Mutex<WriteOutcome>,
    comments: Mutex<Vec<String>>,
    writes: Mutex<usize>,
}
impl FakeGitHub {
    fn new(outcome: WriteOutcome) -> Self {
        Self {
            outcome: Mutex::new(outcome),
            comments: Mutex::new(vec![]),
            writes: Mutex::new(0),
        }
    }
}
impl GitHubComments for FakeGitHub {
    async fn create(&self, _target: &GitHubTarget, body: &str) -> WriteOutcome {
        *self.writes.lock().unwrap() += 1;
        let outcome = self.outcome.lock().unwrap().clone();
        match outcome {
            WriteOutcome::Published(_) | WriteOutcome::Unknown { .. } => {
                self.comments.lock().unwrap().push(body.into());
            }
            WriteOutcome::Rejected { .. } => {}
        }
        outcome
    }
    async fn find(&self, _target: &GitHubTarget, body: &str) -> Result<Option<NonZeroU64>, String> {
        Ok(self
            .comments
            .lock()
            .unwrap()
            .iter()
            .any(|s| s == body)
            .then(|| NonZeroU64::new(101).unwrap()))
    }
}

#[test]
fn pure_rule_rejects_stale_and_empty_reviews_and_names_the_artifact() {
    assert_eq!(
        decide("plan-b", &review()),
        Decision::Skip(SkipReason::StalePlan)
    );
    let mut empty = review();
    empty.text = " \n ".into();
    assert_eq!(
        decide("plan-a", &empty),
        Decision::Skip(SkipReason::EmptyReview)
    );
    match decide("plan-a", &review()) {
        Decision::Publish(publication) => {
            assert_eq!(
                publication.body,
                "Review of plan `plan-a`:\n\nKeep the backup."
            );
            assert_eq!(publication.plan_id, "plan-a");
        }
        Decision::Skip(reason) => panic!("unexpected rejection: {reason:?}"),
    }
}

#[tokio::test]
async fn basic_shell_skips_without_publishing_and_returns_a_typed_write_outcome() {
    let github = FakeGitHub::new(published());
    assert_eq!(
        publish_once(&review(), &target(), &plans("plan-b"), &github)
            .await
            .unwrap(),
        Outcome::Skipped(SkipReason::StalePlan)
    );
    assert_eq!(*github.writes.lock().unwrap(), 0);
    assert_eq!(
        publish_once(&review(), &target(), &plans("plan-a"), &github)
            .await
            .unwrap(),
        Outcome::Attempted(published())
    );
    assert_eq!(*github.writes.lock().unwrap(), 1);
}

#[tokio::test]
async fn receipt_survives_restart_and_a_new_current_plan() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("journal.sqlite");
    let github = FakeGitHub::new(published());
    let journal = PublicationJournal::open(&path).unwrap();
    let first = recovery::publish("plan-a", &review(), &target(), &journal, &github)
        .await
        .unwrap();
    drop(journal);
    let journal = PublicationJournal::open(&path).unwrap();
    assert_eq!(
        recovery::publish("plan-b", &review(), &target(), &journal, &github)
            .await
            .unwrap(),
        first
    );
    assert_eq!(*github.writes.lock().unwrap(), 1);
}

#[tokio::test]
async fn equivalent_destinations_reuse_the_same_receipt() {
    let journal = PublicationJournal::open(":memory:").unwrap();
    let github = FakeGitHub::new(published());
    let first = recovery::publish("plan-a", &review(), &target(), &journal, &github)
        .await
        .unwrap();
    let same = GitHubTarget {
        issue_number: 42,
        repo: "Infrastructure".into(),
        owner: "EXAMPLE".into(),
    };
    assert_eq!(
        recovery::publish("plan-a", &review(), &same, &journal, &github)
            .await
            .unwrap(),
        first
    );
    assert_eq!(*github.writes.lock().unwrap(), 1);
}

#[tokio::test]
async fn uncertainty_and_its_cause_survive_restart_and_can_be_reconciled() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("journal.sqlite");
    let github = FakeGitHub::new(WriteOutcome::Unknown {
        reason: "response lost after commit".into(),
    });
    let journal = PublicationJournal::open(&path).unwrap();
    let first = recovery::publish("plan-a", &review(), &target(), &journal, &github)
        .await
        .unwrap();
    drop(journal);
    let journal = PublicationJournal::open(&path).unwrap();
    assert_eq!(
        recovery::publish("plan-b", &review(), &target(), &journal, &github)
            .await
            .unwrap(),
        first
    );
    assert_eq!(
        recovery::reconcile(&target(), &review().id, &journal, &github)
            .await
            .unwrap(),
        published()
    );
    assert_eq!(*github.writes.lock().unwrap(), 1);
}

#[tokio::test]
async fn known_rejection_preserves_its_reason_and_allows_an_explicit_retry() {
    let journal = PublicationJournal::open(":memory:").unwrap();
    let rejected = WriteOutcome::Rejected {
        reason: "HTTP 401: bad credentials".into(),
    };
    let github = FakeGitHub::new(rejected.clone());
    assert_eq!(
        recovery::publish("plan-a", &review(), &target(), &journal, &github)
            .await
            .unwrap(),
        Outcome::Attempted(rejected)
    );
    *github.outcome.lock().unwrap() = published();
    let retried = recovery::retry_rejected("plan-a", &review(), &target(), &journal, &github)
        .await
        .unwrap();
    assert_eq!(retried, Outcome::Attempted(published()));
    assert_eq!(*github.writes.lock().unwrap(), 2);
}

#[tokio::test]
async fn explicit_retry_never_resends_an_unknown_write() {
    let journal = PublicationJournal::open(":memory:").unwrap();
    let github = FakeGitHub::new(WriteOutcome::Unknown {
        reason: "response lost".into(),
    });
    let first = recovery::publish("plan-a", &review(), &target(), &journal, &github)
        .await
        .unwrap();
    assert_eq!(
        recovery::retry_rejected("plan-a", &review(), &target(), &journal, &github)
            .await
            .unwrap(),
        first
    );
    assert_eq!(*github.writes.lock().unwrap(), 1);
}

#[tokio::test]
async fn changed_content_cannot_reuse_an_existing_review_identity() {
    let journal = PublicationJournal::open(":memory:").unwrap();
    let github = FakeGitHub::new(published());
    recovery::publish("plan-a", &review(), &target(), &journal, &github)
        .await
        .unwrap();
    let mut changed = review();
    changed.text = "Remove the backup.".into();
    assert!(matches!(
        recovery::publish("plan-a", &changed, &target(), &journal, &github).await,
        Err(Error::IdentityConflict)
    ));
}

#[test]
fn competing_connections_only_reserve_one_write() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("journal.sqlite");
    drop(PublicationJournal::open(&path).unwrap());
    let barrier = Arc::new(Barrier::new(2));
    let handles: Vec<_> = (0..2)
        .map(|_| {
            let path = path.clone();
            let barrier = barrier.clone();
            std::thread::spawn(move || {
                let journal = PublicationJournal::open(path).unwrap();
                barrier.wait();
                journal
                    .reserve(
                        "same-key",
                        &Request {
                            target: target(),
                            body: "same body".into(),
                        },
                        false,
                    )
                    .unwrap()
                    .0
            })
        })
        .collect();
    assert_eq!(
        handles
            .into_iter()
            .map(|handle| usize::from(handle.join().unwrap()))
            .sum::<usize>(),
        1
    );
}

#[tokio::test]
async fn crash_before_sending_and_absent_evidence_stay_unknown() {
    let journal = PublicationJournal::open(":memory:").unwrap();
    let key = recovery::publication_key(&target(), &review().id);
    journal
        .reserve(
            &key,
            &Request {
                target: target(),
                body: "unsent".into(),
            },
            false,
        )
        .unwrap();
    let github = FakeGitHub::new(published());
    assert!(matches!(
        recovery::reconcile(&target(), &review().id, &journal, &github)
            .await
            .unwrap(),
        WriteOutcome::Unknown { .. }
    ));
    assert_eq!(*github.writes.lock().unwrap(), 0);
}
