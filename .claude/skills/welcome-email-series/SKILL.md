---
name: welcome-email-series
description: Generate a multi-part welcome/nurture email series for new subscribers who have NOT yet purchased. Trigger on 'welcome series', 'nurture sequence', 'cold lead emails', 'subscriber onboarding', 'opt-in follow-up', or 'email funnel for new signups'. NOT for people who already bought — use post-purchase-email-series. Produces ready-to-paste subject lines, preview text, and body copy for any ESP (Klaviyo, Mailchimp, etc.).
---

# Welcome Email Series Generator

Generate a complete welcome/nurture series for subscribers who signed up but haven't
bought yet.

## Routing

- Recipient already purchased → `post-purchase-email-series`
- Single first-touch email to a cold prospect → `cold-email`
- One-off operational email to a known contact → `email-composer`
- Stage-based pipeline follow-ups → `follow-up-nurture`

## Required inputs

Gather before writing anything (ask if missing):
1. **Brand guide** — voice, tone, values, phrases to use/avoid. Check
   `clients/<client-slug>/brand/` for a brand file (build one via `brand-guide-builder`
   if none exists).
2. **Product/service details** — what's sold, key features, unique value proposition
3. **Audience** — who subscribes, what motivated the signup, pains, aspirations
4. **Series length** — default 6 if unspecified

## Series framework

The arc below is the full 6-email version. Adapt length, preserve the psychological
progression: welcome → connection → value → proof → pitch → close.

### Email 1: The Warm Welcome (send: immediately)
Deliver on the opt-in promise and set expectations.
- Thank them; deliver any promised lead magnet
- Briefly introduce the brand/founder — who you are, why you exist
- Set expectations: what they'll receive, how often
- Tone: warm, personal, grateful — NOT salesy. CTA: soft (read a post, follow, reply to say hi)

### Email 2: The Story (day 2-3)
Build emotional connection through origin story or mission.
- The founder's story or the brand's "why", connected to the subscriber's world
- Establish credibility without bragging
- Tone: authentic, narrative. CTA: soft

### Email 3: The Value Drop (day 4-5)
Prove expertise by giving genuine value with no ask.
- Teach something useful or solve a small problem, related to the product without pitching it
- Tone: helpful, generous. CTA: soft (try a tip, read more)

### Email 4: Social Proof & Community (day 7-8)
Show that others trust what you offer.
- Real testimonials, reviews, or user stories — never fabricated; if none exist, use
  real results, milestones, or media mentions instead
- Make them feel like they're joining something, not just a list
- Tone: confident, celebratory. CTA: medium (join community, see the bestseller)

### Email 5: The Soft Pitch (day 10-12)
Introduce the product as the natural next step.
- Bridge from the value given to the product as the deeper solution
- Transformation and outcomes, not features; address 1-2 common objections in the copy
- A specific reason to act (discount, bonus, limited availability) only if real
- Tone: confident, helpful — not pushy. CTA: direct (shop now, learn more)

### Email 6: The Gentle Close (day 14-15)
Final nudge with urgency or a new angle.
- Reframe the value ("what you're missing" / "imagine if...")
- Light urgency only with a real reason — never fake scarcity
- Recap the series; end warm regardless of whether they buy
- Tone: encouraging, no-pressure but clear. CTA: direct

## Adjusting for series length

- **3:** Welcome → Value + Story → Soft Pitch
- **4:** Welcome → Story → Value + Social Proof → Soft Pitch
- **5:** Welcome → Story → Value → Social Proof + Soft Pitch → Gentle Close
- **7-8:** add extra value drops, or split proof into testimonials + community
- **9+:** add re-engagement or segmentation emails between value and pitch phases

## Output format (per email, copy-paste ready)

```
---
EMAIL [#] OF [TOTAL]: [DESCRIPTIVE NAME]
Send timing: [relative to signup]
---
SUBJECT LINE: [primary]
SUBJECT LINE (ALT): [A/B alternative]
PREVIEW TEXT: [40-90 characters]
---
[Body copy — short paragraphs, brand voice, personalization tokens per the ESP table]
---
CTA BUTTON TEXT: [button copy]
CTA LINK DESTINATION: [where it points — describe if URL unknown]
---
INTERNAL NOTES:
- [Build guidance for the ESP]
- [Imagery/design notes]
- [Segmentation or automation trigger notes]
```

## Writing guidelines

**Voice:** match the brand guide; default conversational, warm, personal. Write like a
real person — founder's name or "we", never generic corporate language.

**Structure:** 1-3 sentence paragraphs, generous line breaks (mobile), front-load the
point, skimmable in 30 seconds, 150-350 words per email — shorter is usually better.

**Subject lines:** under 50 characters when possible; curiosity/benefit/personal
connection, no clickbait; always an A/B alternative; never ALL CAPS or "!!!"; emoji
only if the brand guide supports it, max one.

**Merge tags & automation (adapt to the client's <ESP>):**
- First name with fallback — Klaviyo: `{{ first_name|default:'friend' }}` ·
  Mailchimp: `*|FNAME|*`
- Trigger — list-subscribed automation with time delays between emails
- Flag emails needing segmentation or conditional content blocks

**Avoid:** aggressive sales language in emails 1-3, fake urgency, generic filler
("In today's fast-paced world..."), walls of text, more than one CTA per email,
unsubscribe guilt-tripping.

## Process

1. Read the brand guide and all inputs
2. Confirm understanding: summarize voice, audience, product, series length
3. Draft all emails in sequence; present in the output format
4. Iterate on feedback
5. Client work: log the deliverable in the client's record and update the matching
   <TASK SYSTEM> task
6. Regulated-topic gate: if any email touches financing offers, health claims, or
   similar regulated language, run the client's compliance checklist before delivery

## Deploying into the ESP

This skill ends at approved copy. Deployment gotcha worth knowing: in flow-based ESPs
(e.g. Klaviyo), subscribers see the FLOW-BOUND template — updating the template library
copy alone changes nothing. Verify the change on the flow itself, and confirm shipped
copy by viewing what a real subscriber receives, not by the API returning success.
