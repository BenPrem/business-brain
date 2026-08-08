---
name: ai-3d-generator
description: AI 3D model generation and web optimization — production-ready GLB/GLTF from text, images, or phone scans (worked examples Meshy AI, Tripo3D, Polycam, Blender — swap your vendor), then gltf-transform compression and model-viewer verification. Triggers on "3D model", "image to 3D", "GLB", "configurator model", "digital twin". Upstream of interactive-website-builder, which displays the assets; escalate here when procedural Three.js realism stalls.
---

# AI 3D Generator

Full pipeline from concept to web-optimized GLB: generate → compress → verify. Read this entire file before generating. Vendors named below are the worked examples — swap your own; the pipeline is vendor-independent.

**Where this sits:** this skill creates the asset; **interactive-website-builder** displays it (`<model-viewer>`, Three.js, hosted embeds). "Build a 3D product page" starts here, then hands off. Escalation route: when procedural Three.js hits its realism ceiling (2 failed realism iterations on a photoreal ask), stop iterating and come here for an AI-generated PBR GLB.

---

## Tool Selection

```
What do you have to start with?
├── A real physical product?
│   ├── Can photograph from all angles → phone scan (Polycam / Luma AI) — most accurate
│   └── Only 1-2 photos → image-to-3D (Meshy or Tripo3D)
├── Concept/description only?
│   ├── Photoreal product model → text-to-3D (Meshy class)
│   ├── Quick stylized interactive element → editor tool (Spline class)
│   └── Maximum quality + you have a GPU → open-source (Hunyuan3D / TRELLIS class)
├── A 2D render or illustration? → image-to-3D (fast vendor for iteration, quality vendor for finals)
└── An existing model that's too heavy? → skip to Optimization Pipeline
```

Rules of thumb: quality/ease balance → Meshy-class; fastest iteration → Tripo-class; real unique objects → scan the actual thing. Pricing and model versions drift fast — verify current versions and pricing before quoting or committing, and validate any pinned API model slug against the vendor's live docs before first use in a session.

---

## Workflow 1 — Image-to-3D (most common)

**Step 1 — Prepare the input image.** Input quality determines output quality:
- Clean background (remove or use white/neutral) — busy backgrounds confuse the boundary
- Even, diffused lighting; no harsh shadows
- Single object per image
- Front 3/4 view — enough visible geometry to infer depth and back surfaces
- 1024x1024 minimum; don't upscale a blurry phone photo and expect miracles

If the client's photo is weak, run **ai-asset-generator** first to produce a clean studio shot, then feed that in.

**Step 2 — Generate.** Web UI or API. Worked example (Meshy API):
```bash
curl -X POST "https://api.meshy.ai/openapi/v2/image-to-3d" \
  -H "Authorization: Bearer $MESHY_API_KEY" -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/product.jpg", "ai_model": "<current-slug>",
       "topology": "quad", "target_polycount": 50000}'
# Poll the task ID until model_urls.glb appears
```

**Step 3 — Optimize** (pipeline below). **Step 4 — Verify** at modelviewer.dev/editor/: clean geometry, correct textures, loads in under 3 seconds.

## Workflow 2 — Text-to-3D

Describe the physical OBJECT, not a scene: `[Object type] + [material/finish] + [key features] + [scale reference]`.

Good: "A modern ergonomic office chair with mesh back, aluminum 5-caster base, adjustable armrests, dark charcoal fabric seat, matte black frame. Product shot, centered, clean."
Bad: "a cool chair" — the more physical detail (materials, colors, finish), the better the mesh.

## Workflow 3 — Phone Scan (real products)

Polycam-class object capture: orbit slowly, 50-100 photos with 60%+ overlap, include top-down views. Even diffused light; matte surfaces scan best; plain unpatterned surface underneath; dust shiny objects with dry shampoo or talcum powder to kill reflections (it works). Video-based capture (Luma-class): 30-60s slow orbit. Export GLB → optimization pipeline.

## Workflow 4 — Full AI Chain (nothing exists yet)

Text description → ai-asset-generator makes a photoreal product image → this skill turns it into a GLB → optimize → interactive-website-builder embeds it. Powerful for prototypes and pre-launch products that don't physically exist.

---

## Optimization Pipeline — Web-Ready GLBs

Raw AI models are almost always too heavy. Targets:

| Context | Max polys | Max file | Max texture |
|---------|-----------|----------|-------------|
| Hero viewer (desktop) | 100K | 5MB | 2048px |
| Configurator | 75K | 3MB | 2048px |
| Mobile product page | 50K | 2MB | 1024px |
| Card/thumbnail | 25K | 1MB | 512px |
| iOS AR Quick Look | 100K | 10MB (USDZ) | 2048px |

```bash
npm install -g @gltf-transform/cli

gltf-transform inspect input.glb            # vertex/triangle counts, texture sizes

# Draco compression + WebP textures + dedup/prune
gltf-transform optimize input.glb output.glb \
  --compress draco --texture-compress webp --texture-size 2048
# Mobile build: --texture-size 1024

# Still over 100K polys? Simplify first (start --ratio 0.75, go lower as quality allows)
gltf-transform simplify input.glb temp.glb --ratio 0.5 && \
gltf-transform optimize temp.glb output.glb --compress draco --texture-compress webp && rm temp.glb
```

Verify: `ls -lh output.glb`, re-inspect, then drag into modelviewer.dev/editor/ and LOOK at it — compression artifacts show up visually, not in stats.

### PBR Materials for Configurators

Color/finish switching requires proper PBR setup: base color (what a variant changes), metallic (0 plastic/fabric, 1 metal), roughness (0 mirror, 1 matte), normal map (detail without geometry). Each independently-configurable part needs its OWN material (seat, frame, arms, casters). If the AI baked everything into one material, split in Blender: import GLB → select faces per part → assign materials → re-export.

The `KHR_materials_variants` extension packs multiple material sets into one GLB — the foundation for `<model-viewer>` configurators. Easiest authored in Blender (3.0+ has the variants addon built in); keep the .blend beside the exported GLB.

---

## File Organization

```
clients/<slug>/site/assets/models/
├── product.glb              # optimized, web-ready
├── product-mobile.glb
├── product.usdz             # iOS AR, if needed
└── source/
    ├── product-raw.glb      # original generator output
    ├── product.blend        # if edited
    └── reference-photo.jpg  # generation input
```
Always keep sources — later change requests (new color, higher quality) start from them, not from scratch.

## Troubleshooting

- **Inside-out model (flipped normals):** Blender → Select All → Mesh → Normals → Recalculate Outside → re-export.
- **Blurry textures after compression:** raise `--texture-quality` (e.g. 90) at the cost of size.
- **Holes/missing faces:** Blender → Mesh → Clean Up → Fill Holes, or regenerate from a cleaner input image.
- **Too shiny/matte:** tune metallic (usually 0.0) and roughness (0.3-0.7 for most products).
- **Black/white box in model-viewer:** missing or external textures — diagnose in modelviewer.dev/editor/; confirm textures are embedded.
- **Can't hit size target:** textures are usually the bottleneck, not geometry — halve texture resolution before reducing polys; last resort, split into on-demand parts.

## Hard Rules

- Optimize before delivering — no raw 50MB GLBs on websites.
- Keep source files in `source/`.
- Test every model in a viewer before integration.
- Configurator models: separate materials per configurable part.
- API keys in `.env` only; log significant generation spend in your decision log.
- Three failed generation attempts → switch approach (different vendor, Blender cleanup, or a phone scan), don't keep rerolling.
- Hand interactive-website-builder the OPTIMIZED GLB path, never the raw one.
