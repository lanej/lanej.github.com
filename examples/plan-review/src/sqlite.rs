use rusqlite::{Connection, TransactionBehavior, params};
use std::{path::Path, sync::Mutex};

use crate::{
    approve_plan::{
        policy::{Approval, Plan},
        workflow::{ApprovalRecords, RecordOutcome},
    },
    publish_review::workflow::CurrentPlan,
};

pub struct SqliteStore(Mutex<Connection>);

impl SqliteStore {
    /// One reference workspace per database. Seeding the current plan is explicit.
    pub fn open(path: impl AsRef<Path>) -> Result<Self, String> {
        let conn = Connection::open(path).map_err(|e| e.to_string())?;
        conn.busy_timeout(std::time::Duration::from_secs(5))
            .map_err(|e| e.to_string())?;
        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY, author TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS current_plan (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                plan_id TEXT NOT NULL REFERENCES plans(id)
            );
            CREATE TABLE IF NOT EXISTS approvals (
                plan_id TEXT NOT NULL, approver TEXT NOT NULL,
                PRIMARY KEY (plan_id, approver)
            );",
        )
        .map_err(|e| e.to_string())?;
        Ok(Self(Mutex::new(conn)))
    }

    pub fn replace_plan(&self, plan: &Plan) -> Result<(), String> {
        let mut conn = self.0.lock().map_err(|e| e.to_string())?;
        let tx = conn
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(|e| e.to_string())?;
        tx.execute(
            "INSERT OR IGNORE INTO plans (id, author) VALUES (?1, ?2)",
            params![plan.id, plan.author],
        )
        .map_err(|e| e.to_string())?;
        let author: String = tx
            .query_row("SELECT author FROM plans WHERE id = ?1", [&plan.id], |r| {
                r.get(0)
            })
            .map_err(|e| e.to_string())?;
        if author != plan.author {
            return Err("an artifact's author is immutable".into());
        }
        tx.execute(
            "INSERT INTO current_plan (singleton, plan_id) VALUES (1, ?1)
             ON CONFLICT(singleton) DO UPDATE SET plan_id = excluded.plan_id",
            [&plan.id],
        )
        .map_err(|e| e.to_string())?;
        tx.commit().map_err(|e| e.to_string())
    }

    pub fn approval_count(&self) -> Result<usize, String> {
        let count: i64 = self
            .0
            .lock()
            .map_err(|e| e.to_string())?
            .query_row("SELECT count(*) FROM approvals", [], |r| r.get(0))
            .map_err(|e| e.to_string())?;
        usize::try_from(count).map_err(|e| e.to_string())
    }
}

impl CurrentPlan for SqliteStore {
    fn current_plan_id(&self) -> Result<String, String> {
        self.0
            .lock()
            .map_err(|e| e.to_string())?
            .query_row(
                "SELECT plan_id FROM current_plan WHERE singleton = 1",
                [],
                |r| r.get(0),
            )
            .map_err(|e| e.to_string())
    }
}

impl ApprovalRecords for SqliteStore {
    fn current_plan(&self) -> Result<Plan, String> {
        self.0
            .lock()
            .map_err(|e| e.to_string())?
            .query_row(
                "SELECT p.id, p.author FROM plans p
                 JOIN current_plan c ON c.plan_id = p.id WHERE c.singleton = 1",
                [],
                |r| {
                    Ok(Plan {
                        id: r.get(0)?,
                        author: r.get(1)?,
                    })
                },
            )
            .map_err(|e| e.to_string())
    }

    fn record(&self, approval: &Approval) -> Result<RecordOutcome, String> {
        let mut conn = self.0.lock().map_err(|e| e.to_string())?;
        let tx = conn
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(|e| e.to_string())?;
        let current: String = tx
            .query_row(
                "SELECT plan_id FROM current_plan WHERE singleton = 1",
                [],
                |r| r.get(0),
            )
            .map_err(|e| e.to_string())?;
        if current != approval.plan_id {
            return Ok(RecordOutcome::PlanChanged);
        }
        tx.execute(
            "INSERT OR IGNORE INTO approvals (plan_id, approver) VALUES (?1, ?2)",
            params![approval.plan_id, approval.approver],
        )
        .map_err(|e| e.to_string())?;
        tx.commit().map_err(|e| e.to_string())?;
        Ok(RecordOutcome::Recorded)
    }
}
