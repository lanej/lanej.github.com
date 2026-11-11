use super::policy::{Approval, Decision, Plan, Rejection, Request, decide};

#[derive(Debug, PartialEq, Eq)]
pub enum RecordOutcome {
    Recorded,
    PlanChanged,
}

/// This slice needs the author as well as the artifact ID. The adapter must
/// atomically check the artifact is still current when recording an approval.
pub trait ApprovalRecords {
    fn current_plan(&self) -> Result<Plan, String>;
    fn record(&self, approval: &Approval) -> Result<RecordOutcome, String>;
}

#[derive(Debug, PartialEq, Eq)]
pub enum Outcome {
    Rejected(Rejection),
    Recorded(Approval),
}

pub fn approve(request: &Request, records: &impl ApprovalRecords) -> Result<Outcome, String> {
    let plan = records.current_plan()?;
    match decide(&plan, request) {
        Decision::Reject(reason) => Ok(Outcome::Rejected(reason)),
        Decision::Record(approval) => match records.record(&approval)? {
            RecordOutcome::Recorded => Ok(Outcome::Recorded(approval)),
            RecordOutcome::PlanChanged => Ok(Outcome::Rejected(Rejection::StalePlan)),
        },
    }
}
