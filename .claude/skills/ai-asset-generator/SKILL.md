---
name: ai-asset-generator
description: AI 2D asset generation for websites, social, and client deliverables — product photography, hero images, lifestyle shots, textures, mockups. Routes photoreal vs illustration vs edit-in-place to the right model; worked-example vendor is the Higgsfield CLI (FLUX, Flux Kontext, Nano Banana) with fal.ai fallback and Midjourney hand-off — swap your own. Triggers on "generate an image", "product photo", "hero image", "mockup", "color variants", or when a website builder needs assets. NOT for video — use social-video-producer.
---

# AI Asset Generator

Generate production-quality 2D assets for websites, social, proposals, and deliverables. Read this entire file before generating. The vendor stack below is the worked example — swap in your own tools; the routing logic and doctrine are vendor-independent.

## Model Routing — the decision logic

Route by JOB, not by habit. The categories that matter:

```
What are you generating?
├── Product photography (e-commerce, clean background)?
│   ├── Have an existing product photo? → EDIT-IN-PLACE model (e.g. Flux Kontext):
│   │     background swaps, color variants — keep everything else identical
│   └── No photo? → PHOTOREAL text-to-image model (e.g. FLUX-class)
├── Hero / campaign imagery (artistic, mood-driven)?
│   └── Cheapest quality-tier stylized model; Midjourney hand-off if the operator
│       has a subscription (hero picks benefit from a human eye on variations)
├── Image that must contain TEXT (signage, packaging, logo mockup)?
│   └── The strongest text-rendering model available (e.g. Nano Banana class)
│       — ALWAYS visually verify the rendered text before shipping
├── Recurring character across a campaign?
│   └── Train a reusable character reference once; reuse it per generation
├── Quick mockup / start+end frames for video work? → fast cheap model
├── Copyright-indemnified imagery (nervous client)? → commercial-safe vendor
│   (e.g. Adobe Firefly) — propose the subscription first if not connected
├── Batch (50+ variants)? → price the batch FIRST, then a scripted loop
├── Background removal / upscale? → dedicated utility models, not prompting
└── Texture / seamless tile? → photoreal model + tiling prompt (below)
```

**Before every job:** query the model's current params, then price the job before generating (`higgsfield model get <job_type>` / `higgsfield generate cost ...` in the worked example). Per-image prices drift — never quote from memory. Anything in your vendor CLI that DEPLOYS to vendor infrastructure (site/app generators) is a deploy: explicit operator green-light required.

---

## Prompting Patterns

Universal structure — completeness matters more than order:
```
[Subject] + [Composition/framing] + [Lighting] + [Style/mood] + [Technical specs] + [Negative constraints]
```

**Clean product shot:**
```
[Product with specific material, color, finish, shape].
Single product, centered, white seamless studio background.
Soft diffused lighting from above-left, subtle contact shadow.
Professional e-commerce product photography, sharp focus, high resolution.
No props, no text, no watermarks, no humans.
```

**Lifestyle shot:** product placed naturally in a specific setting, one camera angle, natural time-of-day lighting, shallow depth of field, "no text overlays, no logos, photorealistic".

**Color variants (highest-value e-commerce play):** with an edit-in-place model —
```
Change the color of the [product] from [current] to [target].
Keep everything else identical: same lighting, background, angle, shadows.
Photorealistic, no other changes.
```
Photograph once, generate the other 6-8 colorways — saves the client thousands in studio time. Calculate that ROI when pricing the service (the operator sets the number).

**Hero images:** visually striking with deliberate negative space for the headline — specify WHERE ("clear negative space on the left third for headline text"), dramatic lighting, "no text, no watermarks, no faces", aspect ratio matched to placement (16:9 hero, 1:1 social, 9:16 stories).

**Textures:** "Seamless tileable [material]. [Palette]. Subtle variation, not perfectly uniform. Flat lighting, no perspective distortion. High resolution, seamless edges." — "seamless tileable" + "flat lighting" are the load-bearing modifiers.

**Midjourney hand-off (no API):** your job is the perfect prompt in a copy-friendly code block with all parameters appended (`--ar` matched to use, `--s 250` balanced / 500+ artistic / 100 literal, `--raw` for photoreal, low `--c` for client work). The operator generates, picks, upscales, saves; you optimize for web afterward. When options are wanted, vary mood via `--s`, not by rewriting the subject.

---

## Workflow Patterns

1. **Product photography package:** client sends 2-5 phone photos → background removal → studio shots (photoreal model) → color variants (edit-in-place) → 3-5 lifestyle placements → deliver at required resolution (typically 2000x2000).
2. **Website hero assets:** read `clients/<slug>/brand/brand.md` first → hero via Midjourney hand-off or your quality model → section textures automated → optimize everything for web.
3. **Social batch:** define the calendar → consistent branded backgrounds → per-post images in one style/palette → text overlays via Pillow/HTML by default (bake text in only with the text-strong model, then verify visually).
4. **Proposal visuals:** match the prospect's real industry and brand colors woven into the prompt — never generic imagery.

---

## Web Optimization (every image, every time)

Raw AI images run 2-10MB — never ship them. Convert to WebP (`sharp -i in.png -o out.webp --quality 85`), generate responsive sizes (480/768/1200/1920), serve via `<picture>` + `srcset` with `loading="lazy"`, explicit width/height.

| Use case | Max width | Target size |
|----------|-----------|-------------|
| Hero image | 1920px | <200KB |
| Section background | 1920px | <150KB |
| E-commerce product | 2000px | <300KB |
| Thumbnail | 480px | <50KB |
| Social post | 1080px | <200KB |

File organization: `clients/<slug>/site/assets/img/{hero,products,products/variants,lifestyle,textures,social}/`. Own ventures: `ventures/<slug>/brand/img/`.

---

## Gotchas Carried From Production

- **Flatten transparency before generating from a PNG.** Transparent inputs behave unpredictably in image-to-image and image-to-video models — composite onto the target background color first. Same rule when a still will later feed an image-to-video pipeline.
- **Image-to-video prompts describe motion only.** When an asset from this skill feeds video generation: prompts under 30 words, motion/lighting/atmosphere only — never re-describe the image contents.
- **Text in images is guilty until proven innocent.** Any generated image containing rendered text gets downloaded and visually Read before shipping — models misspell.
- **Never ship any generated or stock image without viewing it.** Download it, Read it, confirm subject, framing, and that it actually looks good.

## Anti-Slop Rules

- Over-saturated color → add "natural color grading" / "desaturated"
- Plastic skin → avoid people unless needed; "natural skin texture, imperfections, no airbrushing"
- Perfect symmetry → real scenes have subtle asymmetry
- Stock-photo poses → be specific about context and action
- "HDR" in prompts → use "natural dynamic range" or "film-like contrast"
- Purple/blue AI gradients → the universal tell; use the client's actual brand palette

## Hard Rules

- Check `clients/<slug>/brand/brand.md` before any brand-adjacent imagery.
- Never generate images of real, named people; never AI-generate client headshots/team photos without explicit client approval; disclose AI generation if the client asks.
- Optimize every image for web before delivery — no 4MB PNGs on websites.
- API keys live in `.env` only — reference by variable name, never paste values.
- Price every batch before running it; log significant generation spend in your decision log.
- Keep the best working prompt per client in their brand folder for reuse.
