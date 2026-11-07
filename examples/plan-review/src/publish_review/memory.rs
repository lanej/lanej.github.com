use std::{num::NonZeroU64, sync::Mutex};

use super::workflow::{GitHubComments, GitHubTarget, WriteOutcome};

/// An offline comment adapter. The generated GitHub client implements the same port.
#[derive(Default)]
pub struct MemoryComments(Mutex<Vec<(GitHubTarget, String)>>);

impl MemoryComments {
    pub fn count(&self) -> usize {
        self.0.lock().unwrap().len()
    }
}

impl GitHubComments for MemoryComments {
    async fn create(&self, target: &GitHubTarget, body: &str) -> WriteOutcome {
        let mut comments = self.0.lock().unwrap();
        comments.push((target.canonical(), body.into()));
        WriteOutcome::Published(NonZeroU64::new(comments.len() as u64).unwrap())
    }

    async fn find(&self, target: &GitHubTarget, body: &str) -> Result<Option<NonZeroU64>, String> {
        let comments = self.0.lock().map_err(|e| e.to_string())?;
        let matches: Vec<_> = comments
            .iter()
            .enumerate()
            .filter(|(_, (t, text))| *t == target.canonical() && text == body)
            .map(|(index, _)| NonZeroU64::new(index as u64 + 1).unwrap())
            .collect();
        match matches.as_slice() {
            [] => Ok(None),
            [id] => Ok(Some(*id)),
            _ => Err("multiple matching comments; inspect manually".into()),
        }
    }
}
