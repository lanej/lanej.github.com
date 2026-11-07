//! GitLab merge-request notes over the existing reqwest dependency.
use super::{
    policy::Publication,
    workflow::{ReviewPublisher, WriteOutcome},
};
use serde::Deserialize;
use std::{num::NonZeroU64, time::Duration};

pub struct GitLabPublisher {
    client: reqwest::Client,
    api_base: String,
    token: String,
    project_id: u64,
    merge_request_iid: u64,
}

#[derive(Deserialize)]
struct Note {
    id: i64,
}

impl GitLabPublisher {
    pub fn new(
        token: String,
        project_id: u64,
        merge_request_iid: u64,
    ) -> Result<Self, reqwest::Error> {
        let client = reqwest::Client::builder()
            .timeout(Duration::from_secs(10))
            .redirect(reqwest::redirect::Policy::none())
            .build()?;
        Ok(Self::with_client(
            client,
            "https://gitlab.com/api/v4",
            token,
            project_id,
            merge_request_iid,
        ))
    }

    /// Inject a client and API root for self-hosted GitLab or a local HTTP fixture.
    pub fn with_client(
        client: reqwest::Client,
        api_base: &str,
        token: String,
        project_id: u64,
        merge_request_iid: u64,
    ) -> Self {
        Self {
            client,
            api_base: api_base.trim_end_matches('/').into(),
            token,
            project_id,
            merge_request_iid,
        }
    }
}

impl GitLabPublisher {
    async fn create_note(&self, body: &str) -> WriteOutcome {
        // GitLab notes can execute quick actions. This port only publishes feedback.
        if body.lines().any(|line| line.trim_start().starts_with('/')) {
            return WriteOutcome::Rejected {
                reason: "GitLab quick-action lines are unsupported in review feedback".into(),
            };
        }
        let url = format!(
            "{}/projects/{}/merge_requests/{}/notes",
            self.api_base, self.project_id, self.merge_request_iid
        );
        let response = self
            .client
            .post(url)
            .header("PRIVATE-TOKEN", &self.token)
            .json(&serde_json::json!({"body": body}))
            .send()
            .await;
        let response = match response {
            Ok(response) => response,
            Err(error) => {
                return if error.is_builder() {
                    WriteOutcome::Rejected {
                        reason: error.to_string(),
                    }
                } else {
                    WriteOutcome::Unknown {
                        reason: error.to_string(),
                    }
                };
            }
        };
        let status = response.status();
        if !status.is_success() {
            let reason = format!("GitLab HTTP {}", status.as_u16());
            return if matches!(
                status.as_u16(),
                400 | 401 | 403 | 404 | 405 | 410 | 422 | 429
            ) {
                WriteOutcome::Rejected { reason }
            } else {
                WriteOutcome::Unknown { reason }
            };
        }
        match response.json::<Note>().await {
            Ok(note) => match u64::try_from(note.id).ok().and_then(NonZeroU64::new) {
                Some(id) => WriteOutcome::Published(id),
                None => WriteOutcome::Unknown {
                    reason: "GitLab returned no valid note ID".into(),
                },
            },
            Err(error) => WriteOutcome::Unknown {
                reason: error.to_string(),
            },
        }
    }
}

impl ReviewPublisher for GitLabPublisher {
    async fn publish(&self, publication: &Publication) -> WriteOutcome {
        self.create_note(&publication.body).await
    }
}
