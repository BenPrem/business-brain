# Summit Digital — Business Details
**Last updated:** 2026-08-01

Quick orientation summary. Live status lives in `context/current-priorities.md`; client
facts in `clients/[slug]/`; if this file conflicts with either, trust those first.

## The Business
- **What:** Solo marketing agency for local service businesses (trades and clinics) in the
  Boise metro. Founded November 2025; first revenue February 2026.
- **Positioning:** the marketing department a 5–30 person service business can't hire —
  senior strategy plus AI-accelerated execution, priced as one system instead of five
  freelancers.
- **Services:**
  - Website builds and rebuilds (conversion-first, not brochure sites)
  - Brand refresh (logo cleanup, colors, voice — light, not full rebrand agency work)
  - Local SEO and Google Business Profile management
  - Review generation systems
  - Monthly retainer: the above ongoing, plus reporting that proves ROI
- **Target market:** established Boise-metro service businesses doing $1M–$8M/yr with no
  in-house marketer. Roofing, HVAC, dental, ortho, landscaping. Avoiding restaurants
  (churn) and startups (no budget).
- **Revenue model:** foundation project as the audition ($8K–$15K range historically),
  retainer as the real engine. Retainer target: $4K/mo per client, 3 clients = the
  $10K/mo MRR goal.

## Current Clients
- **Canyon Roofing Co.** — flagship. $12K website + brand project delivered May 2026, now
  $4K/mo retainer. Owner Dana Whitfield (she/her). Record: `clients/canyon-roofing/_index.md`.
- **Lakeside Dental** — $8K website project in progress, target launch Aug 29. Contact
  Dr. Sam Okafor (he/him). Record: `clients/lakeside-dental/_index.md` (not included in
  this excerpt).

## Tools in Use
- **Claude Code** — primary build/execution layer; this repo is the brain.
- **Netlify** — static hosting and previews for all client sites.
- **Google Workspace** — email/calendar (alex@summitdigital.example).
- **Stripe** — invoicing. Ledger mirrored in `finances/invoices.md` (not included in
  this excerpt).
- **Figma** — client-facing design review only; production is code-first.
- **CallRail trial** — call tracking for Canyon Roofing, decision due Aug 15 (see
  current-priorities).
- Not yet connected: GA4 API (reports are manual exports), any CRM (TASKS.md per client
  for now).

## Key Metrics to Track
- MRR: **$4K/mo** (Canyon Roofing). Goal $10K/mo by end of Q4 2026.
- Cash collected 2026 YTD: $20K (Canyon $12K project + $4K June retainer + Lakeside $4K
  deposit). Canyon July retainer invoice is OVERDUE — see current-priorities.
- Canyon Roofing leads/month: 22 in July (vs ~9/mo pre-rebuild) — the number that renews
  the retainer; verify from form logs + call tracking before quoting it.
- Pipeline: 2 warm referrals (an ortho practice, a landscaping company) — nurture, don't
  push until Lakeside ships.
