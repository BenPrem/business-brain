---
name: content-calendar
description: Plan and manage a content calendar for your business or a client. Use when the operator says 'content calendar', 'what should I post', 'plan this month's content', or asks about posting schedules. Handles SCHEDULING and POST PLANNING only — assumes a strategy exists (run content-strategy first if not); for writing the actual posts use content-repurposer or social-media-manager. Execution tasks live in <TASK SYSTEM>.
---

# Content Calendar

Plan what to post, when, and where — tied to business goals, not random inspiration.

## Routing

- No content strategy exists for this account yet → run `content-strategy` FIRST. The
  calendar is the execution layer; it needs pillars, audience, and tone to build from.
- Writing the actual posts → `content-repurposer` (from source material) or
  `social-media-manager` (from scratch)
- Auditing an existing social presence → `social-media-auditor`
- The `daily-brief` session kickoff may flag "content planning" as today's priority —
  that lands here.

---

## Step 1 — Gather inputs

Ask the operator:
1. **Who is this for?** (own business or a specific client)
2. **Time period?** (this week, next 2 weeks, this month)
3. **Platforms?** (LinkedIn, X/Twitter, Instagram, Facebook, newsletter, blog — active ones only)
4. **Upcoming events or launches?** (new service, case study, local event, seasonal tie-in)
5. **Existing content to repurpose?** (blog posts, videos, call transcripts)

Then read the account's strategy doc and, for client work,
`clients/<client-slug>/brand/brand.md`.

---

## Step 2 — Confirm the content pillars

Every account needs 3-5 recurring themes — they prevent "what do I post?" paralysis.
Pull them from the strategy doc. Typical service-business pattern:

1. **Expertise / educational** — tactical tips in their domain (positions them as the expert)
2. **Customer stories / results** — before/after, testimonials (social proof)
3. **Behind the scenes** — team, process, lessons learned (trust)
4. **Industry or local insights** — market trends, local observations (authority)
5. **Direct offers / CTAs** — use sparingly, max 20% of posts

---

## Step 3 — Build the calendar

### Posting cadence baseline

| Platform | Minimum | Ideal | Good default slots (local time) |
|----------|---------|-------|--------------------------------|
| LinkedIn | 2/week | 3-4/week | Tue-Thu, 8-10am |
| X/Twitter | 3/week | Daily | Tue+Thu threads, daily singles |
| Instagram | 2/week | 3-4/week | Tue-Thu, 11am-1pm |
| Facebook | 2/week | 3/week | Wed-Fri, 1-3pm |
| Newsletter | 1/bi-weekly | 1/week | Friday morning |
| Blog | 2/month | 4/month | Monday publish |

### Calendar format

One row per post:

```
| Date | Platform | Pillar | Topic | Format | CTA | Status |
|------|----------|--------|-------|--------|-----|--------|
| Mar 18 | LinkedIn | Educational | "3 things your website is missing" | Text post | Follow for more | Draft |
| Mar 18 | X/Twitter | Educational | Same topic, thread format | Thread (5 tweets) | Bookmark | Draft |
| Mar 19 | Facebook | Customer story | Recent project spotlight | Text + image | Request a quote | Idea |
```

**Formats:** text post, thread, carousel, video script, story, reel script, poll,
newsletter, blog post.
**Status flow:** Idea → Draft → Review → Scheduled → Posted.

---

## Step 4 — Log to the task system

Create one <TASK SYSTEM> task per calendar item:
- **Task**: "[Platform] — [topic short title]"
- **Due date**: scheduled post date
- **Notes**: pillar, format, CTA, any source material to repurpose

Optionally save the calendar brief to
`clients/<client-slug>/deliverables/content/` (or your own venture's content folder).

---

## Step 5 — Present the plan

```
Content Calendar — [Who] — [Period]
====================================
WEEK OF [DATE]:
  Mon: [Platform] — [Topic] — [Format]
  Tue: [Platform] — [Topic] — [Format]
  ...
  Fri: [Newsletter] — [Topic]

Pillar distribution: Educational 3 · Customer story 1 · BTS 2 · Local insight 1
Logged [X] tasks to <TASK SYSTEM>.

Ready to write? Run content-repurposer or social-media-manager on any of these.
```

---

## Step 6 — Flag repurposing chains

Mark calendar items that can share source material — this is where `content-repurposer`
takes over:

```
REPURPOSE CHAIN:
  Blog post "3 Website Mistakes" (Mon)
    → LinkedIn post (Tue) — key insight standalone
    → X thread (Tue) — expanded with examples
    → Newsletter block (Fri) — personal angle + CTA
  = 4 pieces from 1 idea
```

---

## Monthly review

At month end (or "how did content do?"):
- Review which posts got the most engagement (operator provides platform data)
- Identify the best-performing pillars
- Lean next month's calendar into what's working; cut what isn't
- Route durable lessons into the strategy doc so they survive between sessions
