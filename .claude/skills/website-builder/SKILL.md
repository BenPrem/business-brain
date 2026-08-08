---
name: website-builder
description: Standard website builder for service businesses and lead-gen sites — clean, fast static HTML/CSS with Tailwind, StoryBrand-structured copy, and prominent call/schedule CTAs. Use for HVAC, plumbing, contractors, dental, legal, restaurants, real estate — any business where the site is a conversion tool, not a brand experience. Triggers on "build a site", "landing page", "website for <CLIENT>", "redesign their site". NOT for pre-delivery QA — use site-qa-checklist.
---

# Website Builder

Read this entire file before writing a single line of HTML or CSS.

**Scope:** conversion-first static sites for service businesses. The visitor is on a phone, mid-task, deciding who to call. Speed and clarity beat aesthetics. If the operator asks for scroll animations, 3D, or an immersive brand experience, say so — that is a different kind of build with different tooling, and this skill deliberately excludes it.

---

## Step 1 — Confirm Mode

- **Mode A — New static site** (new client build, landing pages, prospect demo sites)
- **Mode B — Existing CMS site** (edits to a live WordPress or similar site the client already runs)

---

## Step 2 — Brand Assets First

Check for existing work BEFORE building anything new:
1. Check `clients/<slug>/` for an existing site, brand files, or deliverables (also `archives/` for past work)
2. Read `clients/<slug>/brand/brand.md` if it exists

- Logo exists → use it; never ship a placeholder when a real logo is on disk
- Colors defined → use the exact hex values; never invent brand colors
- Fonts specified → load via Google Fonts CDN
- No brand file → run `brand-guide-builder` (Mode B generates a design system from scratch), then build from its output

**Creative brief (required before coding):** write 2-3 sentences covering the mood of the site (clean professional? warm inviting? bold industrial?), what makes this business visually different from its competitors, and one design choice that anchors the whole build (e.g. "warm earth tones because this is a family-run contractor, not a corporate chain").

---

## Mode A — Static HTML/CSS Build

### Brief checklist
- [ ] Client name
- [ ] Pages needed (homepage only? multi-page?)
- [ ] Inspiration URL (optional)
- [ ] Story context: who is the customer, what is their problem, what does success look like?

### 1. Structure every page with the StoryBrand framework (Donald Miller)

The customer is the hero; the business is the guide. In this order:

- **Header:** a one-liner that passes the grunt test — within 5 seconds anyone should know what's offered, how it helps, and what to do next. If it doesn't, rewrite it.
- **Problem:** external (the visible issue) + internal (how it makes them feel) + philosophical (why it's just plain wrong). Never skip the internal or philosophical layer.
- **Guide:** two sentences — empathy first, then one proof point of authority.
- **Plan:** 3 steps that feel easy, not complicated.
- **CTA:** primary (Book a Call / Get a Quote) + a secondary transitional CTA (See Our Work). Repeat at hero, after the plan, and footer.
- **Stakes:** one honest sentence on the cost of not acting.
- **Success:** a specific transformation — "from [pain] to [outcome]."

**CTA for service businesses (required):** the primary CTA is a short scheduling questionnaire (service selection → project details → calendar booking), not a bare contact form. Embed Calendly, Cal.com, or equivalent. Customize the questions per industry. Always pair with a tap-able `tel:` phone link — many service-business visitors would rather call.

### 2. Generate `clients/<slug>/site/index.html`
- Single file, styles inline
- Tailwind CSS via CDN: `<script src="https://cdn.tailwindcss.com"></script>`
- Custom brand colors in a `tailwind.config` script block
- Two Google Fonts: display/serif for headings + clean sans for body
- Mobile-first responsive
- Real StoryBrand copy — no lorem ipsum

### 3. Local preview
```bash
cd clients/<slug>/site && python3 -m http.server 3000 &
# Site is at http://localhost:3000
```

### 4. Screenshot → Read → fix loop (minimum 2 rounds)
```bash
python3 tools/shot.py http://localhost:3000 screenshots/
```
After each capture, open the PNGs with the Read tool and critique specifically: "nav padding is 32px, should be 16px." Edit → re-screenshot → re-read. Never stop after one pass.

**Mobile QA:** viewport-only screenshots at real device sizes — 375x667, 390x844, 768x1024 — scrolling sequentially (~85% of viewport height per step). Never full-page screenshots on long pages; they lie about what a phone shows. Test the smallest viewport (375px) FIRST. Hero heading pattern that survives it: `text-4xl sm:text-5xl md:text-7xl` plus `<br class="hidden md:inline">`.

### 5. Run `site-qa-checklist` before presenting
At minimum: WCAG AA contrast on all text, responsive at 375px and 768px, every CTA functional, keyboard tab-through. Fix all failures first.

### 6. Present, then deploy only on explicit approval
Show the final screenshots to the operator. Deploy only after an explicit green-light — never on momentum:
```bash
netlify deploy --prod --site "$SITE_ID" --dir=clients/<slug>/site
```
- Always pass `--site <SITE_ID>`; never `netlify link/unlink` or rely on `.netlify/state.json` (the `tools/hooks/deploy-guard.sh` hook enforces this)
- If the project has a `netlify.toml` declaring `publish`/`functions`, cd to its folder and DROP `--dir` (the flag overrides the toml)
- Frequently-updated sites: add `Netlify-CDN-Cache-Control = "public, max-age=0, must-revalidate"` alongside browser Cache-Control, then `curl -I` to verify `cache-status` shows revalidation, not a stale hit
- Prospect builds: name the Netlify site `<slug>-preview`

---

## Mode B — Existing CMS Site (WordPress etc.)

1. Screenshot the live site before touching anything: `python3 tools/shot.py <live-url> screenshots/before/`
2. Confirm scope specifically — "update hero headline and CTA button," not "improve the homepage"
3. Make the change:
   - Content → step through the page-builder/Gutenberg UI, or via the REST API if an application password is configured
   - Theme/code → exact file edit with a before/after diff
   - CSS → snippet for Appearance → Customize → Additional CSS
4. Screenshot after: `python3 tools/shot.py <live-url> screenshots/after/`
5. Read both sets, compare, confirm the change actually rendered. A successful save/API response is not "shipped" — re-fetch the user-facing page past any cache layer and verify the pixels. The operator approves before close-out.

---

## Client Lifecycle: Demo → Production → Retainer

**Phase 1 — Demo on static hosting.** The Tailwind build above, deployed to `<slug>-preview` for the pitch. Disposable after the deal closes.

**Phase 2 — Production build.** Once the client signs, either keep the static site (fine for most service businesses) or migrate to WordPress:
1. Lightweight hosting; lightweight theme (GeneratePress or Astra) — no heavy page builders for standard sites
2. Port the demo HTML into the CMS
3. Register custom fields for frequently-changed content (hero headline, CTA text, meta descriptions) with `register_post_meta()` + `show_in_rest: true`
4. Create an Application Password for REST access — store it in `.env` as `WP_<CLIENT_SLUG>_APP_PASSWORD`, referenced by variable name only
5. Embed the scheduling questionnaire; test on a real phone; run PageSpeed Insights

**Phase 3 — Retainer edits.** Per session: operator states the change → make it (REST API or theme edit) → screenshot the live front-end to verify it landed → operator approves → log the work in the client record and <TASK SYSTEM>.

---

## Design Guardrails

- **Colors** — never the default Tailwind palette (indigo-500, blue-600) as primary. Define custom colors in `tailwind.config`.
- **Shadows** — never flat `shadow-md` alone. Layered and tinted: `box-shadow: 0 4px 24px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04)`.
- **Typography** — never the same font for headings and body. Headings: `letter-spacing: -0.03em`. Body: `line-height: 1.7`.
- **Gradients** — layer multiple radial gradients; SVG noise for texture on rich backgrounds.
- **Animations** — `transform` and `opacity` only. Never `transition-all`. Easing: `cubic-bezier(0.34, 1.56, 0.64, 1)`.
- **Interactive states** — every clickable element gets `hover`, `focus-visible`, and `active`. No exceptions.
- **Images** — gradient overlay on hero images: `linear-gradient(to top, rgba(0,0,0,0.6), transparent)`.
- **Depth** — base → elevated → floating. Cards feel lifted.

---

## Hard Rules

- No sections or content not requested
- No "improving" a reference design — match it exactly
- No stopping after one screenshot pass
- No `transition-all`
- No default Tailwind blue/indigo as primary
- No lorem ipsum
- Never start copy with "We are..." — start with the customer's problem
- Never "innovative solutions" or "leading provider"
- Never a bare contact form as the primary CTA on a service-business site — scheduling questionnaire + phone link
- Never write copy that praises the product itself ("beautiful design," "stunning visuals") — copy ties back to the customer's story and transformation
- Never deploy without the operator's explicit green-light
- Never include pricing in prospect builds — pricing is value-based and set per deal by the operator
- All text meets WCAG AA contrast (4.5:1 body, 3:1 large text)
- Regulated claims (financing, medical, legal outcomes): flag for the operator's compliance review before anything ships — never draft promotional claims for regulated products on your own authority

---

## File Structure

```
clients/<slug>/site/index.html
clients/<slug>/brand/brand.md
clients/<slug>/brand/logo.png
clients/<slug>/deliverables/
```
