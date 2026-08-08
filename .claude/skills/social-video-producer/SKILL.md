---
name: social-video-producer
description: Full video production system across four engines — AI video generation via a CLI vendor (worked example Higgsfield; Seedance, Kling, Veo, Hailuo), Remotion motion graphics, FFmpeg real-footage editing, and cinematic multi-shot production with native audio. Includes auto-captions, safe-zone end cards, and platform export. Triggers on "video", "reel", "video ad", "TikTok/Reel/Short", "video for <CLIENT>". NOT for scroll-driven on-site animation — use interactive-website-builder.
---

# Social Video Producer

Create video content for clients using four production engines. Read this entire file before generating anything. The worked example vendor throughout is the Higgsfield CLI — swap in your own AI-video vendor; the engine routing and production doctrine are vendor-independent.

## Routing Gate

**This skill:** reels, video ads, product demos, explainers, before/after reveals, testimonials, short films, website hero loop videos — any standalone video file.
**interactive-website-builder:** video as scroll-driven animation embedded ON a website.
**content-repurposer:** adapting written content into text posts (no video output).

---

## The Four Engines

### Engine 1 — AI Video Generation (CLI vendor)
Generates clips from text prompts or still images. Use when the client has NO raw footage: social reels, product demos, lifestyle B-roll, hero loops.
- Before every job: query the vendor for the model's current params and constraints (e.g. `higgsfield model get <job_type>`), then price it before generating (e.g. `higgsfield generate cost <job_type> --prompt "..."` — free and exact). Model params drift; never assume.
- Ask for the target aspect ratio natively (`--aspect-ratio 9:16`). Only pillarbox in FFmpeg when a model genuinely lacks the param.
- **Never bake text into AI-generated clips** — all models struggle with text rendering. Generate clean video; overlay text in post (Step 6).

### Engine 2 — Motion Graphics (Remotion)
Programmatic video from React code — text animations, data reveals, branded graphics. Use when content is primarily TEXT + GRAPHICS: stats reels, quote cards, service highlights, logo reveals. Cost: $0.

### Engine 3 — Real Footage Editing (FFmpeg)
Edit, combine, and polish client-provided clips; add captions, overlays, transitions. Cost: $0.

### Engine 4 — Cinematic Multi-Shot Production
Joint audio-video models (worked example: Seedance 2.0) generate synchronized sound + visuals in one pass — native lip-sync, ambient SFX, music-synced motion, no post-production audio work. Use for short films, brand films, multi-shot narratives, dialogue content, music videos, or character consistency across 5+ shots. For standard reels without audio-sync needs, Engine 1 is faster and cheaper.
- Character consistency: prefer a trained reusable character reference (e.g. `higgsfield soul-id`) over ad-hoc reference packs when a character recurs across a campaign. Reference packs: max 3 stills per subject, consistent lighting.
- Free-iterate complex shots on a vendor's free tier if one exists (watermarked); regenerate final picks on the paid path.

## Engine Routing Tree

```
Does the client have raw footage?
├── YES → Engine 3 (FFmpeg)
│   └── Also need AI B-roll? → Engine 3 + Engine 1 hybrid
├── NO → Content primarily text/stats/graphics?
│   ├── YES → Engine 2 (Remotion) — free
│   └── NO → Multi-shot cinematic (5+ shots, character lock, native audio)?
│       ├── YES → Engine 4
│       └── NO → Engine 1
│           ├── Cinematic brand story → highest-quality model tier
│           ├── Product demo / lifestyle → mid-tier quality mode
│           ├── Quick social reel → fastest turbo model, 9:16 native
│           ├── Seamless product loop → same still as start AND end frame
│           ├── Animate existing illustrations → image-to-video (see Step 4)
│           └── Budget volume (10+ reels) → cheapest model; price the batch first
```

---

## Shared Production Stack

**Auto-captions (Whisper):** every reel gets captions unless the operator says otherwise — captions raise watch time materially. Local `whisper --word_timestamps True --output_format json` is free.
**Voiceover:** only when the brief calls for narration; confirm a TTS vendor is connected before promising narrated deliverables.
**Final assembly:** FFmpeg, last step in every pipeline.

### Platform Export Specs

| Platform | Ratio | Resolution | Best duration |
|----------|-------|-----------|---------------|
| Instagram Reel | 9:16 | 1080x1920 | 15-30s |
| TikTok | 9:16 | 1080x1920 | 15-60s |
| YouTube Short | 9:16 | 1080x1920 | 30-60s |
| YouTube long-form | 16:9 | 1920x1080 | 2-10min |
| Facebook | 9:16 or 1:1 | 1080x1920 / 1080x1080 | 15-60s |
| LinkedIn | 1:1 or 16:9 | 1080x1080 / 1920x1080 | 30-120s |

Set aspect ratio at generation time — never crop after. All vertical output keeps text, faces, logos, and CTAs inside platform safe zones (UI chrome eats the top ~15% and bottom ~20% plus the right rail on 9:16 — keep critical content in the center safe area).

---

## Production Workflow

### Step 1 — Brief + budget check
Confirm: client (check `clients/<slug>/brand/` first) · purpose · platforms · duration · message · does the client have footage (determines engine) · voiceover or text-only · style/mood vs brand · CTA · reference reels · character count and consistency needs · budget (estimate 2-3 attempts per AI shot; a 30s video ≈ 6 shots ≈ 15 generations — price the batch and check the account balance before large runs).

### Step 2 — Script and storyboard
Structure: **Hook (0-3s)** — the customer's problem, never the business name/logo. **Value (3-12s)** — the solution or transformation. **Proof (12-18s)** — social proof, results, before/after. **CTA (last 2-3s)**.

Write as a shot list (visual, text overlay, audio, model, input mode per shot). Present the script to the operator for approval BEFORE generating.

### Step 3 — Character and location reference sheets (Engine 4 only)
Generate turnaround sheets per character (front full-body, profile, back, portrait close-up — consistent lighting, proportions, clothing, clean background) and per location (wide establishing, detail close-up, 3/4 angle, reverse wide — consistent time of day, no people). These become the reference pack; for recurring characters train a reusable reference instead.

### Step 4 — Generate raw content

**CRITICAL: does the client have existing illustrations or artwork?** If YES (book illustrations, product photos, brand art):
- Use IMAGE-TO-VIDEO exclusively — never text-to-video. The client's art IS the brand; never generate imagery that replaces it.
- Flatten transparent PNGs onto the target background color before upload — transparency handling is unpredictable across models.
- Keep i2v prompts under 30 words describing only MOTION, LIGHTING, ATMOSPHERE — never re-describe what's already in the image.

Otherwise, prompt with the six-step structure: Subject → Action → Environment → Camera → Style → Constraints. Always append a constraint block: "Face stable without deformation, normal human structure, natural smooth movements. 4K, cinematic texture, no blur, no ghosting, no flickering."

Engine 4 flow: build the reference pack → generate shot-by-shot with references attached and audio generation on → set aspect ratio per platform → review each shot → assemble in FFmpeg with crossfades.

### Step 5 — Iterate and troubleshoot
Budget 2-3 attempts per shot. Common fixes:

| Problem | Quick fix | Nuclear option |
|---------|-----------|----------------|
| Face distortion | "face stable" constraint, anchor image | Switch to image-to-video with a reference photo |
| Jittery motion | Add speed descriptor ("slow", "gentle") | ONE action verb, longer clip |
| Wrong camera move | Exactly one camera verb | Remove the camera instruction entirely |
| Character drift across shots | Same anchor image every shot | Reference pack at weight ~0.8 |
| Hand/finger distortion | "hands naturally at sides" | Frame above the hands |
| Stray text/watermarks | "No text, no watermarks, no signs" | Regenerate |
| Prompt partially ignored | Prompt too long (120+ words) | Trim to 60-80 words; move detail to anchor images |
| Motion/audio mismatch | Joint audio-video model | Generate video first, sync audio in FFmpeg |

After 3 failed attempts on one shot, stop retrying and switch models — don't burn credits on a model that's fighting you. Past 2 retries, diagnose (extract frames, measure) before attempting a third.

**Trim rule:** cut the first and last 0.5s of every AI-generated clip before assembly — models produce boundary artifacts.

### Step 6 — Captions
Run on EVERY reel unless explicitly skipped. Some Homebrew/minimal FFmpeg builds ship without the `drawtext`/`subtitles`/`ass` filters (`ffmpeg -filters | grep drawtext`). The portable method works everywhere:
1. Transcribe: `whisper audio.wav --word_timestamps True --output_format json`
2. Chunk words into caption cards: ≤4 words and ≤1.8s per card
3. Render each card as a transparent PNG with Pillow — white bold text, black outline, max 2 lines
4. Composite with the `overlay` filter, one input per card:
```bash
ffmpeg -i raw.mp4 -i cap1.png -i cap2.png -filter_complex \
  "[0:v][1:v]overlay=(W-w)/2:1450:enable='between(t,0.0,1.8)'[v1];\
   [v1][2:v]overlay=(W-w)/2:1450:enable='between(t,1.8,3.4)'[vout]" \
  -map "[vout]" -map 0:a -c:a copy captioned.mp4
```
Caption rules: bottom third but INSIDE the safe zone, below faces and held products, 1.5s+ per phrase.

### Step 7 — Voiceover (if applicable)
```bash
ffmpeg -i video.mp4 -i vo.mp3 -i music.mp3 \
  -filter_complex "[1:a]volume=1.0[vo];[2:a]volume=0.12[bg];[vo][bg]amix=inputs=2[a]" \
  -map 0:v -map "[a]" -c:v copy narrated.mp4
```
Voiceover 100%, background music 10-15%. Loudness-normalize client speech with `loudnorm=I=-16:TP=-1.5:LRA=11`.

### Step 8 — Platform export (every target in one pass)
```bash
ffmpeg -i final.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -crf 23 -c:a aac reel_vertical.mp4
ffmpeg -i final.mp4 -vf "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -crf 23 -c:a aac reel_square.mp4
ffmpeg -i final.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -crf 18 -c:a aac video_horizontal.mp4
```

### Step 9 — Deliver
Copy outputs to `clients/<slug>/deliverables/video/`. Log the deliverable in your CRM record and update the related task.

---

## Content Templates

- **Before/after transformation (15-30s):** Engine 1 or 3. Hook → before → transition → after → CTA.
- **Quick tips (10-15s):** Engine 2. Hook → tips 1-3 → CTA.
- **Product/service demo (15-30s):** Engine 1 (turbo model for speed, joint-audio model for quality). Problem → intro → demo → proof → CTA.
- **Testimonial (15-30s):** Engine 3 + 2. Best quote as hook → client speaking → results → CTA.
- **Stats/data reveal (10-20s):** Engine 2. Title → animated data → takeaway + CTA.
- **Day-in-the-life (15-60s):** Engine 3 + 1. Hook → process quick cuts → result → CTA.
- **Cinematic brand film (30-120s):** Engine 4, full narrative arc, reference-pack consistency.
- **Animated illustrated content (15-60s):** Engine 1, image-to-video from the client's existing artwork.

---

## Hard Rules

1. Never generate video without the operator approving the script first.
2. Never deliver without the operator reviewing the final render — extract frames, view them, check subject/framing/palette before calling it done.
3. Always add captions unless explicitly skipped.
4. Always check `clients/<slug>/brand/` before creating anything.
5. Never open with the business logo — open with the customer's problem.
6. Match platform aspect ratio at generation time, never by cropping after.
7. Hold on-screen text a minimum of 1.5 seconds.
8. Export for every target platform in one pass.
9. Log every deliverable in the CRM and task system.
10. Route to the cheapest engine that meets the quality bar — Remotion and FFmpeg are free.
11. Every reel works standalone — assume the viewer has never heard of the brand.
12. Trim first/last 0.5s of every AI clip; budget 2-3 attempts per shot; switch models after 3 failures.
13. Safe zones on all vertical output.
14. Ad copy is grounded in the actual creative — extract frames and verify what the video shows before writing accompanying copy; never invent seasonal hooks or details not present in the footage.
15. Any regulated topic in a client's vertical (financing, health claims, legal services) passes that client's compliance checklist BEFORE anyone sees the video.
