import { PublicationJournal } from "./journal.ts";
import { publishReview, reconcile } from "./workflow.ts";
import type { GitHubComments } from "./workflow.ts";

// Offline demonstration. No credentials or real GitHub writes.
const journal = new PublicationJournal(":memory:");
const comments: string[] = [];
const github: GitHubComments = {
  async create(_target, body) {
    comments.push(body); // The provider accepts the write ...
    throw new Error("Response lost after commit"); // ... but we never hear back.
  },
  async find(_target, body) {
    const index = comments.indexOf(body);
    return index < 0 ? undefined : index + 1;
  },
};
const review = { id: "review-7", planId: "plan-sha256-a", text: "Keep the backup." };
const target = { owner: "example", repo: "infrastructure", issue_number: 42 };
try {
  const first = await publishReview(review.planId, review, target, journal, github);
  console.log("Response lost:", first.kind);
  console.log("Repeat request:",
    (await publishReview(review.planId, review, target, journal, github)).kind);
  if (first.kind === "unknown") {
    console.log("Read back evidence:", (await reconcile(first.key, journal, github)).kind);
  }
  console.log("Comments created:", comments.length);
} finally {
  journal.close();
}
