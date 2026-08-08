---
name: daily-brief
description: Start and end every work session with a structured brief and summary. Use when the operator opens a new session, says "good morning", "what should I work on", "daily review", "wrap up", "end of day", "session summary", or seems unsure what to focus on. Also use on Fridays or on "weekly review". Reads context files, checks records and the task system, and keeps the session on the north star from context/current-priorities.md.
---

# Daily Brief

Structure every session: priorities at the start, progress captured at the end.

## When to use
- A new session starts, or the operator asks anything like "what should I do?"
- "wrap up", "done for today", "end of day"
- "weekly review", or it's Friday

---

## Session Start

### 1. Read context files (in this order)
1. `context/current-priorities.md` — the north star; wins any conflict
2. Other `context/*.md` files that exist (goals, business details)
3. `decisions/log.md` — last 5 entries

### 2. Check records + task system
- Read active client and venture records (`clients/*/_index.md`, `ventures/*/`)
- Check <TASK SYSTEM> for tasks due today, replies waiting, proposals outstanding
- Records are durable context; <TASK SYSTEM> is live execution state

### 3. Present the brief

```
Morning brief — [Date]
======================

REVENUE ACTIONS (do first):
  1. [Highest-leverage revenue task]
  2. [Second]

CLIENT WORK DUE:
  • <CLIENT>: [deliverable] — due [date]

PIPELINE:
  • [X] follow-ups due today
  • [X] proposals outstanding
  • [X] replies waiting

BUILD QUEUE (after revenue work):
  • [Next system/skill from current-priorities.md]

NORTH STAR:
  [Quote the #1 priority verbatim from context/current-priorities.md.
   Never hardcode numbers here — the files are the source of truth.]
  Gap: [what's blocking it / what closes it fastest]
```

### 4. Confirm
"Does this look right, or do you want to shift focus?" If the operator overrides the priority, support it — but note what's being deferred so nothing falls through.

---

## Session End

On "wrap up", "done", "end of day":

### 1. Generate the session summary
Use `_templates/session-summary.md` as the structure. Cover:

- **Completed** — what actually shipped (verified, not just attempted)
- **In Progress** — what's left to finish
- **Decisions Made** — each one appended to `decisions/log.md`
- **Blockers** — what's stuck, and on whom
- **Next Session Priority** — top 1-2 tasks to open with
- **Learned Rules Added** — any new rules, or "None"

### 2. Update files
- Append decisions to `decisions/log.md`: `[YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...`
- Route corrections per the routing doctrine (hook / script / skill edit / short rule — never blind-append)
- Update `context/current-priorities.md` if priorities shifted

### 3. Save the summary
```bash
mkdir -p archives/sessions
```
Save to `archives/sessions/[YYYY-MM-DD]-session.md`.

---

## Weekly Review (Fridays or on request)

### 1. Read the week's session summaries
```bash
ls archives/sessions/
```
Read each file from this week.

### 2. Generate the review

```markdown
# Weekly Review — Week of [Date]

## Revenue
- Deals closed / payments collected / proposals sent / calls held / new leads
  (pull real numbers from records — never estimate)

## Client Work
- [What was delivered this week]

## Build Progress
- [Skills or systems built or refined]

## What Worked
- [Keep doing]

## What Didn't
- [Stop or change]

## Next Week Focus
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]
```

Also run the productization hook: "What did you build this week that isn't in the product journal?" — log candidates via the productization-journal skill.

### 3. Save
```bash
mkdir -p archives/reviews
```
Save to `archives/reviews/[YYYY]-W[XX]-review.md`.

---

## Priority Logic

Rank brief items with this hierarchy — `context/current-priorities.md` always wins on conflict:
1. **Flagship client deliverables** — the signed top-tier account beats everything
2. **Billing / AR** — invoices due, payments to collect, billing risk
3. **Pipeline** — hot replies, proposals outstanding, follow-ups due
4. **Outreach** — only if the lane is active in current-priorities.md
5. **Build skills/systems** — important, never at the expense of revenue
6. **Admin/setup** — lowest, unless it blocks something above
