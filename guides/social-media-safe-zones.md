# Social Media Safe Zones — Platform UI Overlay Specs

**Scope:** every vertical video (reel, short, story) you produce.
**Source basis:** platform documentation, creator guides, and overlay template analysis, 2025–2026 data (sources listed at the bottom). Re-verify quarterly — platforms move their UI.

Platform interfaces (profile chrome, captions, engagement buttons, navigation) overlay the edges of vertical video and the viewer cannot move them. Any text, face, logo, or CTA placed under that chrome is effectively invisible. Treat these zones as a hard pre-publish gate: check every vertical video against them before it ships.

---

## Canvas

All platforms below share the standard vertical canvas: **1080 x 1920 px (9:16)**.

---

## 1. Instagram Reels (1080 x 1920)

What the UI covers:

| Zone | Pixels from edge | Occupied by |
|------|-----------------|-------------|
| Top | 0–108px | Status bar, nav bar, profile pic, username, follow button |
| Bottom | 1600–1920px (320px tall) | Caption, audio info, scrub bar |
| Right | 960–1080px (120px wide) | Like, comment, share, bookmark, menu |
| Left | mostly clear | keep a 40px buffer |

Safe rectangle: **top 108 / bottom 1600 / left 60 / right 960 → usable 900 x 1492px.**

Placement notes:
- Hook text sits safest 200–600px from the top.
- Keep readable text above 1550px — captions expand upward when a viewer taps "more."
- The right icon stack spans roughly 750–1700px vertically; keep faces and text out of the right 120px through that band.
- CTA text: above 1500px from the top.

---

## 2. TikTok (1080 x 1920)

| Zone | Pixels from edge | Occupied by |
|------|-----------------|-------------|
| Top | 0–140px | Status bar, profile bar, notch/Dynamic Island |
| Bottom | 1596–1920px (324px tall) | Caption bar, sound attribution, engagement row |
| Right | 916–1080px (164px wide) | Like, comment, share, bookmark, more |
| Left | mostly clear | keep a 60px buffer |

Safe rectangle: **top 140 / bottom 1596 / left 60 / right 916 → usable 856 x 1456px.**

Placement notes:
- TikTok has the widest right-side dead zone of any platform (164px) — the icon stack is tall and thick.
- Paid/promoted placements: add ~46px to the bottom buffer (≈370px total) for the CTA button and "Sponsored" label.
- The playlist button added in early 2026 widened the right dead zone by roughly 20px — older templates undershoot it.

---

## 3. YouTube Shorts (1080 x 1920)

| Zone | Pixels from edge | Occupied by |
|------|-----------------|-------------|
| Top | 0–180px | Search, menu, navigation chrome |
| Bottom | 1540–1920px (380px tall) | Channel name, title, music bar; grows when the description opens |
| Right | 960–1080px (120px wide) | Subscribe, like, comment, share, remix |
| Left | mostly clear | keep a 60px buffer |

Safe rectangle: **top 180 / bottom 1540 / left 60 / right 960 → usable 900 x 1360px.**

Placement notes:
- Largest top dead zone (180px) and largest bottom dead zone (380px) of the four platforms.
- The subscribe button grew ~30% in late 2025, so the right-side zone runs wider than older guides claim.
- The bottom zone expands substantially when a viewer opens the description.

---

## 4. Facebook Reels (1080 x 1920)

| Zone | Pixels from edge | Occupied by |
|------|-----------------|-------------|
| Top | 0–60px | Minimal nav chrome |
| Bottom | 1250–1920px (670px tall) | Caption, like/comment/share, audio info — very large |
| Right | inside the bottom cluster | action buttons stack within the bottom zone |
| Left | mostly clear | keep a 65px buffer |

Safe rectangle: **top 60 / bottom 1250 / left 65 / right 1015 → usable 950 x 1190px.**

Placement notes:
- The most aggressive bottom overlay anywhere: 670px, about 35% of the frame.
- Boosted/promoted Reels add a CTA button and eat even more of the bottom.
- Smallest top zone of the four — more headroom is available here than elsewhere.
- The audience skews older; size text slightly larger for readability.

---

## 5. Universal Cross-Platform Safe Zone

When one render will post to multiple platforms, take the most restrictive value per edge:

| Edge | Buffer | Dictated by |
|------|--------|-------------|
| Top | 180px (9.4%) | YouTube Shorts |
| Bottom | keep above 1250px (34.9% from bottom) | Facebook Reels |
| Left | 65px (6%) | Facebook Reels |
| Right | keep left of 916px (15.2% from right) | TikTok |

**Usable area: ~851 x 1070px — about 44% of the frame.** Critical content (text, faces, logos, CTAs) lives inside this rectangle; background imagery and non-essential visuals can run full-bleed to 1080 x 1920.

---

## 6. Restrictiveness Ranking

Smallest to largest usable area:

| Rank | Platform | Usable area | % of frame |
|------|----------|-------------|------------|
| 1 | Facebook Reels | 950 x 1190px | 57.5% |
| 2 | YouTube Shorts | 900 x 1360px | 59.0% |
| 3 | TikTok | 856 x 1456px | 60.1% |
| 4 | Instagram Reels | 900 x 1492px | 64.7% |

---

## 7. FFmpeg QA Overlays

Burn a visible safe-zone rectangle onto a test render before final review. Universal zone:

```bash
ffmpeg -i input.mp4 -vf "drawbox=x=65:y=180:w=851:h=1070:color=red@0.3:t=3" -codec:a copy safe_zone_check.mp4
```

Per-platform:

```bash
# Instagram Reels
ffmpeg -i input.mp4 -vf "drawbox=x=60:y=108:w=900:h=1492:color=green@0.3:t=3" -codec:a copy ig_safe_check.mp4

# TikTok
ffmpeg -i input.mp4 -vf "drawbox=x=60:y=140:w=856:h=1456:color=blue@0.3:t=3" -codec:a copy tt_safe_check.mp4

# YouTube Shorts
ffmpeg -i input.mp4 -vf "drawbox=x=60:y=180:w=900:h=1360:color=yellow@0.3:t=3" -codec:a copy yt_safe_check.mp4

# Facebook Reels
ffmpeg -i input.mp4 -vf "drawbox=x=65:y=60:w=950:h=1190:color=orange@0.3:t=3" -codec:a copy fb_safe_check.mp4
```

(Note: some Homebrew ffmpeg builds ship without `drawbox`/`drawtext` filters — verify with `ffmpeg -filters | grep drawbox` and fall back to a PNG overlay if absent.)

---

## 8. Standard Text Placement

**Hook text (first 1–3 seconds):** centered horizontally, 250–500px from the top — visible on every platform, clear of top nav and bottom overlays. Minimum 48px type; 60–72px preferred for mobile.

**Mid-video value text:** centered, ~540–700px from the top — dead center of every platform's safe area. Minimum 40px.

**CTA (final scene):** centered, 900–1100px from the top — safely above Facebook's bottom overlay while still reading as "low" on screen. Minimum 48px, bold.

**Logos/watermarks:** top-left inside the safe zone (≈70px from left, ≈200px from top), no larger than 120 x 120px — clear of the right-side buttons and top nav, subtle rather than dominant.

---

## Sources

- Outfy: Instagram Safe Zone Guide (2026)
- Zeely: Instagram & TikTok Safe Zones (2026)
- Kreatli: TikTok & YouTube Shorts Safe Zone Guides (2026)
- Orson Lord: Free Safe Zone Overlays for Reels, TikTok, and Shorts (2025)
- PostPlanify: Social Media Safe Zones Complete Guide (2026)
- SendShort: Facebook Reels Dimensions Guide (2026)
- Kapwing: YouTube Shorts Safe Zone Checker (2026)

*Re-verify these zones quarterly; platform UI layouts change.*
