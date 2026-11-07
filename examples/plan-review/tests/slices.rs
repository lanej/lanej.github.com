use plan_review::{
    approve_plan::{
        policy::{Approval, Decision, Plan, Rejection, Request, decide},
        workflow::{self as approval, ApprovalRecords, RecordOutcome},
    },
    memory::MemoryStore,
    publish_review::{
        memory::MemoryPublisher,
        policy::{Publication, Review, SkipReason},
        workflow::{self as publication, CurrentPlan, ReviewPublisher, WriteOutcome},
    },
    sqlite::SqliteStore,
};
use std::num::NonZeroU64;

fn plan() -> Plan {
    Plan {
        id: "plan-a".into(),
        author: "sam".into(),
    }
}

fn request(approver: &str) -> Request {
    Request {
        plan_id: "plan-a".into(),
        approver: approver.into(),
    }
}

fn review() -> Review {
    Review {
        id: "review-7".into(),
        plan_id: "plan-a".into(),
        text: "Keep the backup.".into(),
    }
}

#[test]
fn approval_rule_uses_ordinary_values_and_has_its_own_rejections() {
    assert_eq!(
        decide(&plan(), &request("sam")),
        Decision::Reject(Rejection::SelfApproval)
    );
    assert_eq!(
        decide(&plan(), &request("alex")),
        Decision::Record(Approval {
            plan_id: "plan-a".into(),
            approver: "alex".into(),
        })
    );
    let mut stale = request("alex");
    stale.plan_id = "plan-previous".into();
    assert_eq!(
        decide(&plan(), &stale),
        Decision::Reject(Rejection::StalePlan)
    );
}

async fn exercise_both_slices(store: &(impl CurrentPlan + ApprovalRecords)) {
    let comments = MemoryPublisher::default();
    let mut stale = review();
    stale.plan_id = "plan-previous".into();
    assert_eq!(
        publication::publish_once(&stale, store, &comments)
            .await
            .unwrap(),
        publication::Outcome::Skipped(SkipReason::StalePlan)
    );
    assert_eq!(comments.count(), 0);
    assert_eq!(
        publication::publish_once(&review(), store, &comments)
            .await
            .unwrap(),
        publication::Outcome::Attempted(WriteOutcome::Published(NonZeroU64::new(1).unwrap()))
    );
    assert_eq!(
        approval::approve(&request("sam"), store).unwrap(),
        approval::Outcome::Rejected(Rejection::SelfApproval)
    );
    let expected = approval::Outcome::Recorded(Approval {
        plan_id: "plan-a".into(),
        approver: "alex".into(),
    });
    assert_eq!(
        approval::approve(&request("alex"), store).unwrap(),
        expected
    );
    assert_eq!(
        approval::approve(&request("alex"), store).unwrap(),
        expected
    );
    assert_eq!(comments.count(), 1);
}

#[tokio::test]
async fn the_same_workflows_run_with_memory_and_sqlite_without_an_sdk() {
    let memory = MemoryStore::new(plan());
    exercise_both_slices(&memory).await;
    assert_eq!(memory.approval_count().unwrap(), 1);
    let sqlite = SqliteStore::open(":memory:").unwrap();
    sqlite.replace_plan(&plan()).unwrap();
    exercise_both_slices(&sqlite).await;
    assert_eq!(sqlite.approval_count().unwrap(), 1);
}

struct UnavailablePublisher;

impl ReviewPublisher for UnavailablePublisher {
    async fn publish(&self, _publication: &Publication) -> WriteOutcome {
        WriteOutcome::Unknown {
            reason: "provider unavailable".into(),
        }
    }
}

#[tokio::test]
async fn a_publication_provider_failure_does_not_prevent_an_approval() {
    let sqlite = SqliteStore::open(":memory:").unwrap();
    sqlite.replace_plan(&plan()).unwrap();
    assert!(matches!(
        publication::publish_once(&review(), &sqlite, &UnavailablePublisher)
            .await
            .unwrap(),
        publication::Outcome::Attempted(WriteOutcome::Unknown { .. })
    ));
    assert!(matches!(
        approval::approve(&request("alex"), &sqlite).unwrap(),
        approval::Outcome::Recorded(_)
    ));
    assert_eq!(sqlite.approval_count().unwrap(), 1);
}

struct UnavailablePlans;

impl CurrentPlan for UnavailablePlans {
    fn current_plan_id(&self) -> Result<String, String> {
        Err("plan lookup unavailable".into())
    }
}

#[tokio::test]
async fn a_plan_lookup_failure_does_not_send_a_comment() {
    let comments = MemoryPublisher::default();
    assert_eq!(
        publication::publish_once(&review(), &UnavailablePlans, &comments).await,
        Err("plan lookup unavailable".into())
    );
    assert_eq!(comments.count(), 0);
}

struct FailingRecord;

impl ApprovalRecords for FailingRecord {
    fn current_plan(&self) -> Result<Plan, String> {
        Ok(plan())
    }
    fn record(&self, _approval: &Approval) -> Result<RecordOutcome, String> {
        Err("disk full".into())
    }
}

#[test]
fn rejecting_an_approval_needs_no_write_and_storage_errors_remain_errors() {
    assert_eq!(
        approval::approve(&request("sam"), &FailingRecord).unwrap(),
        approval::Outcome::Rejected(Rejection::SelfApproval)
    );
    assert_eq!(
        approval::approve(&request("alex"), &FailingRecord),
        Err("disk full".into())
    );
}

struct ChangedBeforeRecord;

impl ApprovalRecords for ChangedBeforeRecord {
    fn current_plan(&self) -> Result<Plan, String> {
        Ok(plan())
    }
    fn record(&self, _approval: &Approval) -> Result<RecordOutcome, String> {
        Ok(RecordOutcome::PlanChanged)
    }
}

#[test]
fn the_workflow_preserves_a_plan_change_reported_at_the_write_boundary() {
    assert_eq!(
        approval::approve(&request("alex"), &ChangedBeforeRecord).unwrap(),
        approval::Outcome::Rejected(Rejection::StalePlan)
    );
}

#[test]
fn both_storage_adapters_reject_an_approval_after_the_current_plan_changes() {
    let approved = Approval {
        plan_id: "plan-a".into(),
        approver: "alex".into(),
    };
    let next = Plan {
        id: "plan-b".into(),
        author: "alex".into(),
    };
    let memory = MemoryStore::new(plan());
    memory.replace_plan(next.clone()).unwrap();
    assert_eq!(
        memory.record(&approved).unwrap(),
        RecordOutcome::PlanChanged
    );
    assert_eq!(memory.approval_count().unwrap(), 0);

    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("plans.sqlite");
    let first = SqliteStore::open(&path).unwrap();
    first.replace_plan(&plan()).unwrap();
    let second = SqliteStore::open(&path).unwrap();
    second.replace_plan(&next).unwrap();
    assert_eq!(first.record(&approved).unwrap(), RecordOutcome::PlanChanged);
    assert_eq!(first.approval_count().unwrap(), 0);
}

#[test]
fn sqlite_receipts_survive_reopening_and_cannot_change_an_artifacts_author() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("plans.sqlite");
    let store = SqliteStore::open(&path).unwrap();
    store.replace_plan(&plan()).unwrap();
    approval::approve(&request("alex"), &store).unwrap();
    drop(store);
    let store = SqliteStore::open(&path).unwrap();
    assert_eq!(store.current_plan_id().unwrap(), "plan-a");
    assert_eq!(store.approval_count().unwrap(), 1);
    let changed_author = Plan {
        id: "plan-a".into(),
        author: "alex".into(),
    };
    assert!(store.replace_plan(&changed_author).is_err());
    assert_eq!(ApprovalRecords::current_plan(&store).unwrap(), plan());
}
