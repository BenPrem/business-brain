---
name: ai-demo-builder
description: Build working AI-automation demos tailored to a prospect's business to close automation sales — voice receptionist, review-request flow, lead follow-up bot, appointment reminders. Triggers - "build a demo for [prospect]", "AI demo", "automation demo", "voice receptionist demo", "review request demo". NOT for website builds — use website-builder.
---

# AI Automation Demo Builder

Don't explain what AI can do — show them. Build a working demo in the prospect's own
business context, let them interact with it live, then close. A demo they can call, text,
or submit to beats any slide deck.

## When NOT to use

- Website builds → `website-builder`
- Cold outreach copy → `cold-email`

## Stack (map each need to YOUR live tools before building)

| Need | Use |
|---|---|
| Scheduled or chat-triggered automation | Your always-on agent box (if you run one), or a scheduled cloud agent |
| Webhook endpoint / form handling / API proxy | Serverless function (keep the source dir OUTSIDE the publish dir; origin-check + rate-limit anything public) |
| SMS | Your SMS provider (e.g. Twilio) |
| Email sequence | Your email platform, or direct transactional send |
| AI generation inside a function | Your LLM router — validate model slugs against its live API first |
| Voice agent | A voice-AI platform (e.g. VAPI) + a provisioned phone number |

## Demo types

### 1. AI Voice Receptionist
The prospect calls a number and talks to an AI that knows their business and books appointments.
- Configure the voice agent with the business's name/hours/services/FAQ — scrape their
  site or ask the founder for the facts; never invent capabilities
- Call-event webhook → serverless function: create the calendar event, send a
  confirmation, log the call summary to the workspace + <TASK SYSTEM>
- Test 3 scenarios (hours question, booking, services list), screen-record, then share
  the number: "Call this."
- **Dependencies:** voice-platform account + phone number. Not buildable until those exist — say so upfront.

### 2. Automated Review Request Sequence
Job marked complete → the customer automatically gets a perfectly-timed review ask.
- Trigger: a message to your automation box or a webhook when a job completes
- Sequence: immediate thank-you text → 2h review request with the direct Google review
  link → 3-day gentle follow-up if no review yet
- SMS via your provider, email variant via your email platform; track
  asked/reviewed/response-rate in the workspace
- Demo: walk the sequence using their real business name, city, and actual review link

### 3. Lead Follow-Up Bot
Form submission → instant personalized AI response + owner notification within 60 seconds.
- Form → serverless function → LLM generates the personalized reply → email out
- Owner notification (chat/text/email): lead details, an urgency-signal lead score,
  suggested talking points
- Demo: a simple form page, submit a test inquiry live in front of them

### 4. Appointment Reminder System
Automated 24h (email + text) and 2h (text) reminders with confirm/reschedule replies;
cancellations ping the owner immediately.
- A scheduled job reads the calendar (calendar API or a manual list) and fires the sends
- **Dependencies:** calendar access + SMS provider

## Picking the demo

Choose by the prospect's loudest pain — missed calls / no reviews / slow follow-up /
no-shows. Rough vertical defaults (primary + secondary):
dental-medical → 4+1 · trades/contractors → 3+2 · restaurants → 1+2 · legal → 3+1 ·
real estate → 3+4 · auto repair → 2+4. Their actual complaint overrides the table.

## Delivery process

1. **Customize with their real data** — business name, hours, actual review link,
   industry language. This is what separates a demo from a pitch deck. Never fabricate
   reviews, stats, or capabilities the system doesn't have.
2. **Build** into `ventures/<automation-venture>/deliverables/demos/<prospect-slug>/<demo-type>/`
   (`mkdir -p`). Reusable vertical templates accumulate in `deliverables/demos/_templates/`
   — the second demo in any vertical should take 30 minutes, not 3 hours.
3. **Deploy** (if the demo needs hosting): get the founder's explicit green-light first,
   then deploy with your pinned site ID (`netlify deploy --prod --site "<YOUR-SITE-ID>"`
   or your host's equivalent). If a serverless function means the demo only works
   deployed, tell the founder BEFORE they try it locally and hit the error.
4. **Present** live (let them call the number / submit the form) or screen-recorded with narration.
5. **Close:** "That's this running 24/7 for [Business]. Setup takes about 1–2 weeks."
   Pricing is value-based and set by the founder per deal — never quote a number.
   → run `proposal-generator` for the formal proposal.
6. **Write-back:** after any prospect demo or conversation, log an activity note on the
   prospect's workspace record and update the matching <TASK SYSTEM> task/stage before closing out.

## Compliance gate

If a demo asset is client- or public-facing and touches a regulated topic (financing
offers, health claims, legal outcomes, insurance), run `regulated-copy-compliance`
against it before anyone outside the team sees it.
