---
name: video-analyzer
description: Analyze video files by extracting frames with FFmpeg and visually Reading them to learn what's actually inside — on-screen text, products, people, quotes, branding — before any content decision. Triggers on "look at these videos", "what's in these clips", "review the footage", "analyze the reels", or whenever client-provided videos need captions, calendars, or audits. If video files exist and decisions depend on them, run this first — never guess from filenames.
---

# Video Analyzer

Claude cannot play video, but it CAN view images. This skill bridges the gap: extract key frames with FFmpeg, then Read them. The result is planning accuracy equal to having watched the footage.

Why it matters: planning content around unseen videos produces wrong captions, wrong scheduling, and missed details. A filename like `Review (FB).mp4` doesn't tell you which product is reviewed, what the reviewer said, or what the visual style is. Frames do.

## When to Run This First

Before any of these tasks, whenever video files are involved:
- **Content calendar creation** — know what each video contains before scheduling or captioning it
- **Social media planning** — match videos to pillars, platforms, cadence
- **Client video audit** — inventory existing content before building strategy
- **Caption writing** — see the screen so captions complement rather than repeat
- **Quality review** — brand consistency, text readability, style across a set

---

## Workflow

### Step 1 — Probe metadata, then extract frames

```bash
# Metadata for every video in a folder (duration, resolution, audio streams)
for f in videos/*.mp4; do
  ffprobe -v quiet -print_format json -show_format -show_streams "$f" \
    > "analysis/$(basename "$f" .mp4).json"
done

# Extract start / middle / end frames (repeat per file; MID = duration/2, END = duration - 0.5)
ffmpeg -ss 0.5 -i video.mp4 -frames:v 1 thumbs/video_start.png
ffmpeg -ss "$MID" -i video.mp4 -frames:v 1 thumbs/video_mid.png
ffmpeg -ss "$END" -i video.mp4 -frames:v 1 thumbs/video_end.png
```

Save output alongside the videos, e.g. `clients/<slug>/deliverables/content-calendar/video-analysis/`. Write a `summary.md` inventory table (filename, duration, resolution, aspect, audio y/n) as you go.

Frame count by duration:

| Duration | Frames | Why |
|----------|--------|-----|
| Under 5s | 1 (mid) | One frame captures it |
| 5-15s | 3 (start/mid/end) | Default — catches transitions and the final CTA |
| 15-60s | 5 | Multiple scenes likely |
| Over 60s | 5-8 | Full scene coverage |

### Step 2 — Read the metadata for signals
- **No audio stream** = animated graphic or text overlay; captions carry 100% of the story.
- **Under 10 seconds** = likely an animated social graphic, not filmed content.
- **Portrait (1080x1350, 1080x1920)** = built for Instagram/TikTok; **landscape** = Facebook/YouTube.
- **Same content at two resolutions** = client pre-made platform pairs (filenames often end "(FB)"/"(IG)").

### Step 3 — View the frames
Read each PNG. Start with the `_mid` frames — they usually capture the main content; check `_start`/`_end` only when mid is ambiguous or the video runs longer than 15s.

Document per video:
1. **On-screen text** — headlines, quotes, CTAs, review text. Transcribe exactly.
2. **Visuals** — people, products, packaging, scenes, illustrations.
3. **Visual style** — colors, fonts, template, brand consistency.
4. **Which product/service is featured** — read the actual labels and covers in the frame, not the filename. Filenames lie.
5. **Content category** — countdown, announcement, review, promotional, educational, behind-the-scenes.
6. **Platform fit** — from aspect ratio plus content type.

### Step 4 — Write the content brief
Save `video-content-briefs.md` alongside the analysis. Include:
1. **Discoveries** — things filenames could not have told you ("all the review videos feature the flagship product, not the new releases")
2. **Per-category breakdowns** with the actual visible text/quotes
3. **Scheduling recommendations** — lead order, sequences, what to hold back
4. **Caption guidance** — what the caption should ADD versus what's already on screen; never just repeat the visible quote
5. **Summary table** — counts by category, duration, audio, format

This brief is the handoff artifact: content-calendar, social-media-manager, and content-strategy consume it by path instead of re-analyzing the videos. Gaps it reveals feed social-video-producer.

### Step 5 — Verify critical details
- Cross-reference product shots against client records; when frame and filename disagree, trust the frame.
- Partially visible or cut-off text: note it and flag for the operator to verify.
- Check brand consistency against `clients/<slug>/brand/`.

---

## Patterns to Watch For

**Client-provided social graphics:** often silent ~5s animations in FB/IG resolution pairs sharing a template; the product shown may differ from the filename.
**Review/testimonial videos:** identify the exact product reviewed from the frame; transcribe the full quote (gold for captions and site testimonials); note reviewer name and credentials for authority positioning; schedule multi-part reviews together.
**Countdown/launch videos:** verify the sequence is complete; map to calendar dates counting backward from launch day.
**Quote/verse graphics:** transcribe the exact text and attribution; note deliberate pairings of subject and quote; match the caption's tone to the content's register, not a sales register.

## Troubleshooting

- **FFmpeg missing:** `brew install ffmpeg` (macOS) or your package manager.
- **Black frames:** slow fade-in — extract more frames at more timestamps.
- **50+ files:** view only `_mid` frames first, bucket by filename pattern, then deep-dive one representative per bucket.
