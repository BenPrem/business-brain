---
name: content-strategy
description: Build the strategic foundation a client's content runs on — audience personas, platform selection, content pillars, mix ratios, voice guide, 90-day KPIs. Use when the operator says 'content strategy', 'build a strategy for [client]', 'what should our content approach be', or when onboarding a social media client who needs a foundation before any posts. Competitor research is REQUIRED before writing strategy. NOT for day-to-day posting — use content-calendar or social-media-manager.
---

# Content Strategy

Build the strategic foundation before a single post gets written. This skill owns the
"why" and "what" — sibling skills handle the "when" (content-calendar) and "how"
(social-media-manager, content-repurposer).

## Routing

- Planning specific posts for the week/month → `content-calendar`
- Writing individual posts → `social-media-manager`
- Turning one piece into many → `content-repurposer`
- Assessing what a prospect currently has → `social-media-auditor`
- New-client setup (folders, records, kickoff) → `client-onboarding`

**Skill chain for a new content client:**
`social-media-auditor` (where they are) → `content-strategy` (this skill — where they're
going) → `content-calendar` (first month) → `social-media-manager` / `content-repurposer`
(execution).

---

## Step 0 — Competitor research is mandatory

Never write a content strategy from general knowledge. Before Step 2, research 3-5 real
competitors in the client's market:

- Find them: search "[service] [city]", check who ranks, who runs ads, who the client
  names as rivals. `web-research` handles the fan-out; `competitive-ads-extractor` pulls
  their live ads if paid social matters here.
- For each competitor record: platforms active, posting frequency, content types that
  get engagement, hooks/angles they lean on, gaps they leave open.
- The strategy must cite what competitors are doing and where the whitespace is. A
  strategy with no competitor section is not done.

---

## Step 1 — Gather inputs

From the operator or the client:
1. **Business goals** — leads, foot traffic, awareness, hiring, community?
2. **Target audience** — ideal customer demographics, psychographics, where they spend time online
3. **Current state** — what content exists, what worked, what didn't (use `social-media-auditor` output if available)
4. **Competitive landscape** — Step 0 findings
5. **Budget and resources** — who creates content, how much time/money is real
6. **Brand voice** — read `clients/<client-slug>/brand/brand.md` if it exists

Answer the narrative questions that become the messaging backbone for all content:
- Who is the hero (their customer — never the business)?
- What problem does the customer have (external, internal, philosophical)?
- How does this business guide them, what's the plan, what does success/failure look like?

Core content doctrine to bake in:
- **Education over entertainment** for business audiences — teach, don't water down
- **For them, not us** — customer problems, not company news
- **Narrow beats wide** — one specific reader per piece
- **Revenue over views** — every vanity metric gets a paired revenue metric
- **Long-form converts, short-form distributes**
- **Assume nothing** — every piece works for a first-time reader
- **Volume + consistency** — minimum 3 posts/week per active platform

(For offer design and lead-gen mechanics behind the content, see `hormozi-100m-leads`.)

---

## Step 2 — Define the strategy

### A. Audience personas (1-3 max)
```
PERSONA: [Name — e.g., "Busy Mike"]
- Who: [Role, age range, location]
- Struggles with: [Problems related to this business]
- Wants: [Desired outcome]
- Hangs out on: [Platforms, time of day]
- Content they engage with: [Video, text, images]
- How they find businesses: [Search, social, referrals, reviews]
```

### B. Platform selection
Pick 2-3 platforms based on where the audience actually is — better to be great on 2
than mediocre on 5:

| Business type | Primary | Secondary | Usually skip |
|---------------|---------|-----------|--------------|
| B2B / professional services | LinkedIn | X/Twitter | TikTok |
| Local restaurant / retail | Instagram, Facebook | Google Business Profile | LinkedIn |
| Home services (HVAC, plumbing) | Google Business Profile, Facebook | Instagram | X/Twitter |
| Real estate | Instagram, Facebook | LinkedIn | X/Twitter |
| Dental / medical | Google Business Profile, Instagram | Facebook | X/Twitter |

### C. Content pillars (3-5)
Each pillar must connect to a business goal, address an audience pain point, and be
sustainable weekly without running dry. Across all pillars, cover the four engagement
levers: status (aspiration), power (capability the reader gains), credibility (proof),
likeness (relatability).

```
PILLAR: [Name]
- Goal it serves: [awareness / trust / conversion / retention]
- Lever: [status / power / credibility / likeness]
- Example topics: [3-5 specific post ideas]
- Frequency: [X posts/week]
- Best platform: [where this performs]
```

### D. Content mix ratio

| Content type | % of posts | Purpose |
|--------------|-----------|---------|
| Educational / value | 50% | Build authority — education IS the entertainment |
| Social proof / results | 20% | Credibility, overcome objections |
| Story / behind the scenes | 15% | Connection, humanize |
| Direct CTA / offers | 10% | Conversion |
| Community / engagement | 5% | Relationship, algorithm |

Never let direct selling exceed 20%. Be the guide, not the hero — educational content
that solves a problem sells without asking.

### E. Format strategy

| Format | Role |
|--------|------|
| Long-form (blog, 5-15 min video, case study) | Conversion engine — builds deep trust |
| Short-form (reels, shorts, carousels) | Distribution/awareness — drives to longs |
| Email/newsletter | Nurture — keeps the relationship warm |

Always keep one long-form conversion engine running. Shorts bring eyeballs; longs close.

### F. Voice and tone guide
```
WE SOUND LIKE: [3-5 adjectives]
WE NEVER SOUND LIKE: [3-5 adjectives]
WE USE: [Language patterns, local references, terms the audience knows]
WE AVOID: [Jargon, corporate-speak, competitor mentions]
FORMALITY: [Casual / conversational / professional — per platform]
```

### G. 90-day goals — pair every vanity metric with revenue

| Vanity metric | Current | 90-day target | Paired revenue metric | Target |
|---------------|---------|---------------|----------------------|--------|
| Followers | | | Leads from social | |
| Engagement rate | | | Inquiries from engaged users | |
| Site visits from social | | | Visit-to-inquiry rate | |
| Reviews | | | Review-driven calls | |
| Email signups | | | Signup-to-customer rate | |

Never report views or followers without revenue context.

---

## Step 3 — Write the strategy document

Save to `clients/<client-slug>/deliverables/content-strategy-<YYYY-MM-DD>.md`:

```markdown
# Content Strategy — <CLIENT>
Prepared by: <YOUR BUSINESS> · Date · Review period: 90 days

## Executive Summary  — where they are, where they're going, how content gets them there
## Competitive Landscape — what 3-5 competitors are doing + the whitespace
## Target Audience — personas
## Platform Strategy — which, why, cadence each
## Content Pillars — pillars with example topics
## Content Mix — ratio table
## Voice & Tone
## 90-Day Goals — paired-metric KPI table
## Month 1 Focus — quick wins, account setup, first posts
## Ongoing Cadence — weekly rhythm: what, when, by whom
## Measurement & Iteration — when performance is reviewed and how the plan adjusts
```

If presenting to the client as a deliverable, generate a clean version without internal
notes — this document is what they're buying when they sign up for content management.
(A branded proposal wrapping it → `proposal-generator`.)

---

## Step 4 — Set up for execution

After the strategy is approved:
1. Run `content-calendar` to plan the first month
2. Create a recurring <TASK SYSTEM> task: "Monthly content strategy review"
3. Link the strategy doc from the client's README/record so every later content session finds it

Pricing note: if strategy is sold as a standalone service, the operator sets the number —
never auto-fill a price into the deliverable.
