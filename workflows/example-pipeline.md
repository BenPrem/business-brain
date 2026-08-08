# Cold Email Pipeline — SOP (Example Workflow)

> **This file is the PATTERN for workflow SOPs — it does not ship with its parts.**
> The tool (`tools/cold_email.py`) and skill (`cold-email-campaign`) it references are
> ones you'd build for your own pipeline; neither is included in this repo. Keep the
> structure, swap in your own tool, skill, and platforms.

**Skill:** `cold-email-campaign` (you build this)
**Tool:** `tools/cold_email.py` (you build this)
**Purpose:** Convert raw leads from the workspace + <TASK SYSTEM> into personalized, ready-to-send cold emails exported as a CSV for your <ESP>.

---

## When to Run This

- After a lead-scraper run adds new leads to the workspace and <TASK SYSTEM> (stage: "New Lead")
- When targeting a specific niche for a campaign (e.g., HVAC, dental, plumbing)
- Weekly or as needed to keep the outreach pipeline moving

---

## Pipeline Overview

```
Workspace + <TASK SYSTEM> (New Lead)
      ↓
cold_email.py (fetch → generate → export)
      ↓
[output dir]/cold-email-[niche]-[date].csv
      ↓
<LEAD SOURCE> (find + verify email addresses)
      ↓
<ESP> (import + send)
      ↓
<TASK SYSTEM> (update stage → "Contacted")
```

---

## Step 1: Dry Run (Always First)

Run a preview before committing to a full export. This generates emails and prints them to the terminal without saving a CSV or updating <TASK SYSTEM>.

```bash
# All new leads, limit 20
python tools/cold_email.py --stage "New Lead" --limit 20 --dry-run

# Filter to a specific niche
python tools/cold_email.py --niche "HVAC" --limit 10 --dry-run
```

**Review the preview output:**
- Does the hook match the lead's pain points?
- Is the internal cost named (not just the external issue)?
- Is there zero fabricated data (no invented percentages, dollar amounts)?
- Is the subject line short and low-key?
- Would you reply to this if you received it cold?

If quality looks good, proceed to Step 2. If not, check the system prompt in `cold_email.py` and refine.

---

## Step 2: Full Run — Export CSV

```bash
python tools/cold_email.py --stage "New Lead" --limit 20
```

CSV saves to a gitignored output directory (prospect data never commits): `cold-email-[niche-or-stage]-[date].csv`

**CSV columns:**
| Column | Source |
|---|---|
| first_name | Manual / <LEAD SOURCE> |
| last_name | Manual / <LEAD SOURCE> |
| email | Manual / <LEAD SOURCE> |
| company | Workspace record |
| website | Workspace record |
| industry | Workspace record |
| location | Workspace record |
| subject | AI-generated |
| body | AI-generated |
| pain_points | Workspace scraper notes |
| source_record | Workspace path or <TASK SYSTEM> task link |

---

## Step 3: Find Email Addresses

The CSV exports without email addresses unless the lead scraper found them. Fill in `first_name`, `last_name`, and `email` using:

- **<LEAD SOURCE>** — domain search: enter the company website, get email format + verified addresses
- **LinkedIn** — manual lookup for high-value targets

Update the CSV directly before importing to your <ESP>.

---

## Step 4: Import to <ESP>

1. Log in to your <ESP>
2. Create a new campaign (use the niche + date as the campaign name)
3. Import the CSV
4. Map columns: `email`, `first_name`, `subject`, `body`
5. Set sending schedule (recommended: 20-30 emails/day from a secondary domain)
6. Launch

**Important:** Always send from a secondary domain (never your primary business domain) to protect the primary domain's reputation.

---

## Step 5: Update <TASK SYSTEM> Stages

After emails are sent or imported, mark leads as "Contacted" in <TASK SYSTEM> and add a short workspace Activity note.

<TASK SYSTEM> owns the stage. The workspace owns the durable interaction history.

---

## Step 6: Monitor Replies + Follow-Up

Once contacted leads start replying:

1. Move the lead to "Reply Received" in <TASK SYSTEM> and add the reply summary to the workspace.
2. If no reply after 3-4 days, Touch 2 goes out (success-story angle) — handled by the follow-up-nurture skill
3. If no reply after 7 days, Touch 3 goes out (close / break-up email)

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ERROR: API key not set` | Add key to `.env` file |
| `No leads found` | Run the lead scraper first, or check the stage name matches <TASK SYSTEM> exactly |
| JSON parse error | Transient model issue — re-run the batch |
| Low email quality | Review the system prompt in `cold_email.py`; check pain-points data in the workspace |
| Model fabricating statistics | System prompt already blocks this — if it slips through, flag and re-run |
| CSV missing emails | Normal — fill via <LEAD SOURCE> before importing |

---

## Model & Cost Notes

- **Model:** cheapest capable model via your LLM router
- **Cost:** roughly $0.001-0.002 per email at ~400 max tokens — 20 emails is pennies
- For higher-stakes campaigns, bump to a mid-tier model

---

## Files Reference

| File | Purpose |
|---|---|
| `tools/cold_email.py` (you build this) | Main pipeline tool |
| Workspace + <TASK SYSTEM> | Lead records, pipeline stages, and follow-up tasks |
| A gitignored output directory (prospect data never commits) | Generated CSV files |
| `.claude/skills/cold-email-campaign/SKILL.md` (you build this) | Skill definition for manual invocation |
| `.env` | API keys (never commit) |

---

> **Note:** This is the workflow file pattern — one SOP per repeatable multi-step process.
> The header triad (Skill / Tool / Purpose) declares what reasons (the skill), what
> executes deterministically (the tool), and what the pipeline produces. Copy this shape
> for every workflow you add.
