use rusqlite::{Connection, OptionalExtension, params};
use serde::{Deserialize, Serialize};
use std::{path::Path, time::Duration};
use thiserror::Error;

use super::workflow::{GitHubTarget, WriteOutcome};

#[derive(Debug, Error)]
pub enum Error {
    #[error(transparent)]
    Storage(#[from] rusqlite::Error),
    #[error(transparent)]
    Codec(#[from] serde_json::Error),
    #[error("review identity reused with different content or plan")]
    IdentityConflict,
    #[error("no publication attempt exists")]
    MissingAttempt,
    #[error("GitHub evidence lookup failed: {0}")]
    Lookup(String),
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Request {
    pub target: GitHubTarget,
    pub body: String,
}

#[derive(Debug)]
pub struct Entry {
    pub request: Request,
    pub outcome: WriteOutcome,
}

pub struct PublicationJournal(Connection);

impl PublicationJournal {
    pub fn open(path: impl AsRef<Path>) -> Result<Self, Error> {
        let db = Connection::open(path)?;
        db.busy_timeout(Duration::from_secs(5))?;
        db.execute_batch(
            "PRAGMA synchronous=FULL;
            CREATE TABLE IF NOT EXISTS publications (
                key TEXT PRIMARY KEY, request TEXT NOT NULL,
                outcome TEXT NOT NULL, rejected INTEGER NOT NULL DEFAULT 0
            );",
        )?;
        Ok(Self(db))
    }

    pub fn read(&self, key: &str) -> Result<Option<Entry>, Error> {
        let row: Option<(String, String)> = self
            .0
            .query_row(
                "SELECT request, outcome FROM publications WHERE key=?1",
                [key],
                |row| Ok((row.get(0)?, row.get(1)?)),
            )
            .optional()?;
        row.map(|(request, outcome)| {
            Ok(Entry {
                request: serde_json::from_str(&request)?,
                outcome: serde_json::from_str(&outcome)?,
            })
        })
        .transpose()
    }

    // Reserve before sending; a crash may leave an unsent request unknown.
    pub fn reserve(
        &self,
        key: &str,
        request: &Request,
        retry_rejected: bool,
    ) -> Result<(bool, Entry), Error> {
        let encoded = serde_json::to_string(request)?;
        let unknown = serde_json::to_string(&WriteOutcome::Unknown {
            reason: "attempt reserved; write not yet confirmed".into(),
        })?;
        let mut acquired = self.0.execute(
            "INSERT OR IGNORE INTO publications(key,request,outcome) VALUES (?1,?2,?3)",
            params![key, encoded, unknown],
        )? == 1;
        let entry = self.read(key)?.ok_or(Error::MissingAttempt)?;
        if entry.request != *request {
            return Err(Error::IdentityConflict);
        }
        if !acquired && retry_rejected {
            acquired = self.0.execute(
                "UPDATE publications SET outcome=?2,rejected=0 WHERE key=?1 AND rejected=1",
                params![key, unknown],
            )? == 1;
        }
        Ok((acquired, self.read(key)?.ok_or(Error::MissingAttempt)?))
    }

    pub fn record(&self, key: &str, outcome: &WriteOutcome) -> Result<(), Error> {
        let rejected = matches!(outcome, WriteOutcome::Rejected { .. });
        let changed = self.0.execute(
            "UPDATE publications SET outcome=?2,rejected=?3 WHERE key=?1",
            params![key, serde_json::to_string(outcome)?, rejected],
        )?;
        if changed != 1 {
            return Err(Error::MissingAttempt);
        }
        Ok(())
    }
}
