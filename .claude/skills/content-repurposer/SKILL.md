---
name: content-repurposer
description: Turn one piece of existing content into multiple platform-specific outputs. Use when the operator says 'repurpose this', 'turn this into posts', 'tweet thread from this', 'atomize', 'content from this transcript', or provides any long-form content to distribute across channels. REQUIRES source content as input — for a new post from scratch use social-media-manager. Outputs are copy-paste ready per platform.
---

# Content Repurposer

One input → multiple platform-ready outputs. No extra writing sessions needed.

## Routing

- No source content exists (post from scratch) → `social-media-manager`
- Long-form written from scratch with research → `content-research-writer`
- Deciding WHAT to post and when → `content-calendar`
- This skill = the operator provides a transcript, blog post, case study, call summary,
  or raw idea and wants platform outputs from it.

---

## Step 0 — Who is this for?

Confirm the mode before writing anything:
- **Own-business mode** — your content, your voice. Save under
  `ventures/<venture-slug>/deliverables/content/`.
- **Client mode** — voice source is `clients/<client-slug>/brand/brand.md` (always
  check the client's brand folder before building anything). Save under
  `clients/<client-slug>/deliverables/content/`.

If the client operates in a regulated space (financing offers, health claims, legal
services), run their compliance checklist over every output before delivery.

## Step 1 — Analyze the input

Extract from the source:
- **Core insight** — the one big idea every output orbits
- **Key quotes/phrases** — anything punchy enough to stand alone
- **Data points** — numbers, results, names, places (real ones only — never invent)
- **Story elements** — before/after, lesson learned, unexpected outcome
- **Audience relevance** — why does the target reader care?

## Step 2 — Load the voice

Read the voice source for the chosen mode. Defaults if none exists (ask before assuming):
- Straightforward, no corporate-speak; gets to the point
- Real examples over abstract concepts; speaks from experience
- Confident without arrogance; no emojis unless the brand uses them
- **Education-first** — teach something useful in every output
- **Narrow beats wide** — each output speaks to one specific reader
- **Assume nothing** — every output works standalone for a first-time reader

---

## Step 3 — Generate outputs

### LinkedIn post
**Length:** 150-300 words.
**Structure:** Line 1 = scroll-stopping hook (bold claim, specific number,
counterintuitive insight) — it must work alone, it's all people see before "...see
more". Empty line 2. Then story/context, one idea per line, short paragraphs. End with
takeaway + CTA (question, follow, comment prompt). Last line: 3-5 hashtags.
**Rules:** never open with "I'm excited to share..." or "In today's fast-paced world...".
Write like a person, not a brand account. Specific beats clever — "we signed a client
from one cold email" beats "cold email works if you do it right".

### X/Twitter thread (3-7 tweets)
**Tweet 1:** the hook — must deliver standalone value.
**Tweets 2-6:** one idea each, under 280 characters, specifics (names, numbers, tools),
"→" or numbered lists for structure.
**Final tweet:** restate the core idea + CTA ("Follow for more [topic]" / "Bookmark this").
No tweet may depend on the previous one to make sense.

### Email newsletter block
**Length:** 200-400 words.
**Structure:** 1-2 sentence personal intro → main insight in 2-3 short paragraphs → how
it applies to the reader → one CTA.
Provide **3 subject line options** — short, curiosity-driven, no caps or punctuation tricks.

### Blog post (only when requested)
**Length:** 800-1,500 words.
**Structure:** H1 with target keyword; hook opening, no throat-clearing; 3-5 H2
sections with practical takeaways; specific examples from the business's real work;
closing CTA tied to the relevant service.
**SEO basics:** keyword in H1 and first 100 words; meta description under 160
characters; internal links to service pages.

### Instagram/Facebook caption (only when requested)
**Length:** under 150 words. Hook line → brief insight → CTA. Include an image-concept
suggestion (what visual pairs with this).

---

## Step 4 — Save and present

Save all outputs to one file in the mode's content folder (`mkdir -p` on first use):
`<mode-folder>/<YYYY-MM-DD>-<topic-slug>.md`, one section per platform.

Present everything for review. The operator picks what posts and when.

## Step 5 — Log it

Append to `<mode-folder>/content-log.md`:

```
| Date | Topic | Platforms | Status |
|------|-------|-----------|--------|
```

Then push into the execution layer (mirrors `content-calendar`):
- If <TASK SYSTEM> tasks exist for these calendar slots, attach the draft location and
  move status to Review.
- If not, create one task per output batch, due on the intended post date, notes
  pointing at the saved file.
- Client mode: log the deliverable in the client's record before closing out.

---

## Format strategy

Short-form (reels, tweets, carousels) = distribution/awareness — appetizers.
Long-form (blog, newsletter, video) = conversion engine — the meal.

When repurposing, create the long-form version first, then extract shorts from it.
Shorts drive traffic to longs; longs build enough trust to buy.

## Suggested cadence (operator decides timing)

- LinkedIn: Tue or Wed morning · X/Twitter: Tue + Thu, threads in the morning
- Newsletter: weekly or bi-weekly, Friday morning · Blog: 1-2/month
- Long-form video: 1/week minimum if video is an active channel
