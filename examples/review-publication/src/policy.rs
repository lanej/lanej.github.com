#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Review {
    pub id: String,
    pub plan_id: String,
    pub text: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Publication {
    pub review_id: String,
    pub plan_id: String,
    pub body: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SkipReason {
    StalePlan,
    EmptyReview,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Decision {
    Skip(SkipReason),
    Publish(Publication),
}

// An artifact ID identifies an exact plan, not merely its source commit.
pub fn decide(current_plan: &str, review: &Review) -> Decision {
    if review.plan_id != current_plan {
        return Decision::Skip(SkipReason::StalePlan);
    }
    if review.text.trim().is_empty() {
        return Decision::Skip(SkipReason::EmptyReview);
    }
    Decision::Publish(format_review(review))
}

// Stable formatting is also used to validate a repeated publication request.
pub fn format_review(review: &Review) -> Publication {
    Publication {
        review_id: review.id.clone(),
        plan_id: review.plan_id.clone(),
        body: format!(
            "Review of plan `{}`:\n\n{}",
            review.plan_id,
            review.text.trim()
        ),
    }
}
