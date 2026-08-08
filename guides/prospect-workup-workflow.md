# Prospect Workup Workflow — the 6-Phase Methodology

For every new service-business prospect, run this full workup **before pitching**. It turns a cold lead into a prospect who has already seen what working with you looks like. A companion `prospect-workup`-style skill or runner script can automate the pipeline; this guide is the deep methodology the automation implements, and the reference for re-running any single phase by hand.

The phases run in order — each consumes the previous phase's output.

## Phase 1: Scrape & Research

- Scrape the prospect's entire website (every page) with a crawling tool.
- Extract their branding: colors, fonts, logo.
- Search for their reviews, social presence, and directory listings.
- Identify location, services, team members, and contact info.
- Note anything distinctive about the business (family-owned, niche focus, values-driven) — it becomes personalization fuel later.

Output: `clients/<slug>/research-scrape.md` (plus raw data JSON if automated).

## Phase 2: Competitor Analysis

- Find 4–5 competitors in their market, local and regional.
- Scrape each competitor's website.
- Build a feature comparison matrix: online booking, reviews, SEO, social, chat, financing, and whatever else matters in the vertical.
- Score the prospect against the field, and flag which competitors are actively targeting the prospect's territory.

Output: `clients/<slug>/competitor-analysis.md`

## Phase 3: Website Audit

- Score the current site out of 100 with a page-by-page breakdown of specific issues.
- SEO analysis: title tags, meta descriptions, local keywords, business-profile health.
- Quantify the gap between the prospect and their best competitor.
- Calculate the "word-of-mouth ceiling" — what referral-only growth is leaving on the table — and estimate lost monthly revenue from a weak online presence. Label estimates as estimates; never dress a model up as a measurement.

Output: `clients/<slug>/website-audit.md`

## Phase 4: Demo Website Build

- Build a static HTML/CSS demo on the StoryBrand structure (`guides/storybrand-framework.md`).
- Use photos from their existing site, supplemented by stock lifestyle shots (visually verify every stock image before it ships).
- Include the Speed-to-Call scheduling questionnaire as the primary CTA, customized to their industry (`guides/speed-to-call-methodology.md`).
- Sections: hero, problem, guide, plan, services, gallery, testimonials (clearly placeholder until real ones exist), about, booking CTA.
- Mobile-optimized with a sticky CTA bar.

Output: `clients/<slug>/demo-site/`

## Phase 5: Marketing Plan

- Word-of-mouth gap analysis where applicable.
- Speed-to-Call methodology explanation in the client's terms.
- A three-phase strategy: Foundation → Visibility → Growth.
- Customer profiles they're currently missing.
- Revenue-impact projections (labeled as projections), tool recommendations with costs, and an implementation timeline.

Output: `clients/<slug>/marketing-plan.md`

## Phase 6: Proposal + Preview + Deploy

- Branded HTML proposal following the StoryBrand order: Problem → Stakes → Plan → Speed-to-Call → What You Get → Why Us.
- **No pricing in the proposal.** Let them buy into the vision first; the owner handles pricing in person. No expiration date, no CTA button at the bottom — the close is a human conversation, not a web form.
- Build a preview landing page with a **side-by-side comparison** (required):
  - Screenshot their current site (desktop + mobile) and your demo (desktop + mobile).
  - Desktop: side-by-side with a "VS" badge; mobile: both in phone frames.
  - A before/after checklist: what they're missing vs what you built.
  - Deliverable links below the comparison; a personalized header addressing the prospect by name.

Outputs: `clients/<slug>/proposal/`, `clients/<slug>/preview/`, assembled into `clients/<slug>/deploy/`.

### Deploy Gate (required)

**Never deploy a prospect-facing preview without the owner's explicit approval.**

1. Stage everything locally in `clients/<slug>/deploy/`.
2. Run a local preview and visually QA it (headless screenshots at real mobile viewports, then eyes on them).
3. Notify the owner: what was built, page list, any issues, and the exact deploy command.
4. Wait for the explicit go — a standing "keep working" instruction is not deploy approval.
5. On approval: deploy, rename the site URL to `<client-slug>-preview` for a professional look, and confirm the live URL loads.

### Standard Folder Structure

```
clients/<slug>/
  research-scrape.md
  competitor-analysis.md
  website-audit.md
  marketing-plan.md
  demo-site/
    index.html
  proposal/
    index.html
  preview/
    index.html
  deploy/
    index.html        (preview page at the root)
    demo/
    proposal/
```

### After the Workup

1. Review every output — read the plan, click through the demo, proofread the proposal.
2. Log the prospect into your CRM records and create the follow-up task in your task manager — and verify both writes landed before reporting them done.
3. Outreach references the live preview URL (with the owner's go-ahead).

## Key Principles

- Always scrape the actual prospect and competitors — never write from general knowledge.
- Always use the prospect's own photos on the demo.
- Always lead with the Speed-to-Call questionnaire as the primary CTA.
- Always quantify estimated lost revenue to justify the investment — honestly labeled.
- Always include the side-by-side comparison; it sells the transformation before a word is read.
- Always personalize the preview header with the prospect's name.
- Never include pricing, expiration dates, or closing CTAs in the proposal — the owner closes personally.
- The bar for the demo: the prospect should say "I want this" before price ever comes up.
