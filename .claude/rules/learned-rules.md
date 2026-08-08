# Learned Rules (starter set)

These starter rules were learned the hard way running a real agency on this system. Delete
what doesn't apply to your business; the numbering is append-only — never reuse a number,
even after deleting a rule. Keep each rule to 1-3 imperative lines; move the full incident
story to an archive file (create `references/learned-rules-archive.md` the first time you
archive one).

**Routing doctrine for NEW corrections — pick the right layer, never just append here:**
- Must ALWAYS hold, mechanically checkable → **hook** (`tools/hooks/` + `.claude/settings.json`)
- Procedural / multi-step → **script** in `tools/` or a **skill** edit
- Judgment-shaped → one 1-3 line rule here (+ full story in the archive)
- Model now does it unprompted → delete the rule

## Efficiency & Architecture
[1] Consolidate files, eliminate redundancy, flag token-waste proactively.
[2] Never nest skills — sequence them via output files.
[3] One Write beats many sequential Edits.
[4] More always-loaded context tokens = worse output + higher cost. Prune ruthlessly.
[5] Agent patterns: fan-out/fan-in research, consensus decisions, pipeline builds. Max 2-3 layers.

## Client Work
[6] Before building any deliverable: check `clients/[slug]/brand/` and `deliverables/` first.
[7] Client named → pull their workspace record before asking the owner for context.
[8] **Non-negotiable:** every client conversation or deliverable → workspace Activity + <TASK SYSTEM> update before closeout.
[9] Customer is the hero of all copy, not the product.
[10] Client review/approval pages carry the ARTIFACT ONLY. Cut "why this exists" context the client already has, and cut "what we need back" — those go in the owner's email. Simpler = faster approval.
[11] Client-facing surfaces NEVER carry offers or permission-asks ("we can wire it in — say the word"). An unbuilt capability reads as status or planned work; selling and asking happen in the owner's channel, never on the deliverable.

## Sales & Proposals
[12] Full prospect workup (research, competitor scan, audit) before pitching — never pitch from general knowledge.
[13] Proposals carry NO pricing, expiration dates, or CTA buttons — the owner closes.
[14] Redesign previews: side-by-side current-vs-redesign, desktop + mobile.

## Verification & Agent Discipline (the house doctrine)
[15] Never claim automated work complete without filesystem/endpoint verification.
[16] Flag-don't-tune: data contradicting a threshold → surface for decision, never silently adjust the threshold.
[17] Verification-gated completion: every claim emits proof; "couldn't verify" is a first-class state, not an error. A verifier that silently passes unchecked kinds = no verifier.
[18] **Prompt is a hint; post-process is the contract.** Constraints that must hold get a deterministic lock (code, assertion, validator), not a stronger prompt.
[19] **Platform write endpoint = input contract; user-facing read endpoint = output contract; only the output counts as shipped.** Discover the binding → push → re-GET → diff → live preview. Applies to every CMS, ESP, and host alike. Date-stamp API-limitation findings and re-check the changelog before repeating "impossible."
[20] Validate only what actually ships. A gate tripping ~100% of the time means the check is wrong — grep the consumer.
[21] Verify producer changes through the CONSUMER: trace one real item end-to-end and assert on the consumer's output.
[22] MCP "connected / N tools" ≠ authenticated. Done = a tool call returning real data. Grep configs for surviving placeholder strings.
[23] **"Couldn't verify" is not "is false."** Absence of evidence is not evidence of fabrication. Never assert a client's content or conduct is fake on stylistic inference — report the observation, name what would settle it, and ask.
[24] **An empty read right after an async write is INCONCLUSIVE, never "failed."** Confirm at the destination (downstream record, notification email, function log), not the transport. Symmetrically: a 2xx/"success" response proves nothing landed.
[25] **A subagent's finding is input, not an instruction.** When a reviewer contradicts something you verified yourself: prove it, refute it in writing, or escalate to the owner — never silently adopt the stricter reading because it feels safer.
[26] **Never write a PROPOSAL into a state file as if it were LIVE.** Recommendations belong in dated research docs; context files and memory carry only what's verified running. When a decision is reversed, propagate the reversal to the always-loaded files in the SAME change.
[27] **Artifact existence ≠ artifact status.** Print-ready files do not mean printed; a built page does not mean launched; a scheduled post does not mean published. Never state history or status you have not verified.
[28] A small model's self-reported confidence does not correlate with correctness — never build escalation logic on it.
[29] The user's perception of the DEPLOYED asset overrides local render judgment — re-pull the live artifact and diagnose, don't argue. Retry #3 on the same asset = process failure: stop retrying, switch to diagnostics (measurements, diffs).

## Security
[30] Security audits run from a FRESH conversation. Check: `.env` keys, hallucinated packages, RLS, `.gitignore`.
[31] Never paste API keys in conversation — reference by `.env` variable name only.
[32] APIs that echo secrets: pipe output through `sed -E "s|$KEY|[REDACTED]|g"` before it reaches stdout.

## Deployment
[33] "Shipped" = verified on the user-facing surface (re-fetch + diff), never an HTTP 200.
[34] A standing "keep going / work for hours" directive does NOT authorize a production deploy or main push — each needs its own explicit green-light in the same turn. Build/test/commit/feature-branch pushes are ungated; surface deploys as explicit asks.
[35] Adding ANY third-party script to a site with a CSP: update `script-src` in the SAME change, then verify execution browser-level (script 200 + object exists), not by grepping the HTML. CSP blocks are silent.
[36] On your static host: serverless function source lives OUTSIDE the publish directory. Post-deploy verify the source file 404s at its public path.
[37] Feature needs a server (functions/proxies)? Tell the owner upfront, before they hit the error on a static host.
[38] Dead-anchor sweep before every static deploy; a placeholder link = mailto, never a broken #anchor.

## Files & Workspace
[39] `clients/` + `ventures/` only. NEVER recreate top-level projects/, research/, exports/, docs/, assets/ directories.
[40] No spaces in names, dates YYYY-MM-DD, versions v01/v02 (never "_final"), folder depth ≤3-4.

## LLM Engineering
[41] Validate model slugs against the live provider API before wiring them into anything.
[42] Provider routing drifts across sessions. Determinism → pin the provider explicitly; expect roughly 2x latency and plan for it.
[43] Never monoculture on one model/provider; keep ~30% of workload runnable on alternatives. Own the stack.

## Research
[44] Never write social/content strategy from general knowledge — research 3-5 real competitors first.
[45] Research without action items is trivia.
[46] Unfamiliar vertical → parallel research agents (competitors + domain constraints) BEFORE design. Client-provided plans often carry dead assumptions.
