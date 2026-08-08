---
name: feedback_verify_before_shipped
description: A deploy is not "shipped" until the live page is re-fetched and diffed against what was intended. HTTP 200 is not proof.
type: feedback
---

# A deploy isn't shipped until the live page is re-fetched and diffed

**What happened (2026-06-18):** Told Alex the Canyon Roofing services-page update was
"live." The deploy had returned 200, but the CDN was serving the stale page — Dana opened
it on a call with a customer twenty minutes later and saw the old pricing-adjacent copy
the update was supposed to remove. Alex found out from the client. Cost: an embarrassed
apology call and a dent in "Alex tells us the truth."

**The rule:** "Shipped" is a claim about the user-facing surface, not about the deploy
pipeline. Until the live URL has been re-fetched and the relevant content diffed against
what was intended, the honest status is "deployed, awaiting verification" — say that
instead.

**Why:** Every hop between the write and the reader (build cache, CDN, wrong branch,
wrong site) can silently serve the old thing while returning success codes. A 200 proves
the server answered; it proves nothing about what it answered with. Alex repeats status
claims to clients verbatim, so an unverified "it's live" becomes Alex's false statement,
not just the agent's.

**How to apply:**
1. After any deploy, fetch the production URL (not the preview, not a cached tab).
2. Diff the fetched content against the intended change — the specific text or element,
   not just "page loads."
3. Only then report "shipped," and include what was verified ("re-fetched /services,
   confirmed the new copy is serving").
4. If verification fails or can't be run, say "deployed, not yet verified" — that is a
   normal status, not a failure.
