---
name: follow-up-nurture
description: Manage pipeline follow-ups by lead stage - reply handling, proposal cadence, re-engagement ladder, meeting confirmations - against workspace records and <TASK SYSTEM>. Trigger on follow up, check the pipeline, who needs a follow-up, nurture, what's next with [name]. NOT for first-touch outreach (use cold-email) - this skill handles everything AFTER the first email is sent.
---

# Follow-Up Nurture

Read the pipeline in <TASK SYSTEM> and the workspace lead records. Identify who is due
for contact. Draft the right follow-up for their stage.

## Routing

- Writing the first cold email → **cold-email**
- Known contact with no active sales stage → **email-composer**
- Everything after the first touch, by stage → this skill

---

## Step 1 — Pull leads due for follow-up

- Check <TASK SYSTEM> for active leads with a follow-up due today
- Filter for stages: Reply Received, Proposal Sent, Meeting Booked, Negotiating,
  Contacted
- Read each matching workspace record for notes, pain points, last contact, proposal
  links, and next-step context

---

## Step 2 — Prioritize by stage (highest urgency first)

### Reply Received (respond same day)

Read the reply. Categorize:

| Reply type | Action | Tone |
|-----------|--------|------|
| Interested | Propose 2-3 meeting times | Warm, confident, match their energy |
| Question | Answer directly, re-present the CTA | Helpful, brief |
| "Not now" | Acknowledge, ask to follow up in 60-90 days | Graceful, zero pressure |
| Not interested | Thank them, close the lead | Professional, brief |
| Auto-reply / OOO | Note return date, set follow-up for it | No response needed |

After drafting: move the task to the right stage (Meeting Booked or Closed Lost) and
write the follow-up note/date into the workspace record.

### Proposal Sent (touch at 3, 7, 14 days)

| Day | Message |
|-----|---------|
| 3 | Quick check-in. "Any questions about the proposal?" One sentence + the question. |
| 7 | Add value — one insight or idea NOT in the proposal. Show you are still thinking about their business. |
| 14 | Gentle breakup. "I know timing matters. Want me to check back in a month?" Usually the highest-response touch. |

### Contacted, no reply (10+ days)

Confirm from the activity log what first touch actually happened — never assume a
sequence ran.

| Timeframe | Action |
|-----------|--------|
| ~14 days | Completely different angle — new hook, different service, new subject. Never "just checking in." |
| 30 days | One more attempt referencing something timely (season, local event, industry trend). Last touch before archiving. |
| 45+ days | Move to Cold. Revisit only on a trigger event (news, site visit, hiring). |

### Meeting Booked

- **Immediately:** confirmation with date/time, brief agenda, what to expect
- **24 hours before:** short, friendly reminder
- **Prep brief:** run **discovery-call-prep** — it owns the internal brief; do not
  rebuild it here

### Negotiating (case by case)

- Respond within 1-2 days
- Address the specific objection directly
- Never discount without adjusting scope — add or remove deliverables instead
- Reference the cost of inaction subtly (StoryBrand stakes)

---

## Step 3 — Draft the follow-ups

All follow-ups inherit the cold-email skill's tone rules:

- Prospect is the hero — never open with "I" or "we"
- Under 100 words (shorter than initial outreach)
- No spam trigger words, no dollar signs, no hyperlinks in cold-pipeline sends
- Trying a new angle → reuse cold-email's hook structure

Present all drafts to the founder for review. Never send without approval.

---

## Step 4 — Update records

After every follow-up action:

- Workspace record: last contact date, next follow-up date, current stage, short note
- <TASK SYSTEM>: task stage and due date, moved forward when appropriate

---

## Step 5 — Report

```
Pipeline Follow-Up Report — [date]
==================================
Replies handled: X  (meetings booked: X · closed lost: X)
Proposals followed up: X
Re-engagement drafted: X
Next follow-ups due tomorrow: X

Pipeline health:
  Reply Received: X (respond today)
  Meeting Booked: X
  Proposal Sent: X
  Contacted (waiting): X
  Total active: X
```

---

## Self-improvement

When a lead goes Closed Lost, look for the pattern: follow-up too late → tighten the
timing table; tone too pushy or too passive → adjust guidance; missed buying signal →
add a classification rule. Log durable lessons to your rules file.
