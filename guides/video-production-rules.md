# Video Production Rules

Route every video request (reel, ad, demo, explainer, short film, social video) through a `social-video-producer`-style skill and this engine decision tree. The engine numbering below matches that skill's naming: Engine 1 = AI generation, Engine 2 = Remotion motion graphics, Engine 3 = FFmpeg real-footage editing, Engine 4 = Seedance cinematic production.

## Engine Selection Decision Tree

```
Step 1: Does the client have raw footage?
  YES → Engine 3 (FFmpeg editing)
    → Need AI B-roll to fill gaps? Add Engine 1 (hybrid)
  NO → Step 2

Step 2: Is the content primarily text, stats, or graphics?
  YES → Engine 2 (Remotion motion graphics) — free, no API cost
  NO → Step 3

Step 3: Multi-shot cinematic project (5+ shots, character consistency,
        native audio/lip-sync)?
  YES → Engine 4 (Seedance 2.0 cinematic production)
  NO → Step 4

Step 4: Which Engine 1 model fits?
  - Cinematic brand story, high production value → Veo-class (premium) or Sora-class
  - Product demo, lifestyle scene, multi-character → Kling 3.0
  - Fast-turnaround social reel, quick iteration → Kling 3.0 Turbo or Runway
  - Multi-shot with character consistency → Kling 3.0 with an identity/reference lock
  - 3D product visualization, camera paths → Luma Dream Machine
  - Stylized / animated / non-photorealistic → PixVerse
  - Budget volume work (10+ reels, cost-sensitive) → MiniMax Hailuo
```

Validate model availability and parameters against your provider's live catalog before wiring anything — model lineups and constraints change monthly.

## Engine 4: Seedance 2.0 / Cinematic Production

**What it is:** ByteDance's Seedance 2.0 — joint audio-video generation (synchronized sound and visuals in one pass). Native lip-sync, ambient SFX, music-synced motion; that joint-audio capability is the differentiator from standard Engine 1 models.

**Use Engine 4 instead of Engine 1 when:**
- The content needs native lip-sync (dialogue, talking head, spokesperson)
- Music-video or rhythm-synced content
- Ambient sound generated with the visual matters
- Multi-shot cinematic work: 5+ shots with character consistency
- Short films, brand films, cinematic promos

**Access options (free-first):**
1. **Dreamina (free tier):** dreamina.capcut.com — daily credits, watermarked output. Good for iteration.
2. **Fal.ai API:** per-second billing after signup credits — for automation and volume.
3. **Higgsfield (paid platform/CLI):** hosts Seedance alongside Kling/Veo/Hailuo; adds workflow tooling. If you standardize on it, its CLI covers most Engine 1 and Engine 4 work with one auth.

**Workflow:** character/location reference sheets → per-shot prompt (a consistent prompt formula: subject → action → environment → camera → style → constraints) → generate → iterate → export → assemble in FFmpeg/CapCut/DaVinci.

## Cost Tier Rules

- **Always route to the cheapest engine that meets the quality bar.** Don't spend premium-model dollars on a stats reel Remotion renders for free.
- **Remotion is free** and covers anything that is primarily text + graphics + icons — a large share of social reels.
- **FFmpeg is free** — client-supplied footage costs $0 in API spend to edit.
- **Reserve premium models (Veo/Sora-class) for hero content:** homepage videos, paid ad creative, anything that will run for months.
- **Default to Kling/Runway-class models for standard social reels** — good quality at reasonable cost.
- **Flat-rate volume plans (e.g., MiniMax Hailuo's subscription) beat per-second billing** once you're producing 10+ reels a cycle; check current pricing before committing.
- **Budget 2–3 generation attempts per shot.** AI video rarely lands on take one; a 30-second video is roughly 6 shots ≈ 15 generations. Price the batch with your provider's cost estimator before starting.

## Production Stack Rules (all videos)

1. **Captions are mandatory** on every reel unless explicitly skipped — they raise watch time substantially and are an accessibility requirement.
2. **Script/storyboard before generation, approved by the account owner.** Pre-work beats production; never start generating without a signed-off script.
3. **StoryBrand structure on every reel** (`guides/storybrand-framework.md`): hook = the customer's problem (never the business logo), middle = guide + plan, end = CTA + success vision.
4. **Export for every target platform in one pass** — vertical, square, and horizontal as applicable; don't make anyone re-request formats.
5. **Log every video deliverable** in your client records and task tracker when it ships.
6. **Trim the first and last 0.5 seconds of every AI-generated clip** — models produce boundary artifacts.
7. **Switch models after 3 failed attempts on a shot.** Don't burn credits fighting a model; follow a written fallback chain.
8. **Set aspect ratio at generation time, never crop after.** If a model has no aspect-ratio parameter, pillarbox in FFmpeg.
9. **Don't bake text into AI-generated clips** — models still render text poorly. Generate clean video; composite text in post.

## API Key Priority

Use an aggregator (e.g., Fal.ai) as the primary API integration point — one key covers Kling, Veo, and hundreds of other models. Typical minimum keys:

- `FAL_KEY` — video model access
- `OPENAI_API_KEY` — Whisper captions (local Whisper also works free) and Sora if used
- `ELEVENLABS_API_KEY` — voiceover, only if offering narrated content

Platform-native tools (e.g., a vendor CLI with OAuth) may replace some of these; verify with a real call before building on any of them.

## Skill Routing

- "Make a video/reel/ad for [client]" → social-video-producer
- "Create a short film / cinematic video" → social-video-producer, Engine 4
- "Add video animation to a website" → your interactive website builder skill
- "Repurpose this blog post for social" → your content repurposer skill
- "Build a motion graphics intro" → social-video-producer, Engine 2

## Quality Checklist Before Delivery

- [ ] Script follows StoryBrand (opens with the problem, not the logo)
- [ ] Captions present and synced
- [ ] Every text card holds at least 1.5 seconds
- [ ] Aspect ratio matches every target platform
- [ ] Text, faces, logos, CTAs inside platform safe zones (`guides/social-media-safe-zones.md`)
- [ ] Brand colors/fonts match the client's brand guide — no editor defaults
- [ ] CTA clear, in the final 2–3 seconds
- [ ] Audio balanced (voiceover 100%, music 10–15% under it)
- [ ] First/last 0.5s trimmed from AI clips
- [ ] File size under platform limits
- [ ] The account owner has reviewed and approved the final render — extract frames and actually look at them before calling it done
