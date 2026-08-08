---
name: gbp-local-seo
description: Audit and optimize Google Business Profiles and local SEO for local-service clients — completeness scoring, ranked fixes, 2x/week GBP post plans, NAP/citation sweeps, no-paid-tool rank checks. Triggers on "GBP", "Google Business Profile", "local SEO", "map pack", "local rankings". NOT for review responses or review-request campaigns — use review-manager.
---

# GBP + Local SEO Manager

Drive map-pack visibility for local-service clients. Without GBP API access this skill PREPARES everything — audits from public data, post copy, ranked fix lists — as paste-ready deliverables the operator (or the client) executes in the GBP UI. Items marked *[automation]* activate only once API access exists.

## Paths
- All outputs → `clients/<slug>/deliverables/local-seo/` (`mkdir -p` first), date-stamped `YYYY-MM-DD-*.md`
- Canonical business facts (name, address, phone, services, service areas) come from the client record at `clients/<slug>/` — never guess them

## 1. GBP audit — completeness score (100 pts)
Pull what's publicly visible (web search + fetching the Maps listing and brand searches). Score:

| Item | Pts | Pass bar |
|---|---|---|
| Primary category correct + specific | 15 | e.g. "Window installation service", not generic "Contractor" |
| 2-5 secondary categories | 10 | Each maps to a real service page on the site |
| Services listed WITH descriptions | 10 | Every core service, ~300-char descriptions using local keywords |
| Photos: ≥25 total, ≥3 added in last 30 days | 15 | Real job photos — exterior/team/at-work mix |
| Hours complete (incl. holiday hours) | 5 | — |
| Attributes set | 5 | Family-owned, onsite services, payment types, etc. |
| Q&A seeded (≥5 owner-posted) | 10 | Answer the questions prospects actually ask on calls |
| Booking/appointment link present | 10 | Points at the site's scheduling questionnaire |
| Website link UTM-tagged | 5 | `?utm_source=google&utm_medium=organic&utm_campaign=gbp-listing` |
| Description: 750 chars, keyword + city rich, no promo fluff | 5 | — |
| Posts: ≥1 in last 7 days | 10 | See cadence below |

Output `YYYY-MM-DD-gbp-audit-<profile>.md` with score, per-item pass/fail, and evidence. Below 70 = "needs work" in client-facing framing. This audit doubles as a retainer proof artifact and a sellable service — pricing is value-based; the operator sets the number.

## 2. Optimization actions — impact-ranked order
1. Fix the primary category (biggest single ranking lever)
2. Fill services + descriptions (feeds "provides: X" justifications in the map pack)
3. Photo backlog: batch 10-15 real job photos, then 3+/month steady
4. UTM-tag the website link (otherwise GBP traffic hides as "direct" in analytics)
5. Add the booking link → the site's scheduling questionnaire
6. Seed Q&A (owner asks + answers; mine questions from the client's actual customer calls)
7. Secondary categories, attributes, holiday hours
8. Start the post cadence (section 3)

Deliver as a checklist the operator or client works through in the GBP UI. *[automation: push via API when access exists.]*

## 3. Recurring GBP posts — 2/week per profile
One profile = one track; sibling businesses never share a post. Rotation:
- **Job showcase** (weekly): 1-2 real photos of that client's actual completed work + 2-3 sentences (what/where-ish/outcome) + a "Get a free quote" CTA on a UTM link (`utm_campaign=gbp-post`)
- **Offer / seasonal / FAQ-answer** (weekly, rotate): service spotlight, regional-weather angle, or an answered customer question

Hard rules:
- **Real photos only.** Source from the client's asset folders or photos the client sends. NEVER present stock or AI imagery as a completed job.
- **Regulated offers = gate.** Posts touching financing or other regulated claims need the operator's compliance sign-off; default is not to mention financing in GBP posts at all.
- No fabricated claims, locations, or customer quotes. City names only where the job actually was.

Output a month of drafts to `deliverables/local-seo/YYYY-MM-gbp-posts-<profile>.md` (post text + which photo file + CTA URL) for pasting into the UI. GBP-only — site-wide social content belongs to social-media-manager/content-calendar.

## 4. Citation / NAP consistency sweep
1. Confirm the canonical NAP (exact name, address format, phone) from the client record, or ask the operator. Never guess.
2. Web-search loop per directory: `"[business name]" [city]` and `"[phone number]"` against Google Maps, Apple Maps, Bing Places, Yelp, Facebook, BBB, Angi, HomeAdvisor, Houzz, Nextdoor, Yellowpages.com, Foursquare, MapQuest, and the local chamber of commerce. Also run a bare phone-number search to catch stragglers/duplicates.
3. Record per directory: listed? NAP exact-match? wrong/old data? duplicate listings?
4. Output `YYYY-MM-DD-nap-sweep-<slug>.md`: findings table + prioritized fix list (wrong phone > wrong address > name variants > missing listings) with the edit/claim URL for each. Fixes are manual claims/edits the operator or client submits.

## 5. Local rank tracking — no paid tools
- Query set per profile: 5-10 "[service] [city]" terms derived from the client's service and service-area pages
- Check via web search with the location modifier IN the query; record whether the client appears, roughly where, and who holds the top-3 map pack
- **Be honest about precision:** search results are not geolocated like a phone standing in the client's city, there is no geo-grid, and personalization makes single checks noisy. Treat results as directional trend data (present/absent, top-3 vs page-2), never exact positions — and say so in the deliverable.
- Log to `deliverables/local-seo/rank-log.md` (append a dated block per check; monthly cadence). If the operator needs defensible precision for a client report, flag that a real geo-grid tool is the upgrade path — a decision, not a silent workaround.

## 6. Review velocity
Reviews are a top-3 map-pack factor but NOT this skill's job. Route responses, request timing, and reputation reports to **review-manager**. In the audit, record only review count + rating + recency as scoring context and note "run review-manager" if velocity is weak.

## 7. Write-back (non-negotiable)
After every audit, sweep, post batch, or rank check: log an activity note in the client record (date + 1-2 sentence summary + deliverable path) and update the matching <TASK SYSTEM> task. Do the writes and verify the files/task actually changed — never claim writes that didn't happen.
