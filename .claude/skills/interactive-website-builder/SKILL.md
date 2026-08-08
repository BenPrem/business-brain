---
name: interactive-website-builder
description: Premium interactive website builder for scroll-driven, animated, immersive experiences — GSAP + Lenis, Three.js, 3D model viewers/configurators, AI video backgrounds. Use for creative brands, tech companies, agencies, product launches, portfolios, or your own agency site. Triggers on "interactive", "animated", "scroll animations", "3D", "immersive", "wow factor". NOT for standard service-business conversion sites — use website-builder.
---

# Interactive Website Builder

Build award-caliber interactive sites: GSAP + Lenis + Three.js/3D viewers + AI-generated video. Output is multi-file HTML/CSS/JS deployed to static hosting (worked example: Netlify) or embedded in WordPress.

## Routing Gate — Which Builder?

**This skill:** the operator asks for scroll animations, GSAP, video backgrounds, 3D, "premium/interactive/immersive/Awwwards-level"; creative brands, tech companies, agencies, product launches, portfolios where the site IS the experience; 3D configurators, digital twins, model viewers; adding animation to an existing WordPress site.
**website-builder:** local service businesses (HVAC, dental, contractors, restaurants, legal) where the site's job is pure lead conversion — speed and clarity beat aesthetics; prospect demo sites unless explicitly upgraded.
If unclear, ask: "standard clean site or premium interactive build?"

## Video-to-Website Quick Start (~30 min to a premium demo)

1. Generate a reference image of the product in its hero state (ai-asset-generator).
2. Generate the hero video via social-video-producer — reference image as start AND end frame for a seamless loop; request the aspect ratio natively.
3. Drop the video in the project, extract frames with FFmpeg, build the scroll-driven page.
4. Iterate on localhost with the screenshot loop. Compress video (`ffmpeg -i in.mp4 -vcodec libx264 -crf 28 -preset slow out.mp4`, target 1080p under 5MB); `preload="auto"` + `poster` from the first frame.

---

## Build Workflow

**Step 1 — Brand assets.** Check `clients/<slug>/` for existing site/brand/deliverables FIRST; read `clients/<slug>/brand/brand.md`. Logo exists → use it; colors defined → exact hex; no brand file → run brand-guide-builder or design from the philosophy below.

**Step 2 — Visual direction.** Before code, document: mood (dark cinematic / clean editorial / bold experimental), motion philosophy (subtle polish / scroll storytelling / full immersion), which tech layers the build needs (GSAP only? + Lenis? + Three.js? + video? + 3D models?), reference sites.

**Step 3 — Assets before code** — the hero video/imagery drives palette, typography, layout. Video backgrounds → social-video-producer. Images → ai-asset-generator. 3D models → ai-3d-generator makes the GLB, this skill displays it. Photography: the client's real photos first; never untreated stock heroes; download and visually Read any stock/AI photo before shipping.

**Step 4 — Narrative structure is non-negotiable.** Even premium animated sites follow a conversion arc: Hero (one-liner + CTA above the fold) → Problem (scroll-revealed) → Guide (empathy + authority) → Plan (3 steps animated in sequence) → Stakes (mood shift) → Success → CTA (hero, after plan, footer). Service businesses getting the premium treatment still get a prominent call/schedule CTA, styled to match.

**Step 5 — Scaffold:** `clients/<slug>/site/` with `index.html`, `css/styles.css`, `js/main.js`, `assets/{video,models,img}/`. JS init order: register GSAP plugins → reduced-motion check → Lenis → animations → Three.js → `ScrollTrigger.refresh()` on window load.

**Step 6 — Screenshot loop (minimum 2 rounds).** Serve locally, screenshot, READ each PNG, give yourself specific notes ("hero heading is 48px, bump to 72px"), edit, re-screenshot. Mobile QA via Playwright headless at 375x667 / 390x844 / 768x1024, `device_scale_factor=2`, viewport-only screenshots at sequential scroll positions — never `full_page=True` on pages with sticky/pinned sections (renders artifacts).

**Step 7 — QA.** Run site-qa-checklist, plus interactive minimums: `prefers-reduced-motion` degrades everything to static · WCAG AA contrast over images/video/gradients · 375px layout intact, no horizontal scroll · video has poster fallback, 3D has loading state + fallback image · GSAP/Lenis don't break Tab order or trap keyboard users · touch targets ≥44px · page weight <5MB (8MB with lazy-loaded video).

**Step 8 — Present and deploy.** Present final screenshots; deploy ONLY after the operator's explicit green-light. Netlify worked example: always `netlify deploy --prod --site "$SITE_ID"` — pin the site ID explicitly, never rely on directory linking/state files (wrong-site deploys are how client sites get overwritten). If a `netlify.toml` declares publish/functions dirs, don't pass `--dir` (it overrides the toml). Frequently-updated pages: add an edge-cache revalidation header and verify cache behavior with `curl -I` post-deploy. **Frames gotcha:** if the scroll animation uses extracted frames, verify `.gitignore` isn't excluding `frames/` — excluded frames = works on localhost, blank in production.

---

## Design Philosophy

Goal: sites people screenshot and share — not templates with purple gradients.

**Anti-slop rules:** no Inter/Roboto/Arial/Open Sans/system-ui as display fonts (use Geist, Satoshi, Cabinet Grotesk, Outfit, Syne, General Sans, Switzer, or brand serifs) · no purple-to-blue AI gradients, neon-on-dark, rainbow palettes — one dominant color + one sharp accent, saturation under 80% · no centered hero-subtitle-CTA as the default for every section — break symmetry with offset grids and full-bleed media · no generic drop-shadow card grids, no lorem ipsum, no untreated stock heroes · never animate everything at once — 3-4 key moments per section.

**What premium feels like:** typography carries the design (one distinctive heading font + one clean body font, massive size contrast, headings `letter-spacing: -0.03em`, body `line-height: 1.7`) · whitespace is structural (120-200px section padding) · color restrained · every animation answers "what is this helping the user understand?" — no answer, remove it · scroll is the input, animation is the output · depth from layered tinted shadows (`0 4px 24px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04)`).

## Technology Stack (all free for commercial use)

**GSAP** — all plugins free since the Webflow acquisition (2025). CDN gsap@3 + ScrollTrigger + SplitText; `gsap.registerPlugin(...)` before use. Animate transforms only, never layout properties; `overwrite: true` where tweens overlap; `scrub: 1` for smoothed scroll-sync; `markers: true` in dev only; kill tweens on teardown.

**Lenis — the load-bearing snippet:**
```javascript
const lenis = new Lenis();
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((time) => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```
**Never Locomotive Scroll** — it hijacks native scrolling, breaks CSS sticky, and fights ScrollTrigger. Lenis is the standard.

**Three.js — only when CSS 3D is insufficient** (particles, shaders, custom geometry — CSS 3D + GSAP delivers 80% of the impact for most landing pages). Cap `setPixelRatio` at 2; always add a resize handler; `alpha: true` when layering; static fallback image on mobile; dispose geometry/materials on teardown; verify your CDN pin actually includes the geometry classes you use (older builds lack newer geometries).

## Video Backgrounds

Rules: slow motion (content sits on top) · dark footage (text over light video is unreadable) · seamless 8-10s loop · under 5MB · no text baked in (overlay in HTML) · ship .mp4 + .webm.

```html
<video class="hero-video" autoplay muted loop playsinline preload="auto"
  aria-hidden="true" poster="assets/video/hero-poster.jpg">
  <source src="assets/video/hero.webm" type="video/webm">
  <source src="assets/video/hero.mp4" type="video/mp4">
</video>
```
All four playback attributes are required (`muted` for autoplay, `playsinline` for iOS). Hero container `min-height: 100dvh` (not `vh` — iOS address-bar jump). Layers: video z-0 → overlay z-1 (`rgba(0,0,20,0.55)`) → content z-2. Poster: `ffmpeg -i out.mp4 -frames:v 1 hero-poster.jpg`.

## Scroll-Driven Video (the "I want that" effect)

Scroll position controls playback: a 300-500vh section wrapping a `position: sticky; height: 100vh` container.
```javascript
const video = document.querySelector('.scroll-video');
video.addEventListener('loadedmetadata', () => {
  gsap.to(video, {
    currentTime: video.duration, ease: 'none',
    scrollTrigger: { trigger: '.scroll-video-section',
      start: 'top top', end: 'bottom bottom',
      scrub: 0.5,   // 0 = jittery, 1+ = laggy
      pin: false }  // CSS sticky handles pinning
  });
});
```
More section height = slower playback; `scrub` 0.3-0.8; always a reduced-motion fallback (single key frame); mobile gets a static image or reduced frames. For smoother scrubbing at the cost of weight: extract frames at build time, draw to canvas per scroll position, keep total under 10MB, preload before enabling scroll.

## 3D Stack Decision Table

```
Client has a GLB?
├── Yes → need material/variant switching?
│   ├── Yes → hosted configurator platform, or <model-viewer> with KHR variants
│   └── No → rotate/zoom/AR only → Google <model-viewer> (one tag, free)
├── No → stylized hero scene in an editor tool (Spline class)?
│       else custom programmatic 3D → Three.js
```
No GLB yet → ai-3d-generator. Paid 3D platforms: confirm an account exists and bill the recurring cost into the project before scoping on one. **When NOT to use 3D:** if a static image or video communicates the same thing, use that — decorative 3D slows the page and doesn't convert.

## Performance and Accessibility (built in from the start)

`prefers-reduced-motion`: CSS kills animations and hides video (poster as background), JS checks `matchMedia` before initializing GSAP/Lenis/Three.js · `will-change: transform, opacity` on animated elements (remove after one-shots) · `loading="lazy"` offscreen; `ScrollTrigger.batch()` for repeated elements · targets LCP <3s, INP <200ms — test on a real mid-range Android · pinned sections tested in iOS Safari specifically · `aria-hidden="true"` on background video, visible focus states, semantic landmarks — animation is enhancement, never information.

## WordPress Lifecycle (demo → production → retainer)

**Phase 1:** static demo on Netlify (the sales tool, `<slug>-preview`). **Phase 2 (after signing — a migration, not a rebuild):** managed WordPress hosting (never static-host WordPress); a reusable parent theme carrying the animation stack (GSAP/Lenis enqueue + init script) plus a per-client child theme (brand CSS, ported `main.js`, templates); `register_post_meta()` with `show_in_rest: true` for retainer-editable content; WP Application Password in `.env` only. **Phase 3 (retainer):** content via REST API, design via child-theme edits + cache clear. A 200 from the WP API is NOT "shipped" — re-fetch the front-end URL past cache and verify the change is visible. WP rules: always `wp_enqueue_script()` (footer, dependency chain GSAP → plugins → Lenis → custom), conditional loading on interactive templates only, disable theme smooth-scroll before Lenis, clear caches after every change.

## Debugging Common Issues

- Animations fire on load, not scroll → plugins not registered first.
- ScrollTrigger positions wrong after images load → `window.addEventListener('load', () => ScrollTrigger.refresh())`.
- Scroll jank → animate transforms not layout; add `will-change`.
- Mobile autoplay fails → needs `muted` + `playsinline` (+ `preload="auto"` on some Androids).
- Three.js tanks mobile → cap pixel ratio at 2, cut particles, static fallback.
- Lenis laggy → tune `lerp` (0.1 smoother, 0.15 snappier); ensure `lagSmoothing(0)`.
- 3D model won't load → GLB under 5MB, same-origin or CORS-enabled, viewer script before the element.

## Hard Rules

- No sections not requested; no lorem ipsum — real conversion copy.
- Minimum 2 screenshot rounds; 3-4 animation moments per section, never everything at once.
- Never start copy with "We are..." — start with the customer's problem; never "innovative solutions" / "leading provider".
- Never Locomotive Scroll; never skip `prefers-reduced-motion`.
- Never deploy without the operator's explicit green-light; always pin the deploy target site ID.
- Never include pricing in prospect builds — the operator sets and delivers every number.
- Any regulated claim in the client's vertical (financing, health, legal) passes their compliance checklist before anyone sees the page.
