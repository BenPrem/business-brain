# AI Generation CLI Reference (worked example: Higgsfield)

This file is a **worked example of wrapping a generation vendor's CLI** — image, video, and
3D generation from the command line. The vendor here is Higgsfield; if you use a different
one (fal.ai, Replicate, etc.), keep the doctrine sections and swap the command surface.
The doctrine is the durable part; the model tables are a dated snapshot.

## Why a CLI instead of an MCP server

An MCP server for a generation vendor typically loads 30+ tool schemas into every
session's context permanently, whether or not the session generates anything. A CLI costs
zero context until invoked. For a vendor you use a few times a week, the CLI wins — wrap
it, document it here, and let the agent shell out.

## Param-checking doctrine — read the model before every job

Parameters, constraints, and defaults are **per-model and they change**. The reference
below was read from the vendor's own metadata endpoint on a specific date; treat every
table in this file as stale until re-verified.

```bash
higgsfield model list [--image|--video]   # inventory
higgsfield model get <job_type>           # params, defaults, constraints — READ THIS FIRST
```

Run `model get` before every job — not once per project, every job. Aspect-ratio support,
resolution caps, duration limits, and required flags all vary by model and drift across
vendor updates. Never quote a capability from memory or from this file.

## Cost discipline — price before you generate

```bash
higgsfield generate cost <job_type> --prompt "..."   # returns credits, spends nothing
higgsfield account status                            # current balance
```

Always run the cost estimate before any batch. Per-image cost varies by an order of
magnitude between models (on this vendor, the cheap portrait model ran ~8x cheaper per
image than the multi-reference model), so a batch priced on the wrong assumption blows the
monthly tool budget quietly.

**Not every job type supports cost estimation.** When the estimator returns "unsupported"
for a job type, the spend is UNKNOWN — flag it and get the operator's explicit sign-off
before running, never silently proceed (flag-don't-tune, rule [16] in
`.claude/rules/learned-rules.md`).

## Core commands

```bash
higgsfield generate create <job_type> --prompt "..." [--start-image ./ref.png]
higgsfield generate list | wait <id>
higgsfield upload <file>                  # returns an upload id; local paths auto-upload
higgsfield workflow list | workflow get <name>
```

**Anything that deploys to vendor-controlled infrastructure (site builders, game
exporters) is a deploy** — it needs the same explicit green-light as any production deploy
(rule [34]). Generation commands are ungated; publishing commands are not.

## Headless auth gotchas (generic advice)

- Prefer vendors with token/API-key auth for unattended boxes. If the vendor is
  OAuth-only, the login flow needs a browser once, then stores refreshable credentials.
- **Never override the OAuth callback port.** Only the redirect URI the vendor registered
  (host + port + path) will complete the flow; any other port yields a blank page or a
  silent 400 from the identity provider. If the CLI exposes a `--port` flag, leave it alone.
- **Non-login shells on automation boxes get a bare PATH.** A CLI installed via a package
  manager may resolve fine interactively and fail from cron/ssh — and calling the absolute
  binary path can still fail if its shebang is `#!/usr/bin/env node` and the runtime isn't
  on that bare PATH either. Invoke via `bash -lc "toolname ..."` or prepend the package
  manager's bin dir to PATH explicitly.
- The only valid proof of working auth is an authenticated call returning real account
  data (`account status`), not a stored credentials file existing (rule [22]'s lesson
  applies to CLIs too).

## Native aspect ratio beats post-crop

Ask the model for the target aspect ratio natively:

```bash
higgsfield generate create <video_model> --prompt "..." --aspect-ratio 9:16 --resolution 1080p
```

Only fall back to padding in post when a model has **no** aspect-ratio parameter at all:

```bash
ffmpeg -i clip.mp4 -vf "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0xFFFFFF" out.mp4
```

(An earlier vendor in this seat ignored the aspect-ratio param entirely and always
returned 16:9, which forced pillarboxing on everything — check with `model get` rather
than assuming either behavior.)

## Image-to-video rules

- Client has existing art or photography → **always** image-to-video (`--start-image` /
  image references). Never fall back to text-to-video: it generates new art that doesn't
  match the client's brand.
- Keep i2v prompts **under 30 words**: motion, lighting, atmosphere only. Never describe
  what's already visible in the image — the image does 90% of the work.
- Models that accept both a start and an end image can take the same still for both,
  producing seamless loop videos for website heroes.
- Transparent PNGs are a known hazard on some vendors (alpha renders as black). Flattening
  onto the target background color before upload is a cheap safe default even where
  unverified.

## Model snapshot (dated — re-verify with `model get` before use)

Image: a fast/cheap portrait-quality model (single image reference, trainable character
IDs), a multi-reference model (up to 8 reference images, strong text rendering), a
photoreal generator, an image-editing model, plus background-removal and upscale
utilities.

Video: a quality-default multi-shot model (native 9:16, start/end images, audio
generation, up to 4k), one or two mid-tier models with std/pro modes, a fast/cheap model
**without an aspect-ratio param** (post-pad only), and a video upscaler.

3D: image-to-GLB (PBR, rigging, pose control), multi-image-to-3D for better topology,
text-to-3D, and standalone rigging.

## Asset optimization — generated media is production media

Never ship raw generator output to a website:

```bash
ffmpeg -i in.png -vf "scale='min(1920,iw)':-2" -q:v 80 out.webp                 # multi-MB PNG → tens of KB
ffmpeg -i in.mp4 -c:v libx264 -crf 26 -an -movflags +faststart out.mp4          # small, autoplay-safe
```

Generate the hero video FROM the hero still so poster frame and loop stay visually
continuous.
