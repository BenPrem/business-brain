# Learned Rules — Incident Archive

This file is the second tier of the two-tier learned-rules convention:

- **`.claude/rules/learned-rules.md`** holds the distilled rules — 1-3 imperative lines
  each, always loaded, cheap on context. That file stays lean forever.
- **This file** holds the full incident stories behind those rules — what happened, what
  it cost, and why the rule reads the way it does. It is read on demand, never auto-loaded.

Why keep the stories at all? A distilled rule tells the next reader *what* to do; the story
tells them *why it's load-bearing*, which is what stops a future session from "optimizing"
the rule away or arguing with it mid-task. When you add a rule to `learned-rules.md`, append
its story here in the same change. Bracketed numbers reference the public rule numbers.

Every story below is anonymized from real agency operations: mechanics and costs are real,
actors are generic.

---

## [15] The automation box that hallucinated finished work

An always-on automation agent (a headless box driving CRM updates, file hosting, and demo
deploys) repeatedly reported work as complete — CRM pages created, files uploaded, demos
live — that a filesystem and endpoint check showed had never happened. Nothing existed at
the claimed paths. The cost was hours of downstream planning built on phantom state, plus
the credibility of every future "done" from that agent. Hence: no automated work is
"complete" without filesystem or endpoint verification, no matter how confident the report.

## [16] Tuning a threshold until failing data looked like passing data

During eval calibration on a product build, measured data contradicted pre-set thresholds
and design assumptions several times in one session (confidence cutoffs, ground-truth
labels, latency bars). The tempting move each time was to nudge the threshold until the
miss became a hit. The distinction that survived review: correcting a pre-flagged ambiguous
ground-truth entry IS correction; changing a bar so a failure reads as success IS tuning.
Bars move only with documented rationale, surfaced for a decision — never silently.

## [19] + [33] Six weeks of HTTP 200s that shipped nothing

A push script for a children's-book client PATCHed email templates on the ESP and reported
"shipped" on every HTTP 200 — for six weeks. The client then reported the emails her
subscribers received had none of the changes. Investigation: the ESP's automation flows
were bound to auto-cloned copies of those templates, created when each flow was built; the
script had been updating a parallel set of standalone library templates that no flow
referenced. Every push succeeded; nothing a subscriber saw ever changed. The client nearly
fired the agency over it. The rule this produced is the house's most load-bearing: the
platform's write endpoint is the input contract, the user-facing read endpoint is the
output contract, and only the output counts as shipped — discover the binding first, then
push, re-GET, diff, and preview on the real surface. A footnote worth keeping: the ESP's
"flow content is read-only via API" limitation found that day expired six weeks later when
the vendor shipped a new endpoint — date-stamp API-limitation findings and re-check the
changelog before repeating "impossible."

## [20] The safety gate that failed 100% of the time

A site generator's palette validator checked contrast pairs against a dark-background CSS
variable that was declared but never actually painted anywhere in the rendered output.
Those phantom pairs were unsatisfiable for any real palette, so the corrector failed on
every run and a fallback preset fired 100% of the time — twenty live sites shipped with
only two distinct colors between them, and the "safety" gate was the cause. When a gate
trips at ~100%, suspect the gate: grep the consumer and confirm every checked condition
corresponds to something that actually ships.

## [22] "Connected, 41 tools" — with a placeholder for a token

An MCP server on a headless agent reported "connected, 41 tools discovered" while its
API token was still the literal string `PASTE_YOUR_PAT`. Tool discovery is static — the
server advertises its schema regardless of credentials — so the integration was declared
working and only failed later, mid-task, on the first real API call. Done = a tool call
returning real, recognizable data. And because copy-paste placeholders get pasted
literally more often than you'd think, grep the saved config for surviving placeholder
strings before testing.

## [23] Calling a client's testimonials fake on style alone

A contractor client's testimonial page had initial-only surnames, polished prose, and
cities matching the SEO target list — and the report called the testimonials *fabricated*,
framing it as fake-review legal exposure. The owner pushed back: there was zero evidence,
only stylistic inference; the quotes plausibly came from social media, email, or the
client's own records. The real, defensible finding — "the page claims authenticity I can't
substantiate; here's what would settle it" — got buried under an accusation about a paying
client's conduct. "Couldn't verify" is not "is false." Separate the observation from the
conclusion, and when the subject is the client's own conduct, default to the question.

## [24] Declaring a test failed off an API that hadn't caught up

Three test leads were fired through a live site; ~12 seconds later the host's submissions
API returned nothing, and the QA run was reported as failed. The owner had already
received the auto-reply confirmations — which only send after verification checks and the
CRM push — so the pipeline had worked the whole time; the listing API simply lags by
minutes. Several tool calls were then burned diagnosing a phantom. The same session held
the mirror-image lesson: the client's CRM endpoint returned `"success"` for a field it
silently discards, so for a month every lead arrived with no detail attached. An empty
read right after an async write is inconclusive, and a 2xx proves nothing landed — confirm
at the destination, in both directions.

## [25] Obeying a reviewer subagent over a verified conclusion

A compliance scan had correctly cleared a "we offer financing — ask about your options"
banner under the client's standing policy (generic financing language allowed; the lender
never named). A reviewer subagent then flagged it as a blocker, citing a real clause from
the real lender ruleset — and the banner was stripped from client-facing pages without
pushback. The owner reversed it: the cited clause governed lender-branded assets only, and
the original analysis had been right. The finding was persuasive precisely because it
quoted something real — which is exactly why it needed adjudicating, not obeying. A
subagent's finding is input: prove it, refute it in writing, or escalate — never silently
adopt the stricter reading because it feels safer.

## [26] The dead plan that kept resurrecting from a state file

Early in an ad-campaign build, a fallback plan ("leads land in the ad platform's inbox;
enter them into the CRM manually twice a day") was written into an always-loaded context
file as if it were the live state. The plan died before launch — the ads pointed at the
client's own landing page and leads rode the normal automated funnel — but the correction
landed only in a dated research doc. The always-loaded file kept asserting the dead plan
to the owner session after session for two more weeks. State files and memory carry only
what's verified running; when a decision reverses, the reversal must propagate to the
always-loaded files in the SAME change.

## [27] Labeling a file "the set we already printed" — it was never printed

While tidying a design file of print artboards for a contractor client, a row of earlier
designs got a helpful label: "the set we already printed." Those hangers had never been
printed — print-ready PDFs existed, so "printed" got inferred. Worse, the label was
written onto the client's own working file, where it became *their* record too. Artifact
existence is not artifact status: built ≠ launched, scheduled ≠ published, print-ready ≠
printed. And don't add unrequested titles or chrome to a working file — name the artboards
and stop.

## [28] The small model that was 90% confident and 87% wrong

In an escalation-routing smoke test, a small open-weights model reported 0.90 confidence
on seven of its eight wrong answers. Any escalation logic keyed on self-reported
confidence would have routed almost every error straight past review. Self-reported
confidence from small models does not correlate with correctness — build escalation on
agreement between calls, logprobs, content patterns, or a larger primary model instead.

## [29] Nine deploy cycles on one character card

A single character card for a children's-book client burned nine deploy cycles: wrong
character image entirely, then a tiny figure dwarfed by furniture, then a cropped head on
a clashing background, and on — each retry a new guess, each "fixed" version disputed by
the owner, who was right every time (the deployed asset, viewed fresh in its real context,
is ground truth over any local render). The fix that finally worked was a three-minute
diagnostic — alpha-channel column-density analysis to find the true crop boundary — which
had been available at retry one. Retry #3 on the same asset is a process failure: stop
retrying, switch to measurement.

## [35] The CSP that silently swallowed two tracking scripts

A client site with a strict Content-Security-Policy got an analytics tag deployed —
silently blocked, because the tag's domains weren't in `script-src`. Two weeks later the
identical failure recurred on the same site with an ad pixel: HTML greps looked perfect,
but the header check showed the pixel's domain missing, meaning ad spend would have
optimized against zero conversion events. CSP blocks are silent. Any third-party script
ships WITH its `script-src` entry in the same change, and verification is browser-level —
script returns 200 and the runtime object exists — never a grep of the served HTML.

## [36] The serverless function served as a static file

A demo deploy put the functions directory inside the publish directory, so the host served
the function source as a static asset — full source, including system prompts and the
origin-check logic, publicly downloadable for about two hours before an audit caught it.
The invocation endpoint worked perfectly the whole time, which is why nothing looked
wrong. Function source lives OUTSIDE the publish root, and every deploy ends with a
negative check: curl the source file's public path and confirm it 404s.

## [41] + [43] The slug that didn't exist, and the stack that broke overnight

Two provider lessons from the same season. First: a model slug was wired into a serverless
function from memory; the provider's naming didn't follow the assumed convention and the
slug didn't exist — validate every model ID against the live API before building on it.
Second: a provider policy change broke a third-party orchestration framework overnight,
taking the automation stack with it. Never monoculture: keep ~30% of the workload runnable
on alternative models/providers, and own the stack you depend on.

## [46] The client's plan named seven dead funders

A demo build for a nonprofit in an unfamiliar vertical started from the client's own
AI-generated plan. Parallel research agents (competitor teardown + funder/domain
landscape) run before design found that seven of the funders the plan named were
unusable — wrong geography, sunset programs, invite-only, category exclusions. Building to
the plan as delivered would have wasted a week of applications. Client-provided plans
often carry dead assumptions; in an unfamiliar vertical, research runs before design,
every time.

## [47] The luxury hotel that shipped as a "rest cabin"

A site build sourced stock photos by search-result ID without opening them. What shipped:
a famous luxury hotel interior captioned as a rustic rest-cabin interior, and a gym
sit-ups shot captioned as a young person chopping wood. The pattern that fixed it costs
seconds: download the image, view it, then commit the URL. A photo you haven't looked at
is a photo you haven't verified.

## [50] The rotation that made the photo more crooked

The owner flagged a hero photo as "slightly crooked." Line analysis folded all
near-horizontal and near-vertical lines into one median tilt, and the photo was rotated by
it — making it visibly worse. Measured separately afterward, horizontals and verticals
disagreed by over 2°: the photo was keystoned (shot from below and to one side), so no
rotation could level one axis without tipping the other — and warping a real install photo
fabricates the geometry of a house the client actually worked on. Of six available photos,
one was already square; the answer was selection, not correction. Collateral lesson: the
same wrong-signed rotation had been silently applied to two sibling photos nobody flagged,
one of which had been perfectly plumb — a user reporting one instance of a systematic bug
does not bound the bug; audit every sibling asset.
