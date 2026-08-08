# Decision Log

One line per significant decision, newest at the bottom. Format:

```
[YYYY-MM-DD] DECISION: what was decided | REASONING: why | CONTEXT: what prompted it
```

**Conventions:**
- **Append-only.** Never edit or delete past entries — history is the point.
- **Reversals don't rewrite history.** When a decision is overturned, append a new entry and
  add `(Superseded by YYYY-MM-DD entry)` to the end of the old line — nothing else changes.
- Log decisions that shape money, tooling, priorities, or client commitments. Skip trivia.

---

[2026-01-15] DECISION: Adopt <TASK SYSTEM> as the execution layer for all tasks and pipeline stages | REASONING: The workspace is great long-term memory but has no due dates, reminders, or mobile surface; a dedicated task system owns "what's next" while files own "what's true" | CONTEXT: Follow-ups were slipping because they lived only in markdown notes nobody re-opened
