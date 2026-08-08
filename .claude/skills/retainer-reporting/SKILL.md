---
name: retainer-reporting
description: Assemble the monthly client performance report that justifies a retainer — leads by source, cost per lead, work shipped, next month's plan — with honest availability gates on every metric (no access = flagged gap, never an invented number). Triggers - "monthly report", "retainer report", "client performance report", "<CLIENT> monthly". NOT for weekly check-in agendas — use weekly-client-checkin.
---

# Retainer Reporting

Monthly proof-of-value report. A retainer renews on demonstrated results, and this
document is where those results either land or visibly don't. For a client with multiple
business lines, default to one combined report with a section per line — confirm with the
founder on first run and record the choice in `decisions/log.md`.

## Iron rule — no fabricated metrics, EVER

A report with honest gaps beats a report with invented numbers. Every figure must trace
to a data pull you actually ran this session. If a source is inaccessible, the report
says so plainly ("Ad-platform reporting comes online once account access transfers —
requested via the access matrix") — never estimate, extrapolate, or reuse last month's
figure as this month's.

## Step 1 — Inputs inventory with availability gates

For each source, VERIFY access by pulling real data before you rely on it. "Connected" or
"credentials exist" is not access — the gate is a real record returned this session. The
client's live access state lives in `clients/<slug>/access/access-matrix.md`
(see access-transfer-tracker).

| Source | What it feeds |
|--------|---------------|
| Analytics (GA4 / Search Console or equivalent) | Traffic, top pages, search queries |
| Search ads platform | Spend, cost per lead |
| Social ads platform | Spend, cost per lead |
| Business-profile insights (Google/maps listing) | Calls, direction requests, profile views |
| Call/lead log | Leads by source — the core metric. Pull from <CRM>, form-platform submissions, call-tracking exports |
| Review counts | Reputation delta — public; count live on the listing and date-stamp it, no API needed |

For every NO-ACCESS row: mark the report section "No access yet — requested via the
access matrix" and list the ask in the report's "What we need from you" block. Do not
silently omit the section — a visible gap creates the urgency that gets access granted.

## Step 2 — Pull data (verified sources only)

- **Leads:** export/read form submissions and <CRM> records for the month. Tag each lead
  with a source (form / phone / listing / ads / referral / unknown). "Unknown" is a valid
  category — report it honestly rather than guessing an attribution.
- **Cost per lead:** only computable when an ad platform is accessible AND spend is
  known. Otherwise state "organic + direct only this month."
- **Reviews:** live count + rating per business line, compared against last month's
  report (read it from `deliverables/reports/`; if none exists, this month sets the
  baseline — say so).
- **Work shipped:** pull from <TASK SYSTEM> completed tasks + git log in the client
  folder. Only list work that is verifiably done — a task marked complete without an
  artifact you can point at doesn't go in.

## Step 3 — Report skeleton (in this order)

1. **Wins this month** — plain language the client's operator understands; lead with
   their outcome ("11 new leads came through the website"), never with tooling.
2. **Leads by source** — table per business line; total + month-over-month delta once a
   prior report exists.
3. **Cost per lead** — only with real spend data; otherwise the honest-gap line.
4. **Reviews & reputation** — counts, rating, notable new reviews. Quote real reviews
   only, verbatim — never compose or "improve" one.
5. **Work shipped this month** — bulleted, dated, deliverable-level.
6. **Next month's plan** — 3–5 items, each tied to a lead-flow or revenue outcome.
7. **What we need from you** — access asks + decisions blocking work.

## Step 4 — Tone

Client-facing rules apply (`.claude/rules/communication-style.md`): "we" never "I", no
emojis, professional but approachable, bold the key numbers. No platform jargon — say
"people who called from your Google listing," not "profile interactions." No pricing or
upsell copy inline — pricing is the founder's conversation, not the report's.

## Step 5 — Output

Single self-contained HTML file (inline CSS, client brand colors from
`clients/<slug>/brand/`), plus a short `summary.md` beside it:

```bash
mkdir -p clients/<slug>/deliverables/reports/$(date +%Y-%m)
```

This is a local deliverable — do NOT deploy it anywhere. If the founder wants a hosted
copy, deploy only with an explicit green-light, via
`netlify deploy --prod --site "<YOUR-SITE-ID>"` (or your host's equivalent).

## Step 6 — Review gate + write-back

1. Render and visually read the HTML before handoff — screenshot it, don't trust the source.
2. Status is **"drafted, awaiting the founder's review"** — never "sent" or implied sent.
   The founder reviews every fact before it reaches the client.
3. Write-back: log an activity note on the client's workspace record (date, type:
   deliverable, summary + report path) and update the matching <TASK SYSTEM> task.

## Hard gate — regulated topics

If the report (or next month's plan) mentions or implies a regulated topic for a client
with a compliance ruleset — promotional financing language, health claims, legal-outcome
claims — run regulated-copy-compliance before delivery. Internal metric lines ("2 leads
asked about financing") are fine; promotional language is not.
