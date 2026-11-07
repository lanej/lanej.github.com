use plan_review::{
    approve_plan::{
        policy::{Plan, Request},
        workflow::{ApprovalRecords, approve},
    },
    memory::MemoryStore,
    publish_review::{
        memory::MemoryPublisher,
        policy::Review,
        workflow::{CurrentPlan, ReviewPublisher, publish_once},
    },
    sqlite::SqliteStore,
};

async fn exercise(
    label: &str,
    plans: &impl CurrentPlan,
    approvals: &impl ApprovalRecords,
    publisher: &impl ReviewPublisher,
) -> Result<(), String> {
    let review = Review {
        id: "review-7".into(),
        plan_id: "plan-a".into(),
        text: "Keep the backup.".into(),
    };
    println!(
        "{label} / publish review: {:?}",
        publish_once(&review, plans, publisher).await?
    );
    for approver in ["sam", "alex"] {
        let request = Request {
            plan_id: "plan-a".into(),
            approver: approver.into(),
        };
        println!(
            "{label} / approve as {approver}: {:?}",
            approve(&request, approvals)?
        );
    }
    Ok(())
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let plan = Plan {
        id: "plan-a".into(),
        author: "sam".into(),
    };
    let sqlite = SqliteStore::open(":memory:")?;
    sqlite.replace_plan(&plan)?;
    exercise("SQLite", &sqlite, &sqlite, &MemoryPublisher::default()).await?;
    let memory = MemoryStore::new(plan);
    exercise("Memory", &memory, &memory, &MemoryPublisher::default()).await?;
    Ok(())
}
