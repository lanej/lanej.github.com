#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Plan {
    pub id: String,
    pub author: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Request {
    pub plan_id: String,
    pub approver: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Approval {
    pub plan_id: String,
    pub approver: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Rejection {
    StalePlan,
    SelfApproval,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Decision {
    Reject(Rejection),
    Record(Approval),
}

pub fn decide(plan: &Plan, request: &Request) -> Decision {
    if request.plan_id != plan.id {
        return Decision::Reject(Rejection::StalePlan);
    }
    if request.approver == plan.author {
        return Decision::Reject(Rejection::SelfApproval);
    }
    Decision::Record(Approval {
        plan_id: request.plan_id.clone(),
        approver: request.approver.clone(),
    })
}
