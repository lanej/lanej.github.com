import type { Octokit } from "@octokit/rest";
import type { GitHubComments } from "./workflow.ts";

// Octokit owns HTTP, authentication, response types, and pagination.
// botUserId is the authenticated publisher's GitHub user ID.
export function githubComments(client: Octokit, botUserId: number): GitHubComments {
  return {
    async create(target, body) {
      const { data } = await client.rest.issues.createComment({ ...target, body });
      if (!Number.isSafeInteger(data.id) || data.id <= 0) {
        throw new Error("GitHub response did not confirm a comment ID");
      }
      return data.id;
    },
    async find(target, body) {
      const comments = await client.paginate(client.rest.issues.listComments, {
        ...target, per_page: 100,
      });
      const matches = comments.filter(comment =>
        comment.user?.id === botUserId && comment.body === body);
      if (matches.length > 1) throw new Error("Multiple matching comments; inspect manually");
      return matches[0]?.id;
    },
  };
}
