---
name: lead-flow-verifier
description: Fires marked test submissions through every lead entry point on a deployed site (forms, tel links, quiz funnels, booking, chat) and verifies the full chain — form-platform submission, notification email, <CRM> record, analytics events — as a PASS/FAIL/COULDN'T-VERIFY matrix. Triggers - "verify lead flow", "test the forms", "lead capture check". NOT pre-delivery QA — use site-qa-checklist.
---

# Lead Flow Verifier

Doctrine: the user-facing read surface is the only ship contract. A form that renders, a
200 on POST, or a dashboard saying "connected" proves nothing — a lead flow "works" only
when a real test submission is visible at every downstream step a human relies on.
**COULDN'T-VERIFY is a first-class result** — report it honestly, never round it up to PASS.

Corollary: **an empty read right after an async write is INCONCLUSIVE, never "failed."**
Form-platform APIs and notification pipelines lag by minutes. Confirm at the destination
(the notification inbox, the <CRM> record, the function log) — and symmetrically, a
2xx/"success" transport response proves nothing landed either.

Run this as a launch gate before declaring any client site live "with lead capture," and
re-run after any form, function, or DNS change. site-launch-cutover delegates its
post-launch form check here.

## Gate before firing anything

Test submissions trigger REAL notifications. If any land in the client's inbox, phone, or
<CRM> (not yours), tell the founder exactly which entry points will fire and where
notifications go, and **get a go-ahead first** — a mystery lead confuses the client.
Standard payload, always clearly marked:

- Name: `TEST — <YOUR BUSINESS> verification`
- Email: your own address — Phone: the founder's cell (confirm it, don't guess)
- Message: `TEST submission from <YOUR BUSINESS> verifying lead capture — please ignore, we will remove it.`

## Phase 1 — Inventory entry points (from the DEPLOYED site, not local source)

`curl -s` every page of the live URL (or crawl sitemap.xml) and grep for:

- Forms: `<form`, `data-netlify`, `action=`, honeypot fields, hidden `form-name` inputs
- Phone/email: `href="tel:` (dedupe numbers), `mailto:`
- Quiz/questionnaire funnels: multi-step JS — grep inline + linked JS for `fetch(`,
  `XMLHttpRequest`, or serverless-function paths to find the real submit endpoint
- Booking: Calendly/Cal.com/appointment iframes or links
- Chat widgets: third-party script tags

Diff the inventory against the local source repo. An entry point in source but missing
live = deploy drift; live but not in source = someone edited the wrong copy. List every
finding as a matrix row BEFORE testing any.

Intentionally-unwired demo/preview pages are an expected FAIL: record them as FAIL with a
"by design — real capture wires at launch" note. Flag, don't "fix," and don't count them
against a launch gate unless they ARE the launch surface.

## Phase 2 — Fire test submissions

1. **Pre-check form detection.** On Netlify:
   `netlify api listSiteForms --data '{"site_id":"<YOUR-SITE-ID>"}'` — an empty array
   plus POST→404 usually means HTML form processing is disabled at the platform level.
   That alone is a chain-step FAIL; fixing it means a config change + redeploy, which
   needs the founder's green-light.
2. **Submit like a real user:** headless browser (Playwright) — fill, pass client-side
   validation, click submit, and **record all network requests during submit** (Phase 3
   step 4 needs them). Fallback: `curl -X POST` with the form fields urlencoded — but a
   curl POST can't prove client-side validation or tracking fired, so those cells become
   COULDN'T-VERIFY, not PASS.
3. **Quiz funnels:** complete every step through the thank-you screen — and run skippable
   steps both skipped and filled. Partial-step abandonment is where quiz capture silently dies.
4. **tel:/mailto:** can't be fired programmatically. Verify the number/address matches
   the client's record and is consistent across all pages; the actual ring/delivery is
   COULDN'T-VERIFY unless the founder places a live call — offer that step.
5. **Booking calendars:** book a real test slot ONLY with explicit go-ahead (it lands on
   the client's calendar); cancel it in cleanup. **Chat widgets:** send one marked test
   message; where it routes is checked in Phase 3.

## Phase 3 — Verify the chain, per entry point

1. **Platform record:** list the form's submissions via the platform API (Netlify:
   `netlify api listFormSubmissions --data '{"form_id":"<FORM-ID>"}'`; WordPress:
   form-plugin entries via wp-cli/REST) — find the entry carrying the TEST marker and
   capture its ID for cleanup. Empty list right after submitting = wait and re-poll
   before judging (see the inconclusive-read corollary above).
2. **Notification delivery:** confirm a notification hook/recipient is configured
   (Netlify: `netlify api listHooksBySiteId --data '{"site_id":"<YOUR-SITE-ID>"}'`). No
   notification configured = FAIL — a submission nobody is emailed about is a dead lead.
   If the target is your inbox, confirm the email actually arrived. If it's the client's
   inbox, ask the founder (or the client on the next call) to confirm receipt — until
   then it is COULDN'T-VERIFY, not PASS.
3. **<CRM>/automation record:** ONLY for chains that claim one exists. Verify the record
   in the actual system — never trust the automation's own "success" response; some CRM
   endpoints return success while silently discarding fields, so read the created record
   and check the field CONTENT, not just its existence. No automation claimed → mark N/A;
   don't invent a step.
4. **Tracking fires on submit:** static grep first (analytics tag, ads pixel) — presence
   in source ≠ firing (a CSP can silently block a tag that greps clean). Proof is the
   Phase 2 network capture: a request to the analytics collect endpoint with the
   lead/conversion event, and to the ads-pixel endpoint with the configured event, during
   submission. No tag installed → FAIL only if the setup claims tracking; otherwise note
   "no tracking installed."

## Phase 4 — Verification matrix

Save to `clients/<slug>/deliverables/qa/lead-flow-verification-YYYY-MM-DD.md`
(`mkdir -p` first). One row per entry point; columns: Submitted OK · Platform record ·
Notification arrived · <CRM> record · Analytics event · Ads-pixel event · Cleanup done.
Cells: **PASS / FAIL / COULDN'T-VERIFY / N/A** — every FAIL and COULDN'T-VERIFY gets a
one-line reason plus what would resolve it. Header states the site, live URL, date, and
the payload marker used. Close with a blunt verdict: "lead capture is / is not
launch-ready" — never "shipped" off an HTTP 200.

## Phase 5 — Cleanup

- Delete each test submission via the platform API, then re-list to confirm it's gone —
  verify the delete too.
- Cancel test bookings; delete or flag any <CRM> test records the automation created;
  note in the matrix anything that couldn't be cleaned so the client can ignore it.
- If a notification landed in the client's inbox, have the founder flag it as a test.

## Write-back

Log an activity note on the client's workspace record (date, site, matrix verdict, path
to the matrix file) and update the matching <TASK SYSTEM> task before closing out.
