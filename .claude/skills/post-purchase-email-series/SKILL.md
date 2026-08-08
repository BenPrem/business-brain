---
name: post-purchase-email-series
description: Generate a multi-part post-purchase email series for customers who just bought a product or service. Trigger on 'post-purchase series', 'buyer follow-up', 'thank-you series', 'customer retention emails', 'after-sale sequence', or 'new buyer welcome emails'. NOT for subscribers who have NOT purchased yet — use welcome-email-series. Produces ready-to-paste subject lines, preview text, and body copy for any ESP (Klaviyo, Mailchimp, etc.).
---

# Post-Purchase Email Series Generator

Generate a complete follow-up series for customers who have already bought.

## Routing

- Recipient has NOT purchased yet → `welcome-email-series`
- One-off operational email to a known contact → `email-composer`
- Review-request campaigns beyond this series → `review-manager`

## Required inputs

Gather before writing anything (ask if missing):
1. **Brand guide** — voice, tone, values, phrases to use/avoid. Check
   `clients/<client-slug>/brand/` (build one via `brand-guide-builder` if none exists).
2. **Product/service details** — what they bought, what receiving/using it is like,
   complementary products
3. **Audience** — who buys, why, what outcome they want
4. **Series length** — default 6 if unspecified

## The post-purchase psychology

Fundamentally different from a welcome series — these people already trust you enough
to buy. Goals in order:
- **Emails 1-2:** eliminate buyer's remorse; make them feel smart and excited
- **Emails 3-4:** deepen the relationship from transactional to emotional
- **Emails 5-6:** expand the relationship — next purchase and advocacy, naturally

## Series framework

### Email 1: Gratitude & Confirmation (send: immediately after purchase)
- Genuine, enthusiastic thank you; confirm what they bought and what happens next
  (shipping, delivery, access)
- Brief reminder of why they made a great choice (1-2 key benefits)
- Set expectations for the series: "over the next couple weeks I'll send tips to get
  the most out of [product]"
- Tone: excited, reassuring. CTA: soft (track order, access purchase, follow on social)

### Email 2: The Quick Win (day 2-3, or upon delivery/access)
- One specific, actionable tip to get immediate value
- Physical products: first-use and care tips · content: suggested starting point ·
  services: first steps or quick setup
- Tone: helpful, practical. CTA: soft (try this now, reply with questions)

### Email 3: The Deeper Story (day 5-7)
- The backstory of the product — why it was created, the passion behind it
- Connect the creator's intention to the buyer's experience; the purchase becomes a
  story they're part of, not a transaction
- Tone: personal, meaningful. CTA: soft (share with a friend, join the community)

### Email 4: Social Proof & Belonging (day 10-12)
- How other customers use and love the product — real testimonials, photos, stories
  only; never fabricated
- Invite them into the community; subtly normalize repeat purchase ("many of our
  customers also love...")
- Tone: validating, warm. CTA: medium (leave a review, tag us, join the group)

### Email 5: Cross-Sell / Upsell (day 14-16)
- Bridge naturally: "since you loved [product], you might also enjoy..."
- Focus on how the addition extends their experience; loyal-customer benefit if one
  really exists (exclusive discount, early access, bundle)
- Recommend only what genuinely makes sense
- Tone: helpful, appreciative — not pushy. CTA: direct (shop the collection, grab the offer)

### Email 6: The Loyalty Loop (day 20-21)
- Thank them again; ask for a review (direct link, simple prompt — easy)
- Introduce the referral program if one exists
- A reason to stay connected: upcoming products, content, events
- Tone: warm, forward-looking. CTA: direct (review, refer, stay connected)

## Adjusting for series length

- **3:** Gratitude + Quick Win → Story + Social Proof → Cross-Sell + Loyalty
- **4:** Gratitude → Quick Win → Social Proof + Cross-Sell → Loyalty Loop
- **5:** Gratitude → Quick Win → Story → Social Proof + Cross-Sell → Loyalty Loop
- **7-8:** add a tips-and-tricks email, UGC spotlight, or behind-the-scenes peek
- **9+:** add re-engagement checks, seasonal tie-ins, milestone celebrations

## Output format (per email, copy-paste ready)

```
---
EMAIL [#] OF [TOTAL]: [DESCRIPTIVE NAME]
Send timing: [relative to purchase]
Automation trigger: [purchase confirmed / delivery confirmed / X days after purchase]
---
SUBJECT LINE: [primary]
SUBJECT LINE (ALT): [A/B alternative]
PREVIEW TEXT: [40-90 characters]
---
[Body copy — short paragraphs, brand voice, personalization tokens per the ESP table;
reference the specific product where possible — [PRODUCT NAME] placeholder if dynamic
insertion isn't available]
---
CTA BUTTON TEXT: [button copy]
CTA LINK DESTINATION: [where it points]
---
INTERNAL NOTES:
- [Build guidance for the ESP]
- [Imagery/design notes]
- [Conditional content — e.g. different copy per product]
```

## Writing guidelines

**Voice:** match the brand guide; default warm, personal, celebratory. The tone of a
friend who's excited you got the thing they recommended — never "being marketed to again".

**Structure:** 1-3 sentence paragraphs, generous line breaks (mobile), front-load the
point, skimmable in 30 seconds, 150-350 words per email.

**Subject lines:** under 50 characters when possible; reference their purchase or
customer status (lifts opens); warmth and curiosity, not urgency — they already bought;
always an A/B alternative; never ALL CAPS or "!!!".

**Merge tags & automation (adapt to the client's <ESP>):**
- First name with fallback — Klaviyo: `{{ first_name|default:'friend' }}` ·
  Mailchimp: `*|FNAME|*`
- Product purchased — Klaviyo: event variables from the triggering metric (inspect a
  real event payload before using; exact paths depend on the e-commerce integration) ·
  Mailchimp: e-commerce merge tags if connected
- Trigger — metric-triggered flow on placed-order (buy) or fulfilled-order
  (shipped/delivered) with time delays between emails
- Suppress the series if the customer buys again mid-flow (e.g. flow filter
  "placed order zero times since starting this flow")

**Avoid:** treating post-purchase as just another sales funnel, cross-selling before
the product even arrives, receipt-flavored "thanks for your order" copy, asking for a
review before they've used the product, more than one CTA per email, hiding returns or
support links.

## Process

1. Read the brand guide and all inputs
2. Confirm understanding: voice, audience, product, series length
3. Map the product experience timeline (when received? when first used?) to email timing
4. Draft all emails in sequence; present in the output format; iterate on feedback
5. Client work: log the deliverable in the client's record and update the matching
   <TASK SYSTEM> task
6. Regulated-topic gate: financing offers, health claims, or similar regulated language
   passes the client's compliance checklist before delivery

## Deploying into the ESP

This skill ends at approved copy. Deployment gotcha: in flow-based ESPs (e.g. Klaviyo),
customers see the FLOW-BOUND template — updating the template library alone changes
nothing. Verify on the flow itself, and confirm by viewing what a real recipient
receives, not by an API success response.
