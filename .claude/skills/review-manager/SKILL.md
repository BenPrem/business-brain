---
name: review-manager
description: Monitor and manage Google reviews for your own business and clients — drafts owner responses, review-request campaigns, and monthly reputation reports; also a sellable monthly service. Triggers on "check reviews", "review response", "reputation", "review request", "get more reviews". NOT for full Google Business Profile / local SEO optimization — use gbp-local-seo.
---

# Review Manager

Respond to every review. Request reviews at the right moment. Track reputation over time.

## When to use
- Responding to Google reviews (your own or a client's)
- A project just delivered — time to ask for a review
- Pitching reputation management as a service
- Weekly or monthly reputation check

## Two modes
- **Mode A — Own reviews**: build the operator's reputation as the business grows
- **Mode B — Client service**: manage reviews as part of a monthly retainer (sellable add-on — pricing is value-based; the operator sets the number)

**Regulated-claims gate:** any review response or reputation content that mentions or implies regulated offers (financing terms, medical/legal outcomes) needs the operator's compliance sign-off before it's posted.

---

## Review Response Drafting

### Step 1 — Get the reviews

Ask the operator to paste the review text (reviewer name, star rating, text, date), or look the business up publicly. Until a Google Business Profile API integration is built (you build this — the skill works manually without it), reviews arrive by paste or screenshot.

### Step 2 — Draft a response

**Positive reviews (4-5 stars):**
- Thank them by name
- Reference something specific from their review — never generic "thanks for the kind words"
- Reinforce the experience they described
- Under 50 words, short and genuine, no emojis, no exclamation-point overload

```
[Name], really glad to hear that. [Specific reference to what they mentioned.]
[Brief reinforcement.] Thanks for taking the time to share.
```

**Negative reviews (1-3 stars):**
- Acknowledge their experience — never dismiss or argue
- Apologize for the specific issue, not a blanket "sorry for the inconvenience"
- Take it offline: "I'd like to make this right — can you reach me at [contact]?"
- Professional and calm — future customers are reading this
- Under 75 words

```
[Name], I appreciate you sharing this and I'm sorry about [specific issue].
That's not the experience we want anyone to have. I'd like to make this right —
could you reach me at [contact]? I want to hear more about what happened.
```

**Fake or spam reviews:** draft a brief, professional response noting no record of the interaction; flag for the operator to report through Google Business Profile.

### Response rules
- Never defensive or sarcastic
- Never offer compensation publicly — do it privately
- Never reveal private details of a customer's transaction
- Respond to every review, positive and negative — consistency signals the business cares
- Never fabricate a review, a reviewer, or a response history

---

## Review Request System

### When to ask (highest conversion first)
1. **Right after a deliverable is approved** — the client just said "this looks great"; strike while they're happy
2. **After a compliment via email or text** — "Glad you said that — would you mind leaving a quick Google review?"
3. **At project completion** — part of the handoff process
4. **After 30 days of a retainer** — enough time to see results

### Draft request messages

**Email version:**
```
Subject: Quick favor — 30 seconds

Hi [Name],

Really enjoyed working on [project] with you. If you had a good experience,
would you mind leaving a quick Google review? It makes a huge difference
for a small business like ours.

Here's the direct link: [Google review link]

No pressure at all — and thanks again for trusting us with [project].

<YOUR NAME>
<YOUR BUSINESS>
```

**Text version (closer relationships):**
```
Hey [Name] — really glad you're happy with [project].
Would you mind leaving us a quick Google review?
Here's the link: [URL]
Totally optional but it means a lot. Thanks!
```

### Generate the direct review link
```
https://search.google.com/local/writereview?placeid=[PLACE_ID]
```
Find each business's Google Place ID once and store it in that client's `clients/<slug>/brand/brand.md` (your own in `ventures/<your-business-slug>/brand/brand.md`).

---

## Monthly Reputation Report (client service)

```markdown
# Reputation Report — <CLIENT>
**Period**: [Month Year]

## Snapshot
- Current rating: [X.X] · Total reviews: [X] · New this month: [X] · Responded: [X]/[X]

## Rating Trend
- Last month [X.X] → this month [X.X] ([+/- X.X])

## Review Themes
**Positive (what customers love):** [theme] — mentioned [X] times
**Negative (areas to improve):** [theme] — mentioned [X] times

## Actions Taken
- [X] owner responses drafted and posted · [X] review requests sent · [flagged spam if any]

## Recommendations
- [Specific suggestion grounded in the themes — e.g. "3 negative reviews mention wait times — address operationally"]
```

Save to `clients/<slug>/deliverables/reputation-report-[YYYY-MM].md`. Every count and theme comes from real reviews you were given — an unknown metric is reported as a gap, never invented.

---

## Selling Review Management

**Problem framing (StoryBrand):** "You've got 12 Google reviews and your competitor has 87. When someone searches for [service] in [city], who do you think they call first?"

**What the retainer includes:** respond to every new review within 24 hours · monthly review-request campaigns to recent customers · monthly reputation report with trends and recommendations · monitoring and flagging fake/spam reviews.

**Pricing:** value-based — get the number from the operator; never quote one from memory. Pairs naturally with website builds and SEO as a proposal add-on.

---

## Write-back

After any response is posted or request sent for a client: log an activity note in the client record (date, type, 1-2 sentence summary) and update the matching <TASK SYSTEM> task.

## Hard rules
- This skill outputs drafts — never post a response or send a request without the operator's approval.
- Route GBP completeness, categories, posts, and citations to **gbp-local-seo**.
