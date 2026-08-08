---
name: weekly-client-checkin
description: Prep the packet for a recurring 30-min client check-in call — what shipped this week, in-progress/blocked and on whom, decisions needed, next week's plan, contract-promises check, one-page agenda saved to the client folder. Triggers - "check-in prep", "weekly client call", "client call agenda", "prep for the <CLIENT> call". NOT for sales-call prospect research — use discovery-call-prep.
---

# Weekly Client Check-in Prep

Builds the one-page agenda for a recurring client check-in call — especially when the
cadence is a contract promise, where a missed or unprepared call is a breach, not just a
bad look. Takes a `[client]` parameter; each wired client gets a facts block like the one
below so every run starts from the same ground truth instead of re-deriving it.

## Per-client wiring block (create once, then reuse)

Add a table like this to the top of the client's strategy folder (or inline here for your
primary client) before the first run:

| Thing | Where |
|---|---|
| Account brief (read FIRST, every run) | `clients/<slug>/strategy/account-brief.md` or equivalent |
| Kickoff plan / scope doc | `clients/<slug>/strategy/kickoff-brief.md` |
| Open blockers / access state | `clients/<slug>/access/access-matrix.md` (see access-transfer-tracker) |
| Deliverable folders | `clients/<slug>/deliverables/` |
| <TASK SYSTEM> board(s) | board name/ID per business line |
| Live/preview URLs | list them |
| Contract facts | signing date, phase structure, what "done" means for the current phase, promised cadence and SLAs |

## Step 1 — What shipped this week

Gather from every source; only claim things you can point at — no fabricated progress:

```bash
git log --since="7 days ago" --oneline -- "clients/<slug>/"
ls clients/<slug>/deliverables/   # anything new or updated this week
```

Then pull completed tasks from <TASK SYSTEM> for the period. If your task tool has no
completed-date filter, pull the board twice (open-only, then including completed) and
diff — rows only in the completed run finished at some point; confirm recency against the
git log before claiming "this week."

## Step 2 — In progress / blocked, and on whom

Read the account brief and access matrix, then bucket every open item by owner:

- **The client** — inputs owed: content, photos, decisions, account access, approvals.
- **Third parties** — previous agency transfers, platform verifications, vendor holds.
- **Us** — anything not blocked that we simply haven't advanced. Call it out honestly;
  hiding our own slippage in the "blocked" bucket destroys trust the first time it's noticed.

Every blocked item gets one line: item → blocker → what unblocks it.

## Step 3 — Decisions needed from the client this week

Pull from open decision-tagged tasks, the account brief's pending-questions list, and any
`_drafts/` awaiting client sign-off. **Max 3–5**, each phrased as a yes/no or A/B question
answerable on the call. A decision the client can't resolve in 60 seconds is an agenda
item for a separate working session, not this list.

## Step 4 — Next week's plan

3–6 concrete items pulled from the current phase's priority order in the kickoff plan.
If work is gated on missing access or client inputs, plan from the non-gated list — never
present a plan whose items depend on things you don't have.

## Step 5 — Contract promises check (one line each, every packet)

- **Edit SLA:** any client-requested edit older than the promised turnaround still
  unresolved? (grep activity notes + open tasks). State PASS or name the breach plainly.
- **Check-in cadence:** date of the last check-in; flag if the promised interval slipped.
- **Milestone posture:** where the engagement stands vs. the committed timeline, and the
  single item most gating the next payment or phase start.

## Step 6 — Write the agenda

One page max. Save to `clients/<slug>/check-ins/YYYY-MM-DD-checkin-agenda.md`
(`mkdir -p` the folder on first run). Sections in order:

1. **Shipped this week** (with live/preview URLs where relevant)
2. **In progress / blocked** (owner-bucketed)
3. **Decisions needed from you**
4. **Next week**
5. **Promises check**

Voice: plain and direct, matched to how the client actually talks — no agency-speak. This
is the founder's call script, not a client deliverable, but write it clean enough to
screen-share.

**Hard gates:** if any agenda line touches a regulated topic for a client with a
compliance ruleset (financing, health, legal, insurance), open the ruleset before writing
that line — see regulated-copy-compliance. Never fabricate status, metrics, or
completions; "couldn't verify" is a valid line in the packet.

## Step 7 — Write-back (non-negotiable)

1. Log the prep as an activity note on the client's workspace record (date, type,
   summary, link to the agenda file).
2. Attach the agenda path to the relevant check-in task in <TASK SYSTEM> — create the
   task if none exists.
3. After the call happens, remind the founder to log a second activity capturing the
   client's answers to the Step 3 decisions — undocumented decisions get re-litigated.
