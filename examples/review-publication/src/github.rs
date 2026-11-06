//! Adapter over octorust, generated from GitHub's OpenAPI description.
use crate::workflow::{GitHubComments, GitHubTarget, WriteOutcome};
use octorust::{Client, ClientError, auth::Credentials, types::PullsUpdateReviewRequest};
use std::{num::NonZeroU64, time::Duration};

pub struct GitHub {
    client: Client,
    publisher_user_id: i64,
}

impl GitHub {
    pub fn new(token: String, publisher_user_id: i64) -> Result<Self, reqwest::Error> {
        let http = reqwest::Client::builder()
            .timeout(Duration::from_secs(10))
            .redirect(reqwest::redirect::Policy::none())
            .build()?;
        Ok(Self {
            client: Client::custom(
                "review-publication-reference",
                Credentials::Token(token),
                http,
            ),
            publisher_user_id,
        })
    }

    pub fn with_client(client: Client, publisher_user_id: i64) -> Self {
        Self {
            client,
            publisher_user_id,
        }
    }
}

fn comment_id(id: i64) -> Option<NonZeroU64> {
    u64::try_from(id).ok().and_then(NonZeroU64::new)
}

impl GitHubComments for GitHub {
    async fn create(&self, target: &GitHubTarget, body: &str) -> WriteOutcome {
        match self
            .client
            .issues()
            .create_comment(
                &target.owner,
                &target.repo,
                target.issue_number,
                &PullsUpdateReviewRequest { body: body.into() },
            )
            .await
        {
            Ok(response) => match comment_id(response.body.id) {
                Some(id) => WriteOutcome::Published(id),
                None => WriteOutcome::Unknown {
                    reason: "response has no valid comment ID".into(),
                },
            },
            Err(error) => {
                let rejected = match &error {
                    ClientError::HttpError { status, .. } => {
                        matches!(status.as_u16(), 400 | 401 | 403 | 404 | 410 | 422 | 429)
                    }
                    ClientError::RateLimited { .. } => true,
                    ClientError::JsonWebTokenError(_)
                    | ClientError::UrlParserError(_)
                    | ClientError::SerdeJsonError(_)
                    | ClientError::ReqwestError(_)
                    | ClientError::InvalidHeaderValue(_) => false,
                };
                let reason = error.to_string();
                if rejected {
                    WriteOutcome::Rejected { reason }
                } else {
                    WriteOutcome::Unknown { reason }
                }
            }
        }
    }

    async fn find(&self, target: &GitHubTarget, body: &str) -> Result<Option<NonZeroU64>, String> {
        let response = self
            .client
            .issues()
            .list_all_comments(&target.owner, &target.repo, target.issue_number, None)
            .await
            .map_err(|e| e.to_string())?;
        let matches: Vec<_> = response
            .body
            .into_iter()
            .filter(|comment| {
                comment
                    .user
                    .as_ref()
                    .is_some_and(|user| user.id == self.publisher_user_id)
                    && comment.body == body
            })
            .collect();
        match matches.as_slice() {
            [] => Ok(None),
            [comment] => comment_id(comment.id)
                .map(Some)
                .ok_or_else(|| "matching comment has an invalid ID".into()),
            _ => Err("multiple matching comments; inspect manually".into()),
        }
    }
}
