# Auto-Research Methodology for Skill Optimization
**Source:** the "auto-research" pattern from the ML community (autonomous optimization loops originally built for training runs), applied to skill/prompt optimization.

## What Auto-Research Is

Auto-research is an autonomous optimization loop where an agent iteratively improves a process by:
1. Running the process multiple times
2. Evaluating outputs against a standardized test suite
3. Mutating the instructions/prompt
4. Keeping the winner
5. Repeating on a loop (every N minutes, no human in loop)

It applies directly to skill prompts, outreach emails, website performance, landing pages, or any process with a measurable output.

---

## Three Ingredients Required

### 1. Objective Metric (a number you can measure)
- NOT "feels better" or "resonates more" — an actual number
- Examples: eval pass rate (skills), reply rate (outreach), load time in ms (website), conversion rate (landing page)
- For skills: the eval pass rate out of N criteria × M runs

### 2. Measurement Tool (automated, reliable, no human in loop)
- For skills: an eval test suite with binary yes/no assertions, evaluated by a grading agent
- For websites: Lighthouse performance scores
- For emails: your ESP's analytics API (reply rate, open rate)
- Must be automated so it can run hundreds of times without human intervention

### 3. Something to Change (the variable being optimized)
- For skills: the SKILL.md prompt itself (the instructions)
- For websites: the code
- For emails: the copy
- For landing pages: the layout, headlines, CTAs

---

## The Auto-Research Loop

```
[Define eval suite] → [Run skill N times] → [Evaluate all N outputs against test suite]
        ↑                                              ↓
        └──── [Mutate prompt, keep winner] ←── [Score: X out of max]
```

### Concrete implementation for skills:
1. Generate N outputs (e.g., 10 runs of the skill with different inputs)
2. Evaluate each output against M binary criteria
3. Score = total passes out of N × M (e.g., 37/40)
4. Mutate the skill prompt based on what failed
5. Run again, score again
6. Keep whichever prompt version scored higher
7. Repeat every X minutes until score plateaus or hits target

### Key parameters:
- **N (runs per test):** 10 is a good default — enough to capture the distribution without burning too many tokens
- **M (eval criteria):** 3-6 binary criteria per skill. Enough to cover quality, not so many that you're gaming
- **Interval:** 2-5 minutes between cycles for quick skills. Longer for expensive ones
- **Cost estimate:** roughly $0.02/run for cheap models, so 10 runs × 50 cycles ≈ $10 to fully optimize a skill

---

## Eval Design Principles (Critical)

### Use Binary (Yes/No) Evals
- "Is all text legible and grammatically correct?" → YES or NO
- "Does it use the correct color palette?" → YES or NO
- "Is the layout linear (left-to-right or top-to-bottom)?" → YES or NO
- Never use scaled scoring (1-7 Likert scale) — it compounds variability across criteria and runs, making the total score meaninglessly noisy

### Why Binary Works
All AI outputs are distributions. If you run a skill 20 times, you'll get slight variations each time. Binary evals collapse this variability into a clean signal: pass or fail. When you compound scaled scores (e.g., 4 criteria × 7 possible scores each), the total becomes unreliable — a 39/40 one run might be a 28/40 the next, not because the skill changed but because the scorer drifted.

### Don't Make Evals Too Narrow
- BAD: "Must be under 147 words" / "Must not contain the word 'innovative'" / "Must use exactly 3 bullet points"
- GOOD: "Is the language specific and concrete (uses real numbers, names, places)?" / "Does it lead with the customer's problem, not the business's capabilities?"
- If you give the model too many narrow constraints, it'll find ways to technically pass every eval while the actual quality is garbage. It's like a student who memorizes the test answers but doesn't understand the material.

### The Gaming Problem
When evals are too concrete, the model optimizes for the eval, not the quality:
- It'll parrot eval criteria back at you
- It'll technically pass but produce outputs that feel robotic or forced
- This is the AI equivalent of "teaching to the test"

**Fix:** Keep evals focused on outcomes ("Does the reader know what to do next?") not mechanics ("Contains exactly one CTA button with blue background"). The former tests quality; the latter tests compliance.

---

## Why the Research Log Matters

Every optimization cycle produces a log of:
- What the prompt looked like before and after
- What score it got
- Which specific evals it failed
- What changes were tried

This log is an asset. As models get smarter, you can feed the entire log to the new model and it can pick up where the previous one left off. It's accumulated knowledge about what works and what doesn't for YOUR specific use case.

**Save every run.** Even failed experiments contain signal.

---

## Applying Auto-Research Beyond Skills

| Domain | Metric | Measurement Tool | Variable |
|--------|--------|-----------------|----------|
| Skills/Prompts | Eval pass rate | Agent grader + binary test suite | SKILL.md prompt |
| Cold outreach | Reply rate | ESP analytics API | Email copy |
| Website performance | Load time (ms) | Lighthouse / PageSpeed Insights | Code changes |
| Landing pages | Conversion rate | Analytics + A/B testing | Layout, copy, CTAs |
| Video thumbnails | Click-through rate | Platform analytics | Thumbnail design |
| Ad copy | Cost per click | Ad platform analytics | Ad text/creative |

---

## Implementation Checklist

### Quick-start for optimizing any skill:
1. Pick the skill to optimize
2. Define 3-6 binary eval criteria (what makes a "good" output?)
3. Create test inputs (different realistic scenarios the skill would face)
4. Run 10 outputs per cycle
5. Score all outputs against eval criteria
6. Mutate the prompt based on failures
7. Keep the winner, repeat
8. Stop when score plateaus or hits 90%+

### Prioritize by revenue impact:
Optimize the skills closest to money first — outreach copy (reply rate → meetings → revenue), proposals (close rate), client deliverable quality (retention). Internal convenience skills last.

### Cost-efficiency note:
Use cheap models for the grading agent when possible. The skill itself runs at its specified tier, but the eval/grading step can be much cheaper since it's just checking binary criteria.
