---
name: regulated-copy-compliance
description: Pre-publish compliance scan for any client asset touching a regulated topic — financing, health claims, legal services, insurance. Maintains a per-client ruleset (trigger terms, prohibited phrases, required disclosures), scans files/folders/URLs, and outputs PASS/FAIL with file:line citations. Triggers - "compliance check", "compliance scan", "can we say this", any client asset that mentions a regulated topic. NOT general site QA — use site-qa-checklist.
---

# Regulated Copy Compliance

Pre-publish scan for client assets that touch a regulated topic. Fires on ANY asset —
website, landing page, ad, email, SMS, social post, graphic, video script, flyer, sign,
radio/TV spot, in-home sales material — that mentions or implies the regulated subject.
Enforcement is the agent's job: the client will not remember these rules mid-campaign,
and the founder should not have to. The scan catches it before anyone sees it.

## The per-client ruleset (the binding document)

Every client with regulated exposure gets `clients/<slug>/compliance/ruleset.md`.
**Read it fresh at the start of every scan — never work from memory of it.** No ruleset
yet → build one first (see "Building a ruleset" below), get the founder's sign-off, then scan.

A ruleset carries six sections:
1. **Governing sources** — the actual program guide, ad policy, or regulation the rules
   derive from (link or archived copy). Every rule below cites one.
2. **Trigger terms** — phrases/patterns that, once used, escalate disclosure requirements
   (e.g. in consumer-credit advertising: any rate, term length, or payment amount).
3. **Prohibited phrases** — the hard DON'T list. Any hit is a FAIL regardless of context.
4. **Required elements when the regulated program/partner IS named** — verbatim
   disclosures, marks, logos, conspicuousness rules. Paraphrase = FAIL.
5. **Standing policy** — the client's chosen posture (usually: generic language only in
   public media; the branded path reserved for approved sales material).
6. **Compliance contact** — the named human whose WRITTEN approval clears branded assets.

## Inputs

A file, a folder, or a URL. For URLs: `curl -sL <url> -o <scratch>/scan-<slug>.html` and
scan the fetched file — the deployed page is ground truth; prefer it over local source
when both exist. For folders, scan `*.html *.md *.txt *.json` recursively. For video or
graphics, extract the transcript and on-screen text first (video-analyzer), then scan those.

## Scan procedure (all greps `-inE`, case-insensitive, line-numbered)

**Step 0 — topic detection.** Grep for the ruleset's topic-detection pattern (e.g. for
financing: `financ|apr|loan|credit|per month|/mo|payment plan|monthly payment` plus the
partner's name). No hits → report "no regulated content detected — scan not applicable" and stop.

**Step 1 — trigger terms.** Grep every pattern in ruleset §2. Any hit means the matching
required-disclosure obligation from §4 now applies to this asset — record which.

**Step 2 — prohibited phrases.** Grep every entry in ruleset §3. Each hit = FAIL with the
exact offending string and `file:line`.

**Step 3 — interactive claim tools.** Calculators, estimators, sliders, quizzes that
output a regulated figure (a payment amount, a health outcome, a settlement estimate):
grep `calculat|estimat(e|or)` near the topic, plus `<input type="range">` / JS that
computes the figure. Most program guides ban these outright — default FAIL unless the
ruleset explicitly permits them.

**Step 4 — required elements (only when the program/partner is named).** Check every §4
item: correct name with ® mark where required, verbatim disclosure fingerprint (grep a
distinctive substring of the exact required text — a paraphrase won't match, which is the
point), "subject to approval"-type qualifiers wherever terms appear, required logos
(check text, alt attributes, and image filenames), localized disclosures on translated
pages. Conspicuousness rules (disclosure near the claim, readable size, contrasting, not
hidden in a modal) can't be grepped — render/screenshot the page and check by eye.

## Worked example — financing-partner branding

The most common ruleset shape for home-services clients with a third-party financing partner:

- **Standing policy:** the lending partner is NEVER named in public-facing media. Public
  assets use generic language only — "Financing available", "Ask us about financing
  options." A public asset that names the lender is a policy FAIL even if its disclosures
  are technically complete.
- **Trigger terms** (from consumer-credit advertising rules): any specific rate or APR,
  any term length or number of payments, any monthly-payment dollar amount, down-payment
  claims, deferred-interest headlines ("no interest until…"). One hit requires the full
  plan disclosure on the SAME asset, using partner-supplied plan numbers — hand-filled
  numbers = FAIL.
- **Prohibited phrases:** "no credit check", "guaranteed approval", "pre-approved",
  "same as cash", "easy financing", "as low as", standalone "0%" / "no interest" without
  its qualifying condition, false-urgency promo deadlines that don't really expire.
- **Calculators:** payment estimators on the client's site are banned — any hit = FAIL.
- **Branded path** (approved sales material, or if the client reverses the standing
  policy): partner named correctly with its mark, "subject to credit approval" wherever
  plans appear, the program's verbatim disclosure block, required lender logos, and the
  compliance contact's written approval on file. Until that approval exists, the only
  correct status is **"drafted, pending compliance approval"** — never "done" or "live".

Adapt the same skeleton for health claims (substantiation, before/after imagery, FTC
guidance), legal services (state bar advertising rules: "specialist" claims, outcome
guarantees, required disclaimers), and insurance (state-level ad rules, licensing lines).

## Output — the report

Write to `clients/<slug>/compliance/scans/YYYY-MM-DD-<asset-slug>.md` (`mkdir -p` the
`scans/` dir first) and summarize in chat. One row per ruleset checklist item →
**PASS / FAIL / N/A**, every FAIL with `file:line` and the exact offending string. Then
an overall verdict:

- **PASS (generic path):** topic mentioned in generic terms only, no partner named, zero
  trigger terms, no banned tools — compliant by construction under the standing policy.
- **FAIL:** any Step 1–3 hit or missing Step 4 element. List the minimum edits that reach
  the generic-safe path.
- **BLOCKED ON APPROVAL:** asset names the partner/program and is otherwise clean —
  status stays "drafted, pending compliance approval" until written sign-off exists.

**When unsure whether a phrase is a trigger term: treat it as non-compliant and say so.**
Default to the safe side and route the question to the client's compliance contact via
the founder — never resolve regulatory ambiguity by yourself.

## Hook wiring (make the gate mechanical)

`tools/hooks/deploy-guard.sh` carries a commented client-specific compliance-gate example:
it blocks any deploy for a named client unless a scan report newer than 24h exists in
`clients/<slug>/compliance/scans/`. When a client's ruleset goes live, uncomment and adapt
that block — a gate that depends on remembering to run it is not a gate.

## Building a ruleset for a new client/topic

1. Get the governing documents (partner program guide, platform ad policy, statute/agency
   guidance) — from the client, the partner rep, or primary-source research. Never draft
   rules from general knowledge alone.
2. Extract trigger terms, prohibitions, and required disclosures into the six-section
   format, each rule citing its source section.
3. Have the founder confirm the standing policy and the compliance contact with the client.
4. Commit the ruleset, then wire the hook gate.

## Invocation from other skills

website-builder, site-qa-checklist, social and email skills, proposal-generator — any
skill producing client-facing media for a client that has a ruleset MUST run this scan
whenever the regulated topic appears in the asset. Don't wait to be asked; the gate fires automatically.

## Write-back

After any scan that blocks or clears a deliverable: log an activity note on the client's
workspace record (date, asset, verdict, blocking items) and update the matching
<TASK SYSTEM> task with the verdict.
