---
name: site-launch-cutover
description: Go-live runbook for taking a built static site from a hosting preview to production on a real domain — pre-cutover audit, DNS/registrar steps, verified cutover sequence, rollback plan, post-launch checks. Triggers on "go live", "launch the site", "cutover", "point the domain", "connect the domain". NOT for pre-delivery QA of the site itself — use site-qa-checklist first.
---

# Site Launch Cutover

Runbook for moving a finished static site from `<slug>-preview.netlify.app` (or equivalent) to production on the client's real domain. site-qa-checklist must already have passed — this skill assumes the site content is done.

## HARD GATE (first, always)
**No DNS change, no `--prod` deploy to the production site, no registrar action without the operator's explicit green-light IN THIS SESSION.** A standing "keep going" from earlier does not count. Present the plan, wait for "go". If any launched page carries regulated claims (financing, medical, legal), confirm the operator's compliance sign-off before cutover.

## Phase 1 — Pre-cutover audit (before touching DNS)

Run against the preview URL. All must pass:

1. **Dead anchors:** grep the publish dir for `href="#..."` and verify each target `id=` exists in the DOM. Missing section → `mailto:` placeholder, never a dead link.
2. **Forms detection:** new Netlify sites default `processing_settings.ignore_html_forms: true` — `<form data-netlify="true">` fails silently (POST → 404, form list empty). Flip it:
   `netlify api updateSite --data '{"site_id":"<SITE_ID>","body":{"processing_settings":{"ignore_html_forms":false}}}'`
3. **Function source exposure:** the functions dir must be a SIBLING of the publish dir; netlify.toml drives `publish`/`functions`; deploy with `cd <toml-root> && netlify deploy --prod --site "$SITE_ID"` — never `--dir` (it overrides the toml), never link/state files (the deploy-guard hook enforces this). Verify: `curl -sI <url>/functions/<name>.js` and `/netlify/functions/<name>.js` → **404**; `/.netlify/functions/<name>` → works.
4. **Security headers:** netlify.toml has HSTS, X-Frame-Options SAMEORIGIN, nosniff, Referrer-Policy, Permissions-Policy. Confirm with `curl -sI` on the preview.
5. **CDN cache header:** HTML paths carry `Netlify-CDN-Cache-Control = "public, max-age=0, must-revalidate"` alongside browser Cache-Control, or post-launch edits will serve stale for minutes.
6. **De-index removal — this is launch, reverse the pre-launch lockdown:** delete `Disallow: /` from robots.txt (replace with allow-all + a `Sitemap:` line), remove site-wide `X-Robots-Tag: noindex` headers and `<meta name="robots" content="noindex">` tags. Keep noindex ONLY on genuinely private paths (portals, thank-you pages). Grep, don't trust memory: `grep -rn "noindex\|Disallow" site/ netlify.toml`.
7. **Head hygiene:** every page has `<title>`, meta description, canonical pointing at the FINAL domain (not the preview URL), favicon, `og:title/description/image` (og:image absolute on the final domain). Grep for leftover `netlify.app` absolute URLs in the HTML.
8. **Function env vars** exist on the production site, and any Origin/Referer whitelist in functions includes the production domain — a whitelist still pinned to the preview URL will 403 every visitor after cutover.

## Phase 2 — DNS prep (safe before the gate; changes nothing visible)

1. **Inventory the existing zone FIRST.** `dig +short` for A/CNAME/MX/TXT on apex, www, and mail selectors; save the full record set to `clients/<slug>/deliverables/launch/dns-snapshot-YYYY-MM-DD.md` (`mkdir -p`). Client email (MX/SPF/DKIM) must survive the move — copy every record, not just A/CNAME. A zone that lives at a losing registrar goes dark without this snapshot.
2. **Pick the DNS home:** (a) the host's DNS (delegate nameservers — easiest apex handling), or (b) keep DNS at the registrar with `A/ALIAS` apex → the host's load balancer + `CNAME www` → `<site>.netlify.app`. Use whatever the registrar supports for apex (ALIAS/ANAME/flattened CNAME); a plain A record to the host's published IP is the fallback.
3. **Drop TTLs to 300s** on the records you'll change, at least an hour before cutover — makes rollback near-instant.
4. Add the custom domain (apex + www, one as primary with a 301 from the other) to the hosting site so it answers for the hostname before DNS points at it.

## Phase 3 — Cutover (only after the green-light)

Execute one step, verify, then the next — never fire-and-forget:

1. Flip DNS (nameservers or A/CNAME per the Phase 2 choice).
2. **Verify resolution:** `dig +short <apex>` and `dig +short www.<domain>` return the host's targets; check a second resolver (`@1.1.1.1`, `@8.8.8.8`) to gauge propagation.
3. **HTTPS cert:** the host auto-provisions after DNS verifies; confirm with `curl -svI https://<domain> 2>&1 | grep -i "subject\|expire"`. Both apex and www must serve valid TLS; the non-primary must 301 to primary.
4. **Cache reality check:** `curl -sI https://<domain>/` → expect fresh content or revalidation, NOT `hit` with a high `age` of old bytes. If stale: `netlify api purgeCache --data '{"body":{"site_id":"<SITE_ID>"}}'`.
5. **Content diff:** fetch the live homepage and diff a marker string against the local source. An HTTP 200 on the deploy is the write endpoint; only the user-facing read surface counts as shipped.
6. **Form test end-to-end:** submit a real test entry on the LIVE domain → confirm it appears in the form backend AND any notification email/webhook fires. A form that renders but drops submissions is a failed launch. (An empty API read minutes after submission is inconclusive, not a failure — confirm at the destination: the notification email or CRM record.)
7. **Email survival:** `dig +short MX <domain>` unchanged from the snapshot; send a probe email to the client's address and confirm receipt.
8. **Function smoke:** hit each production function endpoint once with a real payload; re-run the Phase 1 source-exposure 404 check on the live domain.

## Rollback plan (write it down BEFORE Phase 3)

- DNS-level: restore the snapshot records / revert nameservers — with 300s TTLs this lands in minutes. The old host keeps serving as long as it isn't cancelled, so **do not cancel old hosting/registrar service until 72h of clean production traffic**.
- Site-level: roll back to the last known-good deploy in the host's UI (or `netlify rollback --site "$SITE_ID"`) for bad-content problems that aren't DNS.
- Cert won't provision (usually CAA records or slow propagation): check `dig CAA <domain>`, wait out propagation — do NOT thrash DNS back and forth.

## Phase 4 — Post-launch (same day)

1. **Google Business Profile:** update the website link (and appointment link if used) to the new domain.
2. **Analytics firing:** load the live site and confirm the analytics/pixel tag fires (network tab or realtime report) — a tag pinned to the preview hostname silently drops all data. If the site has a CSP, confirm the tag's host is in `script-src` and verify execution browser-level, not by grepping the HTML — CSP blocks are silent.
3. **Search Console:** add + verify the domain property (DNS TXT), submit `sitemap.xml`, request indexing on the homepage.
4. Grep the live site once more for surviving `*-preview` links; rename/repurpose the preview site so nobody keeps editing the wrong one.
5. Old-platform teardown list: cancel old hosting after 72h, transfer-lock the domain, confirm billing on the hosting plan.

## Write-back
Log the launch on the client record (date, domain, DNS home, verification results, rollback window) and update the matching <TASK SYSTEM> launch task before closing out.
