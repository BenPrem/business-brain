# Advanced Agent Patterns

Reference doc for parallelization, agent teams, diversification, and orchestration patterns. Derived from advanced Claude Code usage.

---

## Why Parallelization Matters

1. **Time savings** — Autonomous agents take 5-15+ minutes on complex tasks. Parallelizing can cut that by 40-60%.
2. **Quality through stochasticity** — Models don't return the same answer twice. Running the same query 5x gives you 2-3x more unique solutions than running it once.
3. **Context window hygiene** — Performance degrades as context grows. Sub-agents start with fresh, short contexts — they stay in the "zone of good."
4. **Cost optimization** — Use cheap models for research, expensive models only for synthesis. Matches the tiered model-routing rule in `business-rules.md`.

---

## Three Core Parallelization Patterns

### 1. Fan Out / Fan In (Research → Synthesis)

**When to use:** Research tasks, competitor analysis, API evaluation, any task requiring broad information gathering.

**How it works:**
- Spawn N research sub-agents (use cheaper models)
- Each researches independently with its own fresh context
- A synthesizer agent (use a top-tier model) combines all results
- Synthesizer has a different prompt: "Here's research from N agents — integrate overlaps, score outliers"

**Examples:**
- Prospect workup competitor phase: fan out 5 cheap agents to scrape 5 competitors simultaneously, then a top model synthesizes the comparison matrix
- Content research: fan out researchers to find data on a client's industry, synthesize into a strategy brief

**Key benefit:** 5 minutes of parallel research + 5 minutes synthesis = 10 minutes total vs. 25 minutes serial.

### 2. Debate / Stochastic Consensus

**When to use:** Decision-making, strategy development, nuanced problem-solving where you want to explore the full solution space.

**How it works:**
- Spawn N agents with the same or slightly varied prompts (different "personas" — conservative, aggressive, contrarian, first-principles, etc.)
- Each generates independent solutions
- **Consensus step:** Count frequency of each solution across agents. High-frequency = high-confidence. Low-frequency = interesting outlier.
- **Optional debate rounds:** Let agents see each other's answers, then regenerate. Solutions get more nuanced each round.

**Examples:**
- Outreach copy optimization: run 10 variations, use consensus to find which hooks/CTAs appear most often
- Pricing strategy: have agents argue from different angles (value-based, competitive, ROI-focused) before synthesizing

**Key benefit:** Covers more of the solution space. Finds both the statistically likely answers AND the creative outliers.

### 3. Pipeline (Sequential Specialist Handoff)

**When to use:** Multi-phase builds where each phase needs a different mindset (dev → QA → deploy).

**How it works:**
- Agent A (Developer) builds the feature
- Agent B (QA/reviewer) reviews with fresh eyes — no bias from building it
- Agent C (Testing) runs automated checks
- Loop between B and A until quality passes

**Examples:**
- Demo website build: dev agent builds the site → QA agent reviews against your copy framework checklist → dev agent fixes → deploy agent handles the host
- Proposal generation: research agent gathers data → writer agent drafts → reviewer agent checks against workup rules

---

## Practical Agent Team Configurations

### Recommended: Parent + Researcher + QA (Lean but effective)

```
        TOP MODEL (Parent/Orchestrator)
           /              \
    CHEAP (Researchers)    TOP (QA Agent)
    [fan out for research]  [fresh context, no dev bias]
```

- Parent orchestrates and develops
- Researchers (cheap tier) handle data gathering — cheap, fast, good enough
- QA agent (top tier) reviews with zero context about the build process — catches things the parent is biased toward missing
- This is the sweet spot: covers 90% of use cases without over-complicating

### Minimal: Developer + QA (Two-agent loop)

```
    DEV agent ←→ QA agent (fresh spawn each time)
```

- Dev agent builds, then spawns a fresh QA agent after each feature
- QA agent has NO context about the project — reads code cold
- Returns feedback, dev incorporates, loop until QA passes
- Simpler but still catches the majority of issues

### Avoid: Deep org charts (CEO → CTO → Engineers → QA → etc.)

- Every additional agent layer compounds error probability (0.9^N)
- More layers = more token cost, more time, more drift from intent
- The further an agent is from the human, the more diluted the results
- Keep it lean: 2-3 layers maximum

---

## Diversification Strategy (Anti-Monoculture)

### The Problem
Relying 100% on any one provider creates fragility. When your primary model provider goes down (and it does — outages happen), your entire productivity drops to zero.

### The 70/30 Rule
- **70% primary harness** — your main workhorse
- **30% distributed** across alternatives: a second frontier provider, a multi-model router, and local models for offline fallback and privacy-sensitive tasks

### How to Diversify in Practice

1. **Keep workspace format agnostic** — Don't put everything in `.claude/` exclusively. Maintain parallel agent configs (`CLAUDE.md` plus an `AGENTS.md` or equivalent for other harnesses) and sync them periodically so switching is instant.
2. **Use MCP servers for cross-model orchestration** — delegate to a second harness within the same session when your primary model is degraded but the harness still runs.
3. **Parallel-workspace tools** — platforms that run multiple agent harnesses in isolated workspaces hedge performance fluctuations.
4. **Know your fallback** — Have the alternative installed, configured, and tested BEFORE you need it. Don't scramble during an outage.

### Application
- Primary: Claude Code for daily operations (this workspace)
- Fallback: keep a multi-model router key active — route bulk tasks to alternative models if the primary is degraded
- For client work: never promise delivery timelines that assume zero model downtime. Build in a 20% buffer.

---

## The "How Could You Have Done This Faster?" Feedback Loop

After any completed task, ask the agent: **"How could you have arrived at these conclusions and done everything I just asked you to do faster and for fewer tokens?"**

This generates concrete optimization insights:
- "I made 20 sequential edits when I could have done one full file rewrite"
- "I fetched a well-known site when I already had that knowledge"
- "I could have used sub-agents for the research instead of doing it serially"

Compile these learnings and update CLAUDE.md. This is the local workflow loop that makes every subsequent task faster.

---

## Related Files
- `references/auto-research-methodology.md` — The auto-research optimization loop
- `.claude/rules/learned-rules.md` — Running log of failures and successes
- `CLAUDE.md` — Self-Improvement section
