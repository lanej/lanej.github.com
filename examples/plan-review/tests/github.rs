#![cfg(feature = "github")]

use octorust::{Client, auth::Credentials};
use plan_review::publish_review::{
    comments::{GitHubComments, GitHubTarget},
    github::{GitHub, GitHubPublisher},
    workflow::WriteOutcome,
};
use std::{sync::atomic::Ordering, time::Duration};

mod support;
use support::Server;

impl Server {
    fn github(&self) -> GitHub {
        let http = reqwest::Client::builder()
            .no_proxy()
            .timeout(Duration::from_secs(2))
            .build()
            .unwrap();
        let mut client = Client::custom(
            "reference-fixture",
            Credentials::Token("fixture-token".into()),
            http,
        );
        client.with_host_override(&self.base);
        GitHub::with_client(client, 123)
    }
}
fn target() -> GitHubTarget {
    GitHubTarget {
        owner: "example".into(),
        repo: "infrastructure".into(),
        issue_number: 42,
    }
}
fn comment(id: i64, author: i64) -> serde_json::Value {
    serde_json::json!({
        "id": id, "body": "expected body", "author_association": "OWNER",
        "node_id": "fixture-comment", "url": "", "html_url": "", "issue_url": "",
        "created_at": "2026-11-05T12:00:00Z", "updated_at": "2026-11-05T12:00:00Z",
        "user": {"id": author, "login": "fixture-user", "node_id": "fixture-user",
            "avatar_url": "", "gravatar_id": "", "url": "", "html_url": "",
            "followers_url": "", "following_url": "", "gists_url": "", "starred_url": "",
            "subscriptions_url": "", "organizations_url": "", "repos_url": "",
            "events_url": "", "received_events_url": "", "type": "User", "site_admin": false}
    })
}

#[tokio::test]
async fn generated_client_maps_a_definite_authentication_rejection() {
    let server = Server::new(|header, body, _| {
        assert!(header.starts_with("POST /repos/example/infrastructure/issues/42/comments "));
        assert_eq!(
            serde_json::from_str::<serde_json::Value>(body).unwrap()["body"],
            "expected body"
        );
        Some((401, serde_json::json!({"message":"Bad credentials"}), None))
    });
    let result = server.github().create(&target(), "expected body").await;
    assert!(matches!(result, WriteOutcome::Rejected { ref reason } if reason.contains("401")));
    assert_eq!(server.requests.load(Ordering::SeqCst), 1);
}

#[tokio::test]
async fn generated_client_does_not_retry_a_response_lost_after_a_write() {
    let server = Server::new(|_, _, _| None);
    let result = server.github().create(&target(), "expected body").await;
    assert!(matches!(result, WriteOutcome::Unknown { ref reason } if !reason.is_empty()));
    assert_eq!(server.requests.load(Ordering::SeqCst), 1);
}

#[tokio::test]
async fn generated_client_paginates_and_checks_author_and_entire_body() {
    let server = Server::new(|header, _, count| {
        assert!(header.starts_with("GET /repos/example/infrastructure/issues/42/comments"));
        if count == 0 {
            let host = header
                .lines()
                .find(|line| line.to_ascii_lowercase().starts_with("host:"))
                .unwrap()
                .split_once(':')
                .unwrap()
                .1
                .trim();
            Some((
                200,
                serde_json::json!([comment(99, 999)]),
                Some(format!(
                    "<http://{host}/repos/example/infrastructure/issues/42/comments?page=2>; rel=\"next\""
                )),
            ))
        } else {
            Some((200, serde_json::json!([comment(101, 123)]), None))
        }
    });
    assert_eq!(
        server
            .github()
            .find(&target(), "expected body")
            .await
            .unwrap()
            .unwrap()
            .get(),
        101
    );
    assert_eq!(server.requests.load(Ordering::SeqCst), 2);
}

#[tokio::test]
async fn multiple_matching_comments_require_inspection() {
    let server = Server::new(|_, _, _| {
        Some((
            200,
            serde_json::json!([comment(101, 123), comment(102, 123)]),
            None,
        ))
    });
    assert!(
        server
            .github()
            .find(&target(), "expected body")
            .await
            .unwrap_err()
            .contains("multiple matching")
    );
}

#[tokio::test]
async fn the_same_publication_workflow_accepts_the_github_adapter() {
    let server = Server::new(|header, body, _| {
        assert!(header.starts_with("POST /repos/example/infrastructure/issues/42/comments "));
        assert_eq!(
            serde_json::from_str::<serde_json::Value>(body).unwrap()["body"],
            "Review of plan `plan-a`:\n\nKeep the backup."
        );
        Some((201, comment(301, 123), None))
    });
    support::assert_publication(&GitHubPublisher::new(server.github(), target())).await;
    assert_eq!(server.requests.load(Ordering::SeqCst), 1);
}
