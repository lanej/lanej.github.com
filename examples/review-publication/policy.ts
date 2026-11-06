export type Review = Readonly<{
  id: string;
  planId: string;
  text: string;
}>;

export type Decision =
  | { kind: "skip"; reason: "stale-plan" | "empty-review" }
  | { kind: "publish"; reviewId: string; planId: string; body: string };

// currentPlanId identifies an exact plan artifact, not just a commit.
// Authorization and input parsing happen before this function is called.
export function decide(currentPlanId: string, review: Review): Decision {
  if (review.planId !== currentPlanId) {
    return { kind: "skip", reason: "stale-plan" };
  }
  const text = review.text.trim();
  if (!text) return { kind: "skip", reason: "empty-review" };
  return {
    kind: "publish",
    reviewId: review.id,
    planId: review.planId,
    body: `Review of plan \`${review.planId}\`:\n\n${text}`,
  };
}
