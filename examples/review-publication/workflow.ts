import { createHash } from "node:crypto";
import { decide } from "./policy.ts";
import type { Decision, Review } from "./policy.ts";
import type { PublicationJournal } from "./journal.ts";

export type GitHubTarget = Readonly<{
  owner: string;
  repo: string;
  issue_number: number;
}>;

// This boundary earns its cost by reproducing ambiguous external writes.
// The workflow deliberately knows it publishes a GitHub issue/PR comment.
export interface GitHubComments {
  create(target: GitHubTarget, body: string): Promise<number>;
  find(target: GitHubTarget, body: string): Promise<number | undefined>;
}

type Receipt =
  | { kind: "unknown"; key: string }
  | { kind: "published"; key: string; commentId: number };
type Result = Extract<Decision, { kind: "skip" }> | Receipt;

// A direct utility function needs no injectable hasher interface.
function publicationKey(target: GitHubTarget, reviewId: string): string {
  const identity = [target.owner.toLowerCase(), target.repo.toLowerCase(),
    target.issue_number, reviewId];
  return createHash("sha256").update(JSON.stringify(identity)).digest("hex");
}

function receipt(key: string, entry: ReturnType<PublicationJournal["read"]>): Receipt {
  return entry.state === "published"
    ? { kind: "published", key, commentId: entry.commentId! }
    : { kind: "unknown", key };
}

export async function publishReview(
  currentPlanId: string, review: Review, target: GitHubTarget,
  journal: PublicationJournal, github: GitHubComments,
): Promise<Result> {
  const decision = decide(currentPlanId, review);
  if (decision.kind === "skip") return decision;
  const key = publicationKey(target, decision.reviewId);
  const body = `<!-- statecraft-review:${key} -->\n${decision.body}`;
  const attempt = journal.claim(key, JSON.stringify({ target, body }));
  if (!attempt.fresh) return receipt(key, attempt.entry);

  let commentId: number;
  try {
    commentId = await github.create(target, body);
  } catch {
    // Conservatively unknown for every unconfirmed write, including timeouts.
    // Reconciliation is explicit and read-only; no blind POST retry.
    return { kind: "unknown", key };
  }
  // If this commit fails, propagate the storage error. The prior durable
  // unknown entry still prevents another create after restart.
  journal.confirm(key, commentId);
  return { kind: "published", key, commentId };
}

export async function reconcile(
  key: string, journal: PublicationJournal, github: GitHubComments,
): Promise<Receipt> {
  const entry = journal.read(key);
  if (entry.state === "published") return receipt(key, entry);
  const { target, body } = JSON.parse(entry.payload) as {
    target: GitHubTarget; body: string;
  };
  const commentId = await github.find(target, body);
  // An absent comment is not proof the earlier write can never arrive.
  if (commentId === undefined) return { kind: "unknown", key };
  journal.confirm(key, commentId);
  return { kind: "published", key, commentId };
}
