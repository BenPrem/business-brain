---
name: stylized-3d-worldbuilding
description: Build and art-direct stylized low-poly 3D worlds and structures in Three.js — the Journey/Monument Valley school. Procedural architecture as code, palette and value discipline under tone mapping, silhouette-first design, measured-footprint placement with overlap assertions, ambient animation, and a mechanical verification harness. Triggers on "3D world", "low-poly", "three.js scene/building", "stylized 3D", "make it look hand-crafted", or any walkable-world build. NOT for GLB generation from prompts — use ai-3d-generator; NOT for scroll-page animation — use interactive-website-builder.
---

# Stylized 3D Worldbuilding

Expertise layer for hand-crafted-feeling low-poly worlds built procedurally in Three.js. Everything below was paid for in real builds — treat the laws as load-bearing, not stylistic preference.

## The Laws

1. **The rendered frame is the contract — never the hex swatch.** Tone mapping (ACES) plus scene lighting reshape every color: a plausible dark albedo in code renders as a black void; warm colors push hot. Never judge a material from its hex value. Grade darks roughly 2 stops lighter than instinct says, then verify by screenshot under the world's actual lighting rig.
2. **Value structure beats hue.** Big masses live in mid-values; true darks are reserved for openings (doors, windows, arches). The frame must survive grayscale — if it doesn't read desaturated, no palette will save it. Saturation is a budget spent only on focal points.
3. **One palette = one hand.** Every asset samples one muted master palette. One quiet accent color per structure, meaningfully chosen. Mixed palettes read instantly as mixed authorship.
4. **Silhouette first.** A landmark must be identifiable as an unlabeled black silhouette. Test this literally — build a silhouette toggle into your preview page. Compose big-medium-small massing; a building's identity lives in its roofline.
5. **Ground everything in real references.** Research the real building type or place, encode its 4-6 defining features, and note them in code comments. Reference accuracy is what separates "vaguely church-shaped" from unmistakable.
6. **Build → measure → place → assert.** Meshes are born BEFORE placement. Footprint radii are MEASURED (Box3 swept extent across the mesh), never guessed — guessed radii and unvalidated fallbacks are how buildings end up inside mountains. Placement runs under constraints (slope, channel, region, spacing) and a pairwise composition audit asserting zero overlaps is the gate. Screenshots confirm; audits discover.
7. **No unvalidated placement paths.** Every fallback either validates its result or reports itself. Silent drops are forbidden.
8. **Ambient motion is eased, phase-offset, and meaningful.** No linear motion, no synchronized loops. Small secondary motion (a flag, foam, a swaying lantern) sells life more cheaply than anything else.
9. **Geometry-axis changes invalidate every derived placement.** After remapping any layout axis or coordinate system, re-render and eyeball EVERY placement site — passing physics/containment audits says nothing about composition.

## Procedural Architecture Recipes

- **Domes:** `LatheGeometry` over a profile curve; keep segment counts low (8-12 radial) so facets read as craft.
- **Arches and openings:** `Shape` + holes → `ExtrudeGeometry`; the negative space does the storytelling.
- **Hip/gable roofs:** hand-build with `BufferGeometry` vertices — box-plus-pyramid mashups read as toys; correct eave overhang reads as architecture.
- **Tents and organic forms:** start from a cone/lathe, then jitter vertices with a small deterministic noise pass — perfectly regular geometry is the anti-craft tell.
- **Repetition:** `InstancedMesh` for columns, crenellations, fence posts, foliage; vary scale/rotation per instance slightly.
- **Flat shading everywhere** (`flatShading: true` or computed face normals) — the faceted light response IS the style.
- Budgets: set explicit triangle and footprint budgets per asset class and print them in the preview readout.

## Workflow for a New Build or Upgrade Pass

1. **Research** the real subject → write a spec per asset: proportions, materials, low-poly recipe, one close-look detail.
2. **Style contract:** master palette values, permitted value band, scale convention (human ≈ 1.8 units), triangle + footprint budgets, "nothing glows" rules. Write it down before building.
3. **Build procedurally** against the recipes above, sampling only the contract palette.
4. **Preview page** with the world's EXACT lighting rig + tone mapping, a silhouette toggle, and per-asset footprint/triangle readouts. Judging assets under neutral lighting is self-deception (Law 1).
5. **Verify mechanically** — composition audit, budget checks, silhouette test — then eyeball EVERY asset, no sampling. Then integrate into the world and re-audit in place.
6. **Delegation pattern (proven):** a second model/agent can draft builders in parallel against the same specs and style contract in a quarantined file; integrate by selection plus an art-direction re-grade. Expect delegated output to run too dark and too saturated — grade it to the rendered frame.

## Verification Harness (minimum bar)

- Pairwise overlap assertion across all placed footprints (measured, not declared radii) — zero tolerance.
- Silhouette test per landmark.
- Grayscale screenshot check for value structure.
- Budget assertions (triangles, draw calls) printed per asset.
- Screenshot review at world lighting after every grading pass — the frame, not the code, signs off.
