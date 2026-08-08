# Billboard & Large-Format Outdoor Design Rules

Read this before designing any billboard, roadside panel, yard sign, banner, or wall sign. It replaces designing by eye: every number here traces to a published source, and everything the trade repeats *without* a source is quarantined in §9 as folklore — never to be used in artwork or quoted to a client.

Method note: this guide was built by researching the primary signage-legibility literature first and designing to it, rather than iterating by taste. Keep your underlying research notes (verbatim quotes and URLs) alongside it; where two credible sources disagree, this guide records the conflict rather than silently resolving it.

> **One-line summary:** letter height and word count are decided by published formulas, not taste. Compute them, then design inside the answer.

---

## 1. First: which literature applies?

Two separate research traditions exist, and mixing them produces wrong answers.

| | **On-premise / commercial** | **Highway guide signs** |
|---|---|---|
| Covers | Business signage, roadside panels, 4x8s, wall signs, monuments | DOT directional signage |
| Authority | United States Sign Council (USSC) / USSC Foundation + Penn State PTI (1996–2010) | FHWA / MUTCD |
| Use it for | Everything a marketing agency builds | Reference only |

USSC exists precisely because highway research did not directly transfer to private on-premise signs. **Use the on-premise numbers.** Billboard-operator blog advice is trade practice, not research — treat it accordingly.

---

## 2. Letter Height — the Core Formula

```
Letter height (inches) = Viewing distance (feet) / LI
```

**LI = Legibility Index**: feet of legible distance per inch of *capital* letter height.

### 2.1 Which LI

| LI | Use when | Source |
|---|---|---|
| **30** | Open road, uncongested, good contrast — the on-premise average | USSC, from Penn State test-track research |
| **25** | Moderate congestion (posted <40 mph, on-street parking, tight retail) | USSC environmental factor x0.83 |
| **20** | High congestion (posted <30 mph, signals at most intersections) | USSC environmental factor x0.67 |
| 20–38 | Full measured range across illumination x typeface x color | USSCF Legibility Index table |
| 7 | Extreme observed low in a complex real-world environment | Penn State 2002 |

**Transcription warning:** independent transcription passes of the USSCF Legibility Index table have been observed to disagree on rows within its Internal Opaque block, which shifts the quoted mixed-case advantage between roughly +13–32% and +16–32%. The table is published as a document image and is easy to misread. **Re-read the source table before quoting any specific row.**

**Do not use 50 ft/in** — Penn State's 1998 work explicitly replaced it for on-premise signs. **Do not use FHWA's 40 ft/in** — it belongs to retroreflective highway guide signs, and FHWA's own font report states it in the past tense.

### 2.2 Threshold vs. comfort — read before quoting any distance

**LI 30 is *threshold* legibility, not comfortable reading.** The study behind it assumed an observer who is alert and actively looking for the sign, unfamiliar with it, 20/40 acuity, a perpendicular sign, five or fewer elements, lowercase, unabbreviated. Real drivers meet almost none of that; Penn State's 2002 field study measured legibility falling as low as LI 7 in complex environments — which is why the congestion factors exist.

Separately, reading-speed research finds people read fastest at **2–3x threshold letter height**; the USSC Foundation adopted 3x threshold (effectively LI 10 ft/in) as a design multiplier in its parallel-sign model.

> **Unresolved conflict between credible sources.** One reading: the LI 10 multiplier belongs only to the parallel-sign model, and applying it to a perpendicular panel oversizes letters threefold. The other: the 2–3x reading-speed finding describes human vision, not sign orientation, so threshold-sized copy on a perpendicular sign is equally "technically readable, practically useless." Both readings cite USSCF material.
>
> **Working position until settled:** compute at LI 30/25/20 and call the result the **threshold** distance. State plainly that comfortable reading requires roughly **3x that letter height** (equivalently, comfort arrives at about 1/3 the threshold distance). Report both numbers. **Never quote a single distance as "readable" without saying which one it is.**

### 2.3 Derived letter-height table

Capital letter height required (derived from the formula — the sources publish the formula, not this lookup):

| Viewing distance | LI 30 | LI 25 | LI 20 |
|---|---|---|---|
| 100 ft | 3.3" | 4.0" | 5.0" |
| 200 ft | 6.7" | 8.0" | 10.0" |
| 300 ft | 10.0" | 12.0" | 15.0" |
| 400 ft | 13.3" | 16.0" | 20.0" |
| 500 ft | 16.7" | 20.0" | 25.0" |

Add ~15% if setting ALL CAPS (§4.3).

### 2.4 Wall / parallel signs (different geometry, published lookup)

```
Letter height = (lanes x 10 + lateral offset in feet) / 5
```

Use the **maximum** lane count on the primary target road. Parallel signs only become legible past a ~30° view angle, and in the research drivers missed ~30% of them even when actively looking — and even when the parallel signs were 2–3x larger than the perpendicular comparison. **Perpendicular placement wins.**

---

## 3. How Much Copy Fits — Usually the Binding Constraint

### 3.1 The 40/60 rule (hard)

USSC's minimum standard: negative space must be at least 60% of the sign face. **Copy — letters plus letterspace plus symbols — gets at most 40% of the face.**

### 3.2 Sign area needed

```
A_sign (sq ft) = [ VRT x MPH ]^2 / 800
```

VRT = Viewer Reaction Time in seconds, from the published budget:

| Component | Value |
|---|---|
| Detection | 0.5–1.0 s |
| Message scan | **0.5 s per word** (0.1 s per letter) |
| Symbol / logo / arrow | counts as one word |
| Glance back to road | 0.5 s per 2.5 s of reading (1.0 s if complex) |
| Driving maneuver | 4–6 s — only if the driver must turn in *before* passing the sign |

Published averages assuming six words / 30 letters:

| Road | Pre-sign maneuver | Post-sign |
|---|---|---|
| Simple | 8 s | 4 s |
| Complex | 10 s | 5 s |
| Multi-lane | 11 s | 5 s |

**Worked implication:** at 45 mph, a message requiring a turn-in needs ~162 sq ft of sign. A 4x8 panel is 32 sq ft — it satisfies the standard only around 35 mph with a post-sign maneuver. **A small panel at highway speed is a recognition-and-reinforcement asset; never assign it a turn-in job.**

### 3.3 Word budget — smaller than the trade says

| Basis | Budget |
|---|---|
| USSC published | **4–8 words in ~4 seconds**; six words / 30 letters is their computational standard |
| Measured glance behavior | **1–3 words.** Beijer (2003) measured average glances at outdoor advertising at ~500 ms, with only 22% of glances exceeding half a second; reading one sign word takes 0.5–2.0 s |

**Design to 1–3 words for anything read at speed.** Reserve 4–8 for slow, on-premise, post-sign contexts. The logo counts as a word. "Seven words" is folklore — see §9.

---

## 4. Typography

| Attribute | Spec | Source |
|---|---|---|
| Character width | ≥80% of cap height, target 100% (square); legibility improves monotonically toward square | ADA §703.5.4 (55–110% permitted); Garvey & Mace |
| Stroke width | ADA permits 10–30% of cap height; research converges on 12–20%, sweet spot ~14–18%. **The measured risk is thin, not thick** — a typical Regular weight sits at 8–10%, below the ADA floor; a heavy weight above 20% is acceptable, a light one is not | ADA §703.5.7; Tinker (18%) |
| Letterspacing | 25–35% of cap height between characters; 75–100% between words | Dudek; Woodson; ADA §703.5.8 |
| Line spacing | 135–170% baseline-to-baseline | ADA §703.5.9 |
| x-height | 75% of cap height where a figure is needed | MUTCD 11th Ed. §2A |

Priority order: **character width outranks stroke width, which outranks letterspacing.**

### 4.1 The most damaging common choice: condensed type
Legibility rises as characters approach square; condensing moves the wrong way, and MUTCD makes distortion a hard prohibition (letterforms shall not be stretched, compressed, warped, or otherwise manipulated). **Never condense, never stretch.** Narrow faces with tight tracking are the worst measured combination.

### 4.2 "Always sans-serif" is not supported
The literature's own summary: the bulk of the evidence shows no legibility difference between serif and sans-serif faces. Clarendon — a slab serif — posts the *highest* external-illumination score in the USSCF table. **Judge proportions and stroke weight, not serif presence.** What *is* measured worse: script/handwriting faces, ornate faces, and italic/oblique (ADA prohibits italic outright).

### 4.3 ALL CAPS vs mixed case — advisory, not a gate
USSCF's table shows mixed case winning all 16 measured conditions by +13% to +32%. Against that: FHWA's review judged the mixed-case corpus methodologically confounded and found no overall practical improvement; the Clearview typeface data shows mixed case winning word *recognition* but not raw legibility; and the 2018 reinstatement of Clearview was ordered politically, not by new evidence.

The distinction that matters: mixed case helps when the reader recognizes a word they already know. A sign for a business the driver has never heard of is the unknown-word case, where the advantage shrinks. **Prefer mixed case for multi-word legends; do not treat it as a gate.** Budget ~15% more letter height if you choose caps.

---

## 5. Color and Contrast

### 5.1 Luminance beats hue — the most useful finding in the literature
The research is blunt: luminance contrast matters far more to legibility than color contrast, which only becomes significant when luminance contrast is low — a condition a sign should never be in.

**Convert every proposed color pair to grayscale. If it disappears, no hue will save it.** This is why red-on-green fails: near-identical luminance, maximally different hue.

### 5.2 Which contrast metric — NOT WCAG

| Context | Metric | Threshold |
|---|---|---|
| Printed / reflective signage | `Contrast = [(B1 - B2) / B1] x 100` on light reflectance values (LRV) | **≥65%** (ICC A117.1-2025 §703.2.10.2.2); 70% is trade convention |
| Illuminated / digital / emissive | Luminance ratio, brighter : dimmer | **10:1 to 12:1** (an *optimum*, not a floor) |
| Screens (websites, dashboards) | WCAG `(L1+0.05)/(L2+0.05)` | 4.5:1 — correct standard, but only here |

**WCAG does not transfer to signage.** It measures sRGB relative luminance of a color value, not the light reflectance of a physical material; its +0.05 term models screen flare at desk distance; and 4.5:1 is calibrated for sustained reading at arm's length, not a 500 ms glance at 300 ft. Rough crosswalk: WCAG 4.5:1 ≈ 78% LRV contrast — clears the code floor, but on an illuminated face it is under half the researched optimum.

### 5.3 The famous color ranking is folklore
The widely shared "14 color combinations, black-on-yellow #1" chart has no traceable study — no author, date, method, or distances; it circulates as an image only. Black-on-yellow does not even appear in the real measured dataset, and color rank *flips* with typeface and illumination (Clarendon scores best on yellow/green and worst on white/black under external light; Helvetica the reverse). **There is no typeface-independent color ranking.** Never cite that chart to a client as research; use the USSCF Legibility Index table.

### 5.4 Polarity depends on illumination
Externally lit → dark-on-light wins (black/white ~28–29 vs white/black ~24–26). Internally lit or emissive → light-on-dark wins (up to ~37–38). No universal answer.

---

## 6. Type Over Photography

**No published standard covers this directly**, but three measured findings converge on a strict operational rule:

1. Freyssinier et al. (2003): characters are judged unacceptable once luminance contrast *within* the character's background exceeds ~0.2–0.4 — and a photographic background guarantees the background under a word varies.
2. The sign-research consensus defines required contrast against whatever is actually behind the character, not a nominal color.
3. Akagi et al. (1996): detection distance fell from ~110 ft to ~60 ft moving from low to high visual noise.

The rules that follow:
- **Measure contrast per character against the actual pixels behind it**, at both the darkest and lightest points under the text. An average will pass a half-illegible glyph.
- **A partial gradient scrim does not fix this** — it compresses the range but the range still varies. Use a **solid or near-solid scrim, a color block, or move the type off the image entirely.**
- **No gradient fills on type** — same measured failure.
- **No outline letterforms.** The strongest negative finding in the whole literature: outline characters consistently test less legible than solid ones. The trade habit of "add a thin dark stroke over busy backgrounds" has no research behind it and sits in tension with this finding — a stroke patches a background problem; a scrim removes it.

**Borders help:** the research recommends a border around the sign perimeter, especially in cluttered environments — it makes the sign resolvable as a discrete object. A bleed-to-edge photographic design forfeits a measured conspicuity benefit the trade literature never mentions.

---

## 7. Production

### 7.1 Resolution — effective ppi at FULL SIZE is the only number that matters

```
Effective ppi at full size = document ppi x scale factor
```

"300 dpi" is meaningless until the scale is stated.

| Standard | Effective ppi at full size |
|---|---|
| **OAAA outdoor minimum** | **18–25 ppi** |
| OUTFRONT bulletin spec (rev. 2026) | 25 ppi |
| Lamar poster spec (2017) | 18 ppi |
| Lamar bulletin spec (2017) | 12.5 ppi |
| OAAA transit | 80–100 ppi |
| Banners (read close) | ~200 ppi |

> **Vendor conflict:** for the same 14x48 bulletin, Lamar publishes 12.5 ppi and OUTFRONT publishes 25 — a 2x spread, with Lamar below OAAA's own floor. **Build to 25 and you satisfy everyone.**

OAAA explicitly kills the 300-dpi reflex: aim no higher *or lower* than the published band.

Three conditions when working at the bottom of the band:
1. It must be **real** resolution — upscaled photos take on a painterly quality. **Never run a photo through an upscaler and report the higher number; that is inventing data.**
2. **Type, logos, and hard-edged elements must be vector** — resolution-independent, so the ppi ceiling applies only to the photograph.
3. **The photo must not be the crisp hero at close range.** Scrimming a bottom-of-band photo into a supporting role moves the "must read crisply" job to vector type. If the photo must be a sharp hero, get a better photo, not a bigger file.

For panels up to ~4x8, build at full size: 48x96 inches at 100 ppi is ~46 MP — workable, and it eliminates every scale-conversion error.

### 7.2 Color
- Print → CMYK. Digital/LED boards → RGB.
- Rich black: 50C/50M/50Y/100K (OAAA); some shops publish 50/40/40/100 — use your shop's.
- **No ICC profile is named by OAAA, Lamar, or OUTFRONT.** GRACoL is an offset-litho standard nobody in this chain cites. Ask the shop which output profile their RIP uses for the actual substrate, and hand over against that.
- **Total ink coverage:** there is no published industry ink limit for UV/latex/solvent large format. The oft-quoted 300% figure is SWOP — a heatset web offset spec for magazines — with no authority here. The real limit lives in the shop's RIP media profile: ask. Never use the Registration swatch (400%).
- Saturated golds and oranges shift because they sit outside CMYK gamut — deterministic, not a printer error. **Conflict:** OAAA says convert all spot colors to process; large-format practice says keep the spot name so a 6–8 channel machine can hit it with extended inks. Pre-converting a brand gold throws away the only headroom that could match it — ask how many ink channels the machine has before deciding.
- **Any panel carrying a client's brand color gets a hard proof on the actual substrate**, judged in daylight, never on a monitor. Budget the time and fee.

### 7.3 Bleed and safe area

| Product | Bleed | Safe |
|---|---|---|
| Rigid panel up to 4x8 (ACM) | **0.5"** (see conflict below) | 2" minimum — **plus the frame face width** |
| Small rigid sheet (e.g., 18x12) | **0.125"** (see conflict below) | 0.125" |
| Billboard face | Lamar ~6" / OUTFRONT ~8" — pull the actual panel's spec sheet | ~6" from live area |
| Banner with hems/grommets | per template | 1.5" from edges |

> **Unresolved conflict:** shops publish both 0.5" and 0.125" bleed for the same ACM material. The determinant is the cutting method, and it scales with panel size — a die on an 18x12 holds ±1/16"; a CNC router or shear on a 4x8 does not. Use the figure published by a shop that actually lists your panel's size class, and over-bleed rather than under-bleed.

**What actually eats the edge on a rigid panel — and it isn't print tolerance:** the mounting frame, channel, or Z-bar can cover 3/4"–1.5" of the face, and it does so *after* trimming, so it never shows in a proof. **Get the mounting method in writing before finalizing layout.** This is the most likely way to lose a phone number.

Watch the scale trap: OAAA's "1/2–1 inch of bleed" is stated in **file** inches. At 1"=1' working scale, one file inch equals twelve finished inches — so 1/2–1 file inch is 6–12 inches finished, not 6–12 file inches. Getting this backwards in either direction is the classic large-format error.

### 7.4 Materials — permanent outdoor
- Substrate: 3mm ACM (aluminum composite). Not coroplast — a temporary yard-sign material with no published multi-year outdoor rating.
- Billboard vinyl is a consumable, not permanent — operators warrant 60 days to 2 years and typically require replacement every 12 months.
- **Never quote "7–10 years" for vinyl.** That figure describes *unprinted* film in the mildest climate zone. Printed and laminated, 3M IJ180 warrants roughly 3–6 years in Zone 2 and 2–4 in Zone 3; Avery MPI 1105 with DOL 6460 warrants 5 years vertical on a 1-year product warranty period. 3M does not warrant ink-related fade at all.
- **Quote service life only as: film x laminate x climate zone x exposure angle**, and say whether the number is a warranty or an expected-performance estimate.
- Laminate choice alone can double Zone 2 life (roughly 3 → 6 years) — the biggest single lever.
- "Vertical exposure" means within 15° of vertical. Tilting a panel back toward oncoming traffic roughly halves warranted life. **Mount plumb.**
- UV-flatbed-direct printing has no published durability matrix — get the shop's written warranty naming the ink and any clear coat.

---

## 8. Composition and Message

From the Nielsen/OAAA 2017 study (n=4,020, 10 markets, 36 campaigns) — the main primary effectiveness dataset available:

- Expect 33–62% visually-aided ad recall; ~47% average.
- **In small markets, call-to-action creative out-recalled brand creative 51% vs 46% — and the effect reversed in large markets.** For small-market clients, build around an action.
- Top post-exposure behaviors were all search: ~30% searched online, ~29% visited the website, ~24% searched for the advertiser. The panel's job is to make the business *findable and memorable enough to be searched* — which argues for a recallable, spellable name over a phone number nobody memorizes at 55 mph.
- On logo size, the only evidence-based guidance is a diagnostic, not a fraction: if brand-name recall lags visual recall, increase brand prominence. No source publishes a logo-size rule.

Vendor creative advice (practice, not research): one clear idea, strong silhouette, high contrast, localize the message.

---

## 9. Folklore Register — never use, never quote to a client

Each of these is repeated across the trade with **no primary source found**. Keeping them quarantined here — visibly, with the reason — is part of this guide's value: it prevents them from re-entering the work as "known facts."

1. **"Seven words or fewer" (attributed to OAAA).** OAAA's actual published specs contain formats and pixel ratios only — no word counts. The published figure is 4–8 words at 0.5 s per word; measured glance behavior implies 1–3.
2. **The 14-combination color ranking / "black on yellow is most legible."** No study behind it; the pair isn't in the canonical dataset.
3. **"Always use sans-serif."** Contradicted by the serif research.
4. **"You have 5–7 seconds to read a billboard."** No primary source.
5. **"The logo should be [any fraction] of the board."** No source publishes one.
6. **"High contrast improves outdoor recall by 38%."** No traceable study.
7. **"300% total ink coverage is the large-format limit."** That is SWOP, an offset spec.
8. **"3M/Avery vinyl lasts 7–10 years."** Unprinted film, mildest zone, marketing headline.
9. **"Add a thin dark stroke around text over photos."** Media-owner practice, in tension with the outline-character research.
10. **"Large x-height reads better at distance."** Well-motivated, but no study isolates it; Futura (small x-height) tested equal to the highway standards.
11. **FHWA's 40 ft/in quoted as a *current* MUTCD criterion.** FHWA's own report states it in the past tense.
12. **The 70% LRV contrast "rule."** Universally quoted, but it is trade convention inherited from ADAAG/UFAS practice; the code number is 65% (ICC A117.1-2025). Use 70% as a target, cite 65%.
13. **"Data-driven OOH boosts brand recall 31%."** No traceable study.
14. **"A 14x48 bulletin has a 250 ft minimum viewing distance."** Not confirmable in any OAAA document.
15. **The 1912 newspaper black-on-yellow "experiment."** Second-hand mentions only; unverified.

---

## 10. Pre-Flight Checklist

Run before any outdoor artwork leaves the building.

- [ ] Viewing distance, posted speed, and approach geometry **known, not assumed**
- [ ] Letter height computed from `distance / LI`, LI chosen for the environment
- [ ] **Threshold and comfortable distances both stated** — never a single "readable" number
- [ ] Copy ≤ 40% of face area
- [ ] Word count within budget (1–3 at speed; 4–8 slow/on-premise); logo counts as a word
- [ ] Every color pair checked in grayscale
- [ ] Contrast gated on LRV ≥65% (code floor; 70% is trade convention) or 10:1–12:1 (illuminated) — *not* WCAG
- [ ] Type over photo: per-character contrast at darkest and lightest points; solid scrim, never a gradient
- [ ] No condensed, stretched, italic, script, outlined, or gradient-filled type
- [ ] Character width ≥80% of cap height; stroke inside ADA's 10–30% (target 14–18%)
- [ ] Effective resolution ≥18–25 ppi at full size, real not upsampled; type and logo vector
- [ ] Bleed and safe correct for the substrate — **frame face width confirmed in writing**
- [ ] Mounting plumb (within 15°) and copy above ~5 ft of grade (below that, parked vehicles block it)
- [ ] Border considered
- [ ] Hard proof on the actual substrate ordered for any brand color
- [ ] Service life quoted only as film x laminate x zone x angle, if at all
- [ ] Nothing from §9 appears anywhere in the artwork or client documentation
- [ ] Any regulated-vertical content (financing offers, health claims, legal services) has passed its compliance review before the artwork is shown to anyone
