#![cfg(feature = "github")]

use octorust::{Client, auth::Credentials};
use plan_review::publish_review::{
    github::GitHub,
    workflow::{GitHubComments, GitHubTarget, WriteOutcome},
};
use std::{
    io::{Read, Write},
    net::TcpListener,
    sync::{
        Arc,
        atomic::{AtomicBool, AtomicUsize, Ordering},
    },
    time::Duration,
};

struct Server {
    base: String,
    requests: Arc<AtomicUsize>,
    stop: Arc<AtomicBool>,
    thread: Option<std::thread::JoinHandle<()>>,
}

impl Server {
    fn new(
        handler: impl Fn(&str, &str, usize) -> Option<(u16, serde_json::Value, Option<String>)>
        + Send
        + 'static,
    ) -> Self {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        listener.set_nonblocking(true).unwrap();
        let base = format!("http://{}", listener.local_addr().unwrap());
        let requests = Arc::new(AtomicUsize::new(0));
        let stop = Arc::new(AtomicBool::new(false));
        let counter = requests.clone();
        let stopping = stop.clone();
        let thread = std::thread::spawn(move || {
            while !stopping.load(Ordering::SeqCst) {
                match listener.accept() {
                    Ok((mut stream, _)) => {
                        stream
                            .set_read_timeout(Some(Duration::from_secs(2)))
                            .unwrap();
                        let mut input = Vec::new();
                        let mut byte = [0u8; 1];
                        while !input.ends_with(b"\r\n\r\n") {
                            if stream.read(&mut byte).unwrap_or(0) == 0 {
                                break;
                            }
                            input.push(byte[0]);
                        }
                        let header = String::from_utf8(input).unwrap();
                        let length = header
                            .lines()
                            .find_map(|line| {
                                let (name, value) = line.split_once(':')?;
                                name.eq_ignore_ascii_case("content-length")
                                    .then(|| value.trim().parse::<usize>().unwrap())
                            })
                            .unwrap_or(0);
                        let mut body = vec![0; length];
                        stream.read_exact(&mut body).unwrap();
                        let count = counter.fetch_add(1, Ordering::SeqCst);
                        if let Some((status, value, link)) =
                            handler(&header, std::str::from_utf8(&body).unwrap(), count)
                        {
                            let body = value.to_string();
                            let link = link
                                .map(|value| format!("Link: {value}\r\n"))
                                .unwrap_or_default();
                            write!(stream, "HTTP/1.1 {status} Test\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n{link}\r\n{body}", body.len()).unwrap();
                        }
                    }
                    Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => {
                        std::thread::sleep(Duration::from_millis(2))
                    }
                    Err(error) => panic!("fixture accept failed: {error}"),
                }
            }
        });
        Self {
            base,
            requests,
            stop,
            thread: Some(thread),
        }
    }
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
impl Drop for Server {
    fn drop(&mut self) {
        self.stop.store(true, Ordering::SeqCst);
        self.thread.take().unwrap().join().unwrap();
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
