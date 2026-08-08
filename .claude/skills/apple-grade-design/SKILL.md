---
name: apple-grade-design
description: Apple-grade design language layer for websites and marketing graphics — sleek professionalism with experiential craft, encoding Apple's actual design system (type scale, tracking, palette, layout grammar, motion doctrine, copy voice) as verified against apple.com's live CSS. Use for "Apple-style", "sleek", "premium", "minimal high-end" requests, or when website-builder / interactive-website-builder / ai-asset-generator work needs a premium aesthetic. Three modes: BUILD (apply the system), GRAPHICS (static ads/social/slides), REVIEW (audit against the system). A design-language layer, NOT a builder — it styles what other skills build.
---

# Apple-Grade Design

Reproduce the design philosophy behind apple.com: **clarity** (nothing ambiguous), **deference** (the interface serves the content — on marketing pages, "content" means the hero visual and the claim), and **depth** (hierarchy from layers and restrained motion). Lineage: Dieter Rams' "less, but better" → Jony Ive's "bold, pure, perfectly proportioned, coherent, effortless."

One-sentence version: **a small number of rules, enforced ruthlessly.** One typeface. Semibold-600 headlines with size-scaled negative tracking. White, two grays, near-black, one blue. One message per viewport. Whitespace as material. Motion that reveals instead of performs.

**Provenance:** tokens below were extracted from apple.com's live shipped CSS (2026). Apple evolves its site — if a year has passed, re-verify key values against apple.com before a big build.

## The Ten Commandments

1. **One typeface.** System font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`) or Inter. **NEVER embed SF Pro on client work — Apple's license restricts it to Apple-platform software; embedding it on a client website is a violation.** Weight does all the work: 600 headlines, 400 body, 500 small labels.
2. **Track the type.** Negative letter-spacing that scales with size (about -0.015em at 80px hero sizes, easing toward 0 at body sizes). Untracked large type is the #1 tell of fake-Apple.
3. **Five colors.** White, light gray #f5f5f7, near-black #1d1d1f, one gray text ramp, one blue (#0071e3 buttons / #0066cc links) — and blue appears ONLY on interactive elements.
4. **One message per viewport.** A section makes one claim with one visual. Two headlines = two sections.
5. **Whitespace is a material.** 100-120px section padding on desktop; ≥35% empty canvas on static graphics. Hierarchy comes from space, never from boxes and borders.
6. **Alternate the stage.** white → #f5f5f7 → dark full-bleed bands create chapters; the dark band is reserved for the 1-2 most dramatic claims.
7. **Persistent CTA.** 48px frosted sticky sub-nav (`backdrop-filter: saturate(180%) blur(20px)`) with a pill CTA always reachable — for service-business clients that pill is "Call" / "Get a quote", not "Learn more".
8. **Motion is disciplined.** Fade-up + ~24px translate, ease-out, runs once, staggered across at most 5 elements. One or two scroll-scrubbed moments per page maximum. `prefers-reduced-motion` always honored.
9. **Copy is compressed.** Headlines ≤8 words. Benefit before spec. The period as a signature ("Durable. By design."). Every superlative footnoted or cut.
10. **Feeling → proof → fact.** Emotional hero, escalating proof chapters, quiet rational close — specs styled DOWN (small, gray, dense) at the end, never shouted.

## Mode: BUILD (websites)

1. Choose the font strategy: system stack by default; Inter when cross-platform pixel-fidelity matters.
2. Structure the content with your narrative framework (customer as hero) — that's the WHAT; this system is the HOW. Apple's product-as-hero becomes the customer's *outcome* as hero.
3. Compose sections per the commandments: one claim + one visual each, alternating stage colors, generous padding, frosted sub-nav, footnoted claims, specs styled down at the close.
4. Conversion elements keep their proven mechanics (forms, tel links, tracking) — this skill restyles them, never removes them.
5. Existing-brand clients: their brand color replaces the BLUE ACCENT SLOT only; the neutrals, type discipline, spacing, and motion doctrine stay. If brand guidelines conflict harder than that, flag it — don't silently hybridize.

## Mode: GRAPHICS (ads, social, slides)

Subject-on-dark or center-set-on-light composition. One line of copy. One gradient element maximum. Footnote any superlative. Flat single-color logo. ≥35% empty canvas. Platform safe zones on social sizes. Produce via ai-asset-generator or Pillow, and run the standard visual assertion pass: view the rendered output at real scale, measure centering, verify before shipping.

## Mode: REVIEW (audit an existing design)

Audit against the Ten Commandments, most severe first: typography discipline → color restraint → spacing/hierarchy → one-message-per-viewport → motion restraint → copy compression → accessibility (≥4.5:1 body contrast, 44px touch targets, reduced-motion support). Output what/why/fix per issue, citing the commandment. Be specific — "#aaa on white is 2.3:1 and fails 4.5:1", never "contrast could be better".

## Anti-Checklist (instant tells of fake-Apple)

- Untracked large headlines · multiple typefaces · blue used decoratively
- Boxes, borders, and drop shadows doing hierarchy's job
- Two claims sharing a viewport · centered-hero-subtitle-CTA repeated for every section
- Motion that performs (bounces, spins, parallax everywhere) instead of revealing
- Unfootnoted superlatives · "Learn more" as the primary CTA on a lead-gen site
- SF Pro embedded via @font-face on non-Apple work

## Composition With Other Skills

- **website-builder / interactive-website-builder** — they build, this styles. Use these tokens instead of their default aesthetic when premium is requested.
- **brand-guide-builder** — can emit an Apple-grade variant brand system from these tokens.
- **scroll-demo-builder** — sales demos are wow-first and exempt from the motion budget; keep the easing discipline.
- **ai-asset-generator** — produces the photography this system demands.
- **site-qa-checklist** — still the shipping gate; REVIEW mode here is aesthetic, not QA.

## Verification Gate

A build claiming this skill isn't done until: rendered screenshots at 1440px and 375px are actually viewed and pass a stop-and-look check · type tracking is visibly applied at hero sizes · section rhythm alternates correctly · nothing from the anti-checklist is present · reduced-motion is verified. "Looks Apple" is judged from the rendered frame, not the CSS.
