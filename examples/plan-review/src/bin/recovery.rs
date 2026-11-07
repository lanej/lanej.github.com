use plan_review::publish_review::{
    journal::PublicationJournal,
    policy::Review,
    recovery,
    workflow::{GitHubComments, GitHubTarget, WriteOutcome},
};
use std::{num::NonZeroU64, sync::Mutex};

#[derive(Default)]
struct OfflineGitHub(Mutex<Vec<String>>);

impl GitHubComments for OfflineGitHub {
    async fn create(&self, _target: &GitHubTarget, body: &str) -> WriteOutcome {
        self.0.lock().unwrap().push(body.into());
        WriteOutcome::Unknown {
            reason: "response lost after provider accepted the comment".into(),
        }
    }
    async fn find(&self, _target: &GitHubTarget, body: &str) -> Result<Option<NonZeroU64>, String> {
        Ok(self
            .0
            .lock()
            .unwrap()
            .iter()
            .position(|stored| stored == body)
            .and_then(|index| NonZeroU64::new(index as u64 + 1)))
    }
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let journal = PublicationJournal::open(":memory:")?;
    let github = OfflineGitHub::default();
    let review = Review {
        id: "review-7".into(),
        plan_id: "plan-a".into(),
        text: "Keep the backup.".into(),
    };
    let target = GitHubTarget {
        owner: "example".into(),
        repo: "infrastructure".into(),
        issue_number: 42,
    };
    println!(
        "Response lost: {:?}",
        recovery::publish("plan-a", &review, &target, &journal, &github).await?
    );
    println!(
        "Repeat request: {:?}",
        recovery::publish("plan-a", &review, &target, &journal, &github).await?
    );
    println!(
        "Read back evidence: {:?}",
        recovery::reconcile(&target, &review.id, &journal, &github).await?
    );
    println!("Comments created: {}", github.0.lock().unwrap().len());
    Ok(())
}
