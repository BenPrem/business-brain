---
name: cold-email-campaign
description: Batch cold-email pipeline — load new-lead records from the workspace CRM, generate personalized first-touch emails, export a CSV ready for <YOUR OUTREACH TOOL>. Trigger on "batch", "campaign", "run the campaign tool", or first-touch emails for 5+ leads at once. All writing rules live in cold-email. NOT for leads already contacted or in-pipeline (use follow-up-nurture) or a single hand-written email (use cold-email).
---

# Cold Email Campaign Builder

Batch workflow only: pull leads → generate copy at scale → export a CSV for
<YOUR OUTREACH TOOL>. **All writing rules, tone, structure, and subject-line craft live
in the `cold-email` skill** — this skill is the assembly line, not the copywriter.

The batch script is `tools/cold_email.py`. It reads lead records, calls your LLM router
with a system prompt encoding the cold-email rules, and writes the export CSV. Everything
below also works manually (agent-generated, one lead at a time) if you haven't wired the
script's API key yet.

## Where leads come from

`tools/cold_email.py` reads deal records from your workspace pipeline folder with
`stage: new` (accepts "New Lead" as an alias). Each record needs frontmatter `name`,
`industry`, `location`, `website`, and a `Pain points: ...` line in the notes or body —
these are what personalization is built from; a record without pain points produces a
generic email, which defeats the point. lead-scraper creates these records; verify they
exist on disk before running a campaign — a scored list that never got written is not a pipeline.

## What NOT to include in Touch 1

- No percentages or statistics you can't verify — never invent data
- No "we helped X company increase Y by Z%" — case-study proof belongs in Touch 2
- No differentiator / "what sets us apart" pitch — that belongs in Touch 3
- No asking for a 30-minute call on first touch — the CTA is a small yes

## Target length

**Under 75 words.** Hard cap — it wins over any other number found anywhere.

## Batch workflow

### Step 1 — Confirm parameters
Ask the founder if not provided: **niche** (industry filter, blank = all), **limit**
(default 20). Always recommend a dry run for a new niche.

### Step 2 — Verify leads load (free, no API calls)
```bash
python3 tools/cold_email.py --list --niche "NICHE"
```
Zero leads → create or fix the pipeline records first; don't proceed to generation.

### Step 3 — Dry run (~5 emails, real API calls)
```bash
python3 tools/cold_email.py --stage "New Lead" --niche "NICHE" --limit 5 --dry-run
```
The founder reads the previews and confirms tone before the full batch burns budget on
20 emails in the wrong voice.

### Step 4 — Full run
```bash
python3 tools/cold_email.py --stage "New Lead" --niche "NICHE" --limit LIMIT
```
The CSV lands in `ventures/<your-venture>/deliverables/cold-email-exports/` (created at runtime).

### Step 5 — Report results
How many generated, preview of the top 3 (subject + body), CSV path.

## Before sending — email addresses

Lead records usually capture name/website/phone, not email addresses. Fill `first_name`,
`last_name`, `email` in the CSV via the business website, an email-finder tool's free
tier, or a phone call. Never send to a guessed or unverified address.

## Importing into <YOUR OUTREACH TOOL>

- Import the CSV as a new sequence; default cadence: 3 touches, 3 days apart
- Send from a secondary domain — never your primary business domain (deliverability
  damage on your main domain is near-permanent)
- Subject line is pre-written in the CSV — use as-is

## After the founder confirms send (non-negotiable)

For each sent lead:
- Move its <TASK SYSTEM> task to the Contacted stage and comment
  "Cold email touch 1 sent YYYY-MM-DD"
- Update the workspace deal record to `stage: contacted` and log an activity note
  (type: email-sent)

The script does NOT do these writes — the agent does, then verifies them on disk. When
replies come in, hand off to `follow-up-nurture`.

## Costs and hygiene

- Use a cheap model tier for batch generation and validate the model slug against your
  router's live model list before any run — slugs rot.
- A 20-email batch costs on the order of cents at budget-tier pricing; still dry-run first.
- The export CSV contains prospect contact data — gitignore the exports folder; never
  commit it to a repo.
