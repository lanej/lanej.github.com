#![cfg(feature = "gitlab")]

mod support;
use plan_review::publish_review::{
    gitlab::GitLabPublisher,
    policy::Publication,
    workflow::{ReviewPublisher, WriteOutcome},
};
use std::{sync::atomic::Ordering, time::Duration};
use support::Server;

impl Server {
    fn gitlab(&self) -> GitLabPublisher {
        let client = reqwest::Client::builder()
            .no_proxy()
            .timeout(Duration::from_secs(2))
            .redirect(reqwest::redirect::Policy::none())
            .build()
            .unwrap();
        GitLabPublisher::with_client(
            client,
            &format!("{}/api/v4", self.base),
            "fixture-token".into(),
            7,
            13,
        )
    }
}

fn publication() -> Publication {
    Publication {
        review_id: "review-7".into(),
        plan_id: "plan-a".into(),
        body: "Review of plan `plan-a`:\n\nKeep the backup.".into(),
    }
}

#[tokio::test]
async fn the_same_publication_workflow_accepts_the_gitlab_adapter() {
    let server = Server::new(|header, body, _| {
        assert!(header.starts_with("POST /api/v4/projects/7/merge_requests/13/notes "));
        assert!(
            header
                .to_ascii_lowercase()
                .contains("private-token: fixture-token")
        );
        assert_eq!(
            serde_json::from_str::<serde_json::Value>(body).unwrap()["body"],
            "Review of plan `plan-a`:\n\nKeep the backup."
        );
        Some((201, serde_json::json!({"id":17}), None))
    });
    support::assert_publication(&server.gitlab()).await;
    assert_eq!(server.requests.load(Ordering::SeqCst), 1);
}

#[tokio::test]
async fn a_definite_rejection_is_distinct_from_server_uncertainty() {
    for status in [401, 422, 500] {
        let server = Server::new(move |_, _, _| {
            Some((
                status,
                serde_json::json!({"message":"fixture failure"}),
                None,
            ))
        });
        let outcome = server.gitlab().publish(&publication()).await;
        if status < 500 {
            assert!(matches!(outcome, WriteOutcome::Rejected { .. }));
        } else {
            assert!(matches!(outcome, WriteOutcome::Unknown { .. }));
        }
        assert_eq!(server.requests.load(Ordering::SeqCst), 1);
    }
}

#[tokio::test]
async fn a_lost_response_is_unknown_and_does_not_trigger_another_post() {
    let server = Server::new(|_, _, _| None);
    assert!(matches!(
        server.gitlab().publish(&publication()).await,
        WriteOutcome::Unknown { .. }
    ));
    assert_eq!(server.requests.load(Ordering::SeqCst), 1);
}

#[tokio::test]
async fn successful_http_without_a_valid_receipt_stays_unknown() {
    for value in [
        serde_json::json!({}),
        serde_json::json!({"id":0}),
        serde_json::json!({"id":-1}),
    ] {
        let server = Server::new(move |_, _, _| Some((201, value.clone(), None)));
        assert!(matches!(
            server.gitlab().publish(&publication()).await,
            WriteOutcome::Unknown { .. }
        ));
    }
}

#[tokio::test]
async fn feedback_never_becomes_a_gitlab_quick_action() {
    let server = Server::new(|_, _, _| panic!("quick action must not be sent"));
    let mut review = publication();
    review.body.push_str("\n/merge");
    assert!(matches!(
        server.gitlab().publish(&review).await,
        WriteOutcome::Rejected { .. }
    ));
    assert_eq!(server.requests.load(Ordering::SeqCst), 0);
}
