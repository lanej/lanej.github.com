import { DatabaseSync } from "node:sqlite";

type Entry = {
  payload: string;
  state: "unknown" | "published";
  commentId: number | null;
};

// A concrete journal, not a generic repository abstraction.
export class PublicationJournal {
  private db: DatabaseSync;

  constructor(path: string) {
    this.db = new DatabaseSync(path);
    this.db.exec(`
      PRAGMA busy_timeout = 5000;
      PRAGMA synchronous = FULL;
      CREATE TABLE IF NOT EXISTS publications (
        key TEXT PRIMARY KEY,
        payload TEXT NOT NULL,
        state TEXT NOT NULL CHECK (state IN ('unknown', 'published')),
        commentId INTEGER,
        CHECK ((state = 'published') = (commentId IS NOT NULL))
      );
    `);
  }

  claim(key: string, payload: string): { fresh: boolean; entry: Entry } {
    // Commit uncertainty BEFORE sending. A crash can leave an unsent attempt
    // unknown; it cannot leave a sent attempt eligible for another create.
    const result = this.db.prepare(
      "INSERT OR IGNORE INTO publications VALUES (?, ?, 'unknown', NULL)",
    ).run(key, payload);
    const entry = this.read(key);
    if (entry.payload !== payload) {
      throw new Error("Review identity reused with different content or plan");
    }
    return { fresh: Number(result.changes) === 1, entry };
  }

  read(key: string): Entry {
    const row = this.db.prepare(
      "SELECT payload, state, commentId FROM publications WHERE key = ?",
    ).get(key) as Entry | undefined;
    if (!row) throw new Error("Unknown publication key");
    return row;
  }

  confirm(key: string, commentId: number): void {
    this.db.prepare(
      "UPDATE publications SET state = 'published', commentId = ? WHERE key = ?",
    ).run(commentId, key);
  }

  close(): void { this.db.close(); }
}
