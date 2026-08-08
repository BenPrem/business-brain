---
name: scroll-demo-builder
description: Builds scroll-driven interactive sales demos — single-file HTML with canvas animations and scroll-hijacked storytelling. Two patterns — ASSEMBLY (object builds piece-by-piece) and JOURNEY (object travels through illustrated stations). Triggers on "build a demo", "scroll animation", "interactive preview", "wow them", "journey demo", "scroll journey". SALES WEAPON — not a production website.
---

# Scroll Demo Builder

Build single-file, scroll-driven interactive demos. These are sales weapons: short-lived, high-impact preview pages deployed to wow a prospect before the pitch — not production websites. Read this entire file before writing code.

Two patterns:
1. **ASSEMBLY** — an object (car, building, rocket, logo) assembles piece-by-piece as the user scrolls. Static camera, progressive reveal.
2. **JOURNEY** — an object (coffee bean, raw material, ingredient) travels downward through stations, camera following. Each station is a full illustrated scene.

## Choosing the Pattern

| Client / concept | Pattern | Why |
|-----------------|---------|-----|
| Creative agency, car brand, construction | Assembly | Object builds = craftsmanship metaphor |
| Coffee roaster, brewery, food producer | Journey | Origin-to-finished = process storytelling |
| Manufacturing / supply chain | Journey | Raw material transforms through stages |
| Tech startup, SaaS | Assembly | Rocket/logo builds = innovation metaphor |
| Any "from X to Y" story | Journey | Natural downward progression |
| Any "we build great things" story | Assembly | Watch quality materialize |

If the operator specifies, use that; otherwise suggest the best fit.

## What This Produces

A single HTML file (~50-100KB) containing: full-screen HTML5 canvas (procedural drawing or image compositing) · 8-10 scroll-driven narrative stages · branded text panels fading in/out at set scroll percentages · particle systems (sparks, smoke, dust, steam) · custom cursor with trailing ring + dot (hidden on mobile) · film-grain SVG overlay on dark assembly demos · progress bar · responsive with a mobile fallback · zero external JS dependencies, no build step.

---

## CRITICAL: Visual Quality — Images vs. Procedural Drawing

The most important lesson from real builds.

**Procedural canvas drawing (code-only):** everything drawn with paths, arcs, beziers. Single file, instant load, easy deploy — but a hard ceiling on visual quality. Fine for GEOMETRIC subjects (cars, buildings, logos); **fails for organic/detailed subjects** — code-drawn trees look like code, not illustration. Use for assembly demos and speed-over-fidelity builds.

**Image assets (generated or sourced):** station illustrations as PNGs composited via `drawImage()`. Any visual style becomes reachable — botanical engraving, watercolor, photoreal. Requires an image-generation tool (ai-asset-generator). Use for journey demos, organic subjects, and any premium ask.

**Hybrid (recommended for journey demos):** image assets for station scenes + procedural canvas for the traveling object, particles, and connecting lines. Beautiful static scenes, smooth animated elements. Keep one consistent art direction across all stations (same style, palette, line weight); size images at 2x display resolution; load at startup behind a loading gate; layer procedural effects on top.

**Video-to-frames technique:** generate ONE AI video (social-video-producer), extract frames (`ffmpeg -i reveal.mp4 -vf "fps=24,scale=960:-2" -q:v 4 frames/frame_%04d.jpg`), map scroll percentage to frame number, draw the current frame to canvas, layer text/particles on top. Powerful for product deconstruction demos — the user's scroll drives the deconstruction. Keep total frames under 10MB (JPEG quality 75-80).

---

## Step 1 — Research the Prospect

Before drawing a pixel:
1. **Scrape their existing site** (Firecrawl/WebFetch): brand colors from CSS/logo, business type, real service/product names, tagline, visual style (clean? rustic? luxury?), and — if the demo should preserve their current homepage header — those asset URLs.
2. **Check your CRM and task system** for existing records on this prospect.
3. **Pick pattern + art direction:** dark blueprint (assembly default — near-black bg, accent wireframes) · light/cream (journey — warm white, muted tones) · match-their-brand · botanical/engraving (image assets) · clean modern flat.

## Step 2 — Build

Core architecture, both patterns:
- One scroll container whose height defines total narrative length; canvas is `position: fixed`, full-screen; a scroll handler computes progress 0-1 and everything derives from it.
- Text panels are absolutely-positioned HTML (not canvas text) shown/hidden by scroll range — crisp, accessible, easy to edit.
- Particles: emit and draw in the SAME coordinate space; pool and cap counts; alpha-fade lifecycle.
- Journey world/camera: stations at fixed WORLD Y positions; object Y derived from scroll via easing between station breakpoints; `cameraY = objectY`; everything drawn at `screenY = worldY - cameraY + viewportOffset`.
- Assembly: pieces each have start/end scroll ranges with eased interpolation from offscreen/scattered to final position; sparks fire on connection; exit animation translates the WHOLE object at the top of the draw function.

## Step 3 — Deploy

1. Save as `clients/<slug>/deliverables/demo/index.html` (+ `assets/` if using images).
2. Test locally — scroll through ALL stages, verify panel sync, check mobile.
3. Get the operator's explicit green-light BEFORE deploying.
4. Deploy with the target site pinned explicitly (e.g. `netlify deploy --prod --site "$SITE_ID" --dir=...`) — never rely on directory linking/state files.
5. Name the URL `<client-slug>-preview`; the operator approves the live URL before the prospect sees it.

---

## Common Pitfalls (from real builds)

**Both patterns:**
1. **Particles in the wrong coordinate space** — if particles stick to the viewport, you stored screen coordinates instead of world coordinates. Store world Y; convert when drawing.
2. **Forgetting mobile** — hide the custom cursor (`display:none!important`, `body { cursor:auto }`), pin panels to the bottom, test touch scroll.
3. **Text panels out of sync** — panel scroll ranges and animation ranges are coupled; adjust together.
4. **Unicode minus signs** — U+2212 (−) pasted from formatted text instead of ASCII `-` causes JS syntax errors.

**Assembly:**
5. **Exit animation detaches pieces** — apply the exit translate at the TOP of the draw function so everything moves together, never mid-draw.
6. **Exit direction** — object faces left → exit translates negative X. Match facing.

**Journey:**
7. **Object flies off screen** — the #1 bug. `cameraY = objectY`: object derives from scroll, camera derives from the object. Never compute them independently.
8. **Stations drawn at screen coordinates** — all station positions live in world space, converted via `screenY()`; fixed pixel positions make stations move with the camera.
9. **Procedural drawing on organic subjects** — beziers can't fake botanical illustration. Use image assets; keep procedural for the traveler, particles, connectors.
10. **Hero section breaks scroll math** — journey progress must be LOCAL to the journey section: `pageYOffset - journeySection.offsetTop`.
11. **Draw loop starts before images load** — gate on `loadedCount < totalImages` and show a loading indicator, not blank stations.
12. **scrollBreaks and panel ranges drift apart** — they're coupled arrays; change both or text appears while the object is mid-transit.

## Quality Bar

**Assembly:** something moves within the first 2vh of scroll · no dead zones between 8% and 88% progress · sparks on connection · ambient effects (glints, shimmer) make the finished object feel alive · CTA with hover magnetism and shine sweep · film grain on dark backgrounds · loads in under 1 second.

**Journey:** the object is ALWAYS visible and centered · station illustrations are the star and look premium, not code-generated · the object morphs convincingly between stages (color, size, shape) · quadratic ease-in-out between stations, never linear · panels never overlap stations · particle trails match the current stage color · steam/smoke brings stations to life · loading state until all assets are ready.

## Iteration Pattern

Expect 2-4 refinement rounds after the first build. Feedback lands mostly on station artwork and camera/object behavior. Visual quality complaints about procedural drawing → pivot to image assets. Animation complaints → adjust breakpoints, easing, camera. Copy complaints → panel text only.
