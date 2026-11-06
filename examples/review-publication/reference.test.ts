import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { Octokit } from "@octokit/rest";
import { decide } from "./policy.ts";
import { PublicationJournal } from "./journal.ts";
import { githubComments } from "./github.ts";
import { publishReview, reconcile } from "./workflow.ts";
import type { GitHubComments } from "./workflow.ts";

const target = { owner: "example", repo: "infrastructure", issue_number: 42 };
const review = { id: "review-7", planId: "plan-a", text: "  Keep the backup.  " };

test("policy refuses stale or empty feedback and preserves the exact artifact", () => {
  assert.deepEqual(decide("plan-b", review), { kind: "skip", reason: "stale-plan" });
  assert.deepEqual(decide("plan-a", { ...review, text: " \n " }),
    { kind: "skip", reason: "empty-review" });
  assert.deepEqual(decide("plan-a", Object.freeze(review)), {
    kind: "publish", reviewId: "review-7", planId: "plan-a",
    body: "Review of plan `plan-a`:\n\nKeep the backup.",
  });
});

test("a rejected decision makes no external call or journal entry", async () => {
  const journal = new PublicationJournal(":memory:");
  const unexpected = async () => { throw new Error("Unexpected external call"); };
  try {
    assert.deepEqual(await publishReview("plan-b", review, target, journal,
      { create: unexpected, find: unexpected }), { kind: "skip", reason: "stale-plan" });
  } finally { journal.close(); }
});

test("known success survives restart and never publishes twice", async () => {
  const dir = mkdtempSync(join(tmpdir(), "review-reference-"));
  const path = join(dir, "journal.sqlite");
  let creates = 0;
  const github: GitHubComments = {
    async create() { creates++; return 101; },
    async find() { throw new Error("Known success needs no lookup"); },
  };
  let journal = new PublicationJournal(path);
  try {
    const first = await publishReview("plan-a", review, target, journal, github);
    assert.equal(first.kind, "published");
    journal.close();
    journal = new PublicationJournal(path);
    assert.deepEqual(await publishReview("plan-a", review, target, journal, github), first);
    assert.equal(creates, 1);
  } finally { journal.close(); rmSync(dir, { recursive: true }); }
});

test("two journal connections reserve only one write", async () => {
  const dir = mkdtempSync(join(tmpdir(), "review-reference-"));
  const journals = [new PublicationJournal(join(dir, "journal.sqlite")),
    new PublicationJournal(join(dir, "journal.sqlite"))];
  let creates = 0;
  const github: GitHubComments = {
    async create() { creates++; await Promise.resolve(); return 101; },
    async find() { return undefined; },
  };
  try {
    await Promise.all(journals.map(journal =>
      publishReview("plan-a", review, target, journal, github)));
    assert.equal(creates, 1);
  } finally {
    journals.forEach(journal => journal.close());
    rmSync(dir, { recursive: true });
  }
});

test("timeout stays unknown after restart, then read-only evidence confirms it", async () => {
  const dir = mkdtempSync(join(tmpdir(), "review-reference-"));
  const path = join(dir, "journal.sqlite");
  const bodies: string[] = [];
  const github: GitHubComments = {
    async create(_target, body) { bodies.push(body); throw new Error("Response lost"); },
    async find(_target, body) { return bodies.includes(body) ? 101 : undefined; },
  };
  let journal = new PublicationJournal(path);
  try {
    const first = await publishReview("plan-a", review, target, journal, github);
    assert.equal(first.kind, "unknown");
    if (first.kind !== "unknown") throw new Error("Expected uncertain write");
    journal.close();
    journal = new PublicationJournal(path);
    assert.deepEqual(await publishReview("plan-a", review, target, journal, github), first);
    assert.deepEqual(await reconcile(first.key, journal, github),
      { kind: "published", key: first.key, commentId: 101 });
    assert.equal(bodies.length, 1);
  } finally { journal.close(); rmSync(dir, { recursive: true }); }
});

test("absence and failed lookup never authorize another write", async () => {
  const journal = new PublicationJournal(":memory:");
  let creates = 0;
  const github: GitHubComments = {
    async create() { creates++; throw new Error("Timed out before or after commit"); },
    async find() { return undefined; },
  };
  try {
    const first = await publishReview("plan-a", review, target, journal, github);
    if (first.kind !== "unknown") throw new Error("Expected uncertain write");
    assert.deepEqual(await reconcile(first.key, journal, github), first);
    github.find = async () => { throw new Error("GitHub unavailable"); };
    await assert.rejects(reconcile(first.key, journal, github), /unavailable/);
    assert.deepEqual(await publishReview("plan-a", review, target, journal, github), first);
    assert.equal(creates, 1);
  } finally { journal.close(); }
});

test("reusing an immutable review identity with new text is rejected", async () => {
  const journal = new PublicationJournal(":memory:");
  const github: GitHubComments = {
    async create() { return 101; }, async find() { return undefined; },
  };
  try {
    await publishReview("plan-a", review, target, journal, github);
    await assert.rejects(publishReview("plan-a", { ...review, text: "Changed" },
      target, journal, github), /identity reused/);
  } finally { journal.close(); }
});

test("crash before sending sacrifices delivery rather than risk a second write", async () => {
  const journal = new PublicationJournal(":memory:");
  try {
    journal.claim("reserved", JSON.stringify({ target, body: "Unsent request" }));
    assert.deepEqual(await reconcile("reserved", journal, {
      async create() { throw new Error("Reconciliation must not send"); },
      async find() { return undefined; },
    }), { kind: "unknown", key: "reserved" });
  } finally { journal.close(); }
});

test("the real SDK maps the request, does not retry POST, and paginates evidence", async () => {
  let writes = 0;
  let reads = 0;
  let publishedBody = "";
  const fakeFetch: typeof fetch = async (input, init) => {
    const url = new URL(typeof input === "string" ? input :
      input instanceof URL ? input.href : input.url);
    assert.equal(url.pathname, "/repos/example/infrastructure/issues/42/comments");
    if (init?.method === "POST") {
      writes++;
      publishedBody = JSON.parse(String(init.body)).body;
      throw new TypeError("Response lost after provider commit");
    }
    reads++;
    const page2 = url.searchParams.get("page") === "2";
    // A matching marker copied by another author is not our publication.
    const data = [{ id: page2 ? 101 : 99, body: publishedBody,
      user: { id: page2 ? 123 : 999 } }];
    const headers: Record<string, string> = { "content-type": "application/json" };
    if (!page2) headers.link = `<${url.href}&page=2>; rel="next"`;
    return new Response(JSON.stringify(data), { status: 200, headers });
  };
  const client = new Octokit({ baseUrl: "https://api.example.test",
    request: { fetch: fakeFetch }, log: { debug() {}, info() {}, warn() {}, error() {} } });
  const github = githubComments(client, 123);
  const journal = new PublicationJournal(":memory:");
  try {
    const first = await publishReview("plan-a", review, target, journal, github);
    if (first.kind !== "unknown") throw new Error("Expected uncertain write");
    assert.deepEqual(await reconcile(first.key, journal, github),
      { kind: "published", key: first.key, commentId: 101 });
    assert.equal(writes, 1);
    assert.equal(reads, 2);
  } finally { journal.close(); }
});
