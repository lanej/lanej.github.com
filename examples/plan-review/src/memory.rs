use std::{
    collections::{HashMap, HashSet},
    sync::Mutex,
};

use crate::{
    approve_plan::{
        policy::{Approval, Plan},
        workflow::{ApprovalRecords, RecordOutcome},
    },
    publish_review::workflow::CurrentPlan,
};

struct State {
    plan: Plan,
    authors: HashMap<String, String>,
    approvals: HashSet<(String, String)>,
}

pub struct MemoryStore(Mutex<State>);

impl MemoryStore {
    pub fn new(plan: Plan) -> Self {
        Self(Mutex::new(State {
            authors: HashMap::from([(plan.id.clone(), plan.author.clone())]),
            plan,
            approvals: HashSet::new(),
        }))
    }

    pub fn replace_plan(&self, plan: Plan) -> Result<(), String> {
        let mut state = self.0.lock().map_err(|e| e.to_string())?;
        if state
            .authors
            .get(&plan.id)
            .is_some_and(|author| *author != plan.author)
        {
            return Err("an artifact's author is immutable".into());
        }
        state.authors.insert(plan.id.clone(), plan.author.clone());
        state.plan = plan;
        Ok(())
    }

    pub fn approval_count(&self) -> Result<usize, String> {
        Ok(self.0.lock().map_err(|e| e.to_string())?.approvals.len())
    }
}

impl CurrentPlan for MemoryStore {
    fn current_plan_id(&self) -> Result<String, String> {
        Ok(self.0.lock().map_err(|e| e.to_string())?.plan.id.clone())
    }
}

impl ApprovalRecords for MemoryStore {
    fn current_plan(&self) -> Result<Plan, String> {
        Ok(self.0.lock().map_err(|e| e.to_string())?.plan.clone())
    }

    fn record(&self, approval: &Approval) -> Result<RecordOutcome, String> {
        let mut state = self.0.lock().map_err(|e| e.to_string())?;
        if state.plan.id != approval.plan_id {
            return Ok(RecordOutcome::PlanChanged);
        }
        state
            .approvals
            .insert((approval.plan_id.clone(), approval.approver.clone()));
        Ok(RecordOutcome::Recorded)
    }
}
