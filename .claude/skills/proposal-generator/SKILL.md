---
name: proposal-generator
description: Generate a branded HTML client proposal using StoryBrand structure and a two-phase offer (foundation project + ongoing retainer). Trigger on "create a proposal", "write a proposal for [client]", "quote", "scope of work", or "SOW". Proposals carry NO pricing, expiration dates, or CTA buttons — the founder closes. For cold outreach, use cold-email.
---

# Proposal Generator

Discovery call → branded HTML proposal → ready for the founder's close, in one session.

## Routing

- Cold outreach copy → **cold-email**
- Pre-call research → **discovery-call-prep**
- General website builds → your website-builder skill

---

## The non-negotiable rule

**Proposals never include pricing, expiration dates, or CTA/payment/signature
buttons. The founder handles the close.** No dollar amounts, no "sign below", no
"Pay & Get Started", no deadlines. Rationale: pricing is value-based and set per deal
in a live conversation — a number on a page anchors low and closes doors. The only
exception is an explicit founder override in the current session, and even then the
founder supplies every number.

---

## Step 1 — Gather inputs

Ask for anything not already in the workspace records, <TASK SYSTEM>, or a call
transcript:

1. **Client name and business**
2. **Discovery call notes** — problems they shared, goals stated, their exact words
3. **Services to propose** — website build, redesign, social, email, strategy,
   automation
4. **Timeline expectations**
5. **Special requests or concerns raised on the call**

Check `clients/[client-slug]/deliverables/notes/` for discovery briefs or call notes.

---

## Step 2 — StoryBrand structure

The proposal is a StoryBrand document (Donald Miller's framework):

- **Hero:** the client — their business, their team, their customers
- **Problem:** what is broken or missing in their presence/pipeline
- **Guide:** <YOUR BUSINESS> — empathy ("we get it") + authority ("here's what we've
  done")
- **Plan:** clear phases with deliverables
- **Stakes:** what happens if they don't act — subtle, never fear-mongering
- **Success:** what their business looks like after

The proposal's next step is a conversation with the founder — never a signature or a
payment.

---

## Step 3 — Write the sections

**1 — The Problem** (one paragraph). Name their specific challenge using THEIR words
from the call. Show you listened.

**2 — The Vision** (one paragraph). What success looks like, concretely: more calls,
more booked jobs, a site they're proud to share, showing up on Google and AI search.

**3 — The Plan.** Two-phase structure:

- **Phase 1: Foundation** (one-time project) — specific deliverables ("5-page
  responsive website", not "website"), timeline (typically 2-4 weeks), and explicit
  included-vs-not (stock photography, ads budget, domain, hosting) so there are no
  surprises.
- **Phase 2: Ongoing Management** (monthly retainer — include only if relevant) —
  what is covered each month, reporting cadence (monthly report, weekly check-in).
  One-time engagement → skip Phase 2.

Scope only. No dollar amounts anywhere.

**4 — Why <YOUR BUSINESS>** (3-4 bullets max). Local/vertical expertise, a proven
messaging framework (demonstrate it — don't name-drop "StoryBrand" to the client),
and real results only. **Never fabricate case studies, client counts, or numbers** —
an honest short section beats an impressive invented one.

**5 — Next Steps.** (1) The founder follows up to walk through the plan and
investment. (2) Kickoff call within 48 hours of go-ahead. (3) First deliverable ready
by [date]. No signature block, no payment link, no expiration date.

---

## Step 4 — Build as HTML

Single-file HTML proposal page:

- Read your own brand file (`ventures/<your-venture>/brand/brand.md` or equivalent)
  for colors and fonts
- Clean, professional layout — not a Word-doc feel
- Mobile-responsive (clients read proposals on their phones)
- Your logo in the header, client name prominent

Save to `clients/[client-slug]/deliverables/proposal/index.html`.

**Visual QA before handoff:** serve locally (`node tools/serve.mjs` or
`python3 -m http.server`), screenshot with `tools/shot.py`, and Read the screenshot —
never hand off a page you haven't seen rendered.

**Deploy** only with the founder's explicit green-light, to a URL named
`[client-slug]-proposal`. **PDF version** only if asked (headless Chrome
`--print-to-pdf`).

---

## Step 5 — Update records

- Log a proposal activity note in the workspace CRM
- Move the <TASK SYSTEM> deal card to "Proposal Sent" with the proposal path/URL and
  a follow-up due 3 days out
- Verify both writes landed (re-read the note, re-list the task) before reporting done

The **follow-up-nurture** skill owns the 3/7/14-day cadence from here.

---

## Step 6 — Report

```
Proposal Generated: [client]
============================
HTML: clients/[client-slug]/deliverables/proposal/index.html
Live URL: [if a deploy was approved]
Phase 1: [scope summary]
Phase 2: [scope summary or "none"]
Records: activity logged + task moved to Proposal Sent, follow-up [date]

Next: the founder reviews, prices it, and sends it — pricing happens in the close,
not in this document.
```
