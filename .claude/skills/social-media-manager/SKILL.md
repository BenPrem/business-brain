---
name: social-media-manager
description: Write and format day-to-day social media posts for your business or ACTIVE clients with an existing strategy — drafting, hashtags, visuals, posting logistics. Use when the operator says 'post this', 'draft a post about [topic]', 'write this week's posts', or needs a specific post for a specific platform. NOT for planning what to post — use content-calendar; no strategy exists yet — use content-strategy.
---

# Social Media Manager

Draft, format, and manage day-to-day social posts for accounts that already have a
strategy.

## Routing

- Planning what to post → `content-calendar`
- Turning a blog/transcript into multiple posts → `content-repurposer`
- Auditing a prospect's social presence → `social-media-auditor`
- No strategy exists for this account → `content-strategy` first — day-to-day posting
  without pillars and a voice guide produces random content.

---

## Platform-specific rules

### LinkedIn
- **Length:** 150-300 words. The first line is everything — it's all people see before "...see more".
- **Line breaks:** single-line paragraphs, one idea per line; white space = readability.
- **Hook patterns:** bold claim, specific number, counterintuitive insight, question, hot take.
- **Hashtags:** 3-5 at the end, never inline. Mix broad (#marketing) and niche/local.
- **No emojis** unless the account's brand uses them.
- **CTA:** end with a question, "Follow for more [topic]", or "Comment [X] if you want [Y]".
- **Image:** suggest a concept when relevant; carousels earn 2-3x engagement.
- **Never:** open with "I'm excited to...", use "In today's fast-paced...", sound like a brand account.

### X/Twitter
- **Length:** under 280 characters per tweet; threads (3-7 tweets) for deeper topics.
- **Hook:** tweet 1 must stand alone and deliver value by itself.
- **Structure:** one idea per tweet; "→" or numbered lists inside tweets.
- **Threads:** start with the payoff, not the setup.
- **Hashtags:** 1-2 max, or none — hashtag stuffing is penalized.
- **Engagement:** quote tweets beat retweets; reply to comments within 2 hours.
- **Timing:** threads Tue/Thu mornings; singles anytime.

### Instagram
- **Caption:** under 150 words for feed posts; longer allowed for carousel context.
- **First line** = the hook (shows in feed preview before "...more").
- **Hashtags:** 5-10 in a first comment, not the caption; mix sizes (10K-post tags and 1M+ tags).
- **Stories:** casual, behind-the-scenes, polls, questions; 3-7 slides/day when active.
- **Reels:** under 60 seconds, hook in the first 3 seconds, text overlay for sound-off viewing.
- **Visual required:** no text-only posts on Instagram — always suggest the image concept.

### Facebook
- **Length:** 100-250 words for business pages; slightly more conversational than LinkedIn, local flavor welcome.
- **Images:** posts with images get ~2.3x engagement — always include one.
- **Video:** native upload, never external video links — the platform prioritizes native.
- **Groups:** if the client has (or should have) a community group, suggest group posts separately.

---

## Writing process

### Step 1 — Context check
- Read the content calendar for what's planned today
- Read `clients/<client-slug>/brand/brand.md` (client work) or your own voice guide
- Lead with the customer's problem — even social posts follow that narrative rule
- Regulated-topic gate: if the account has a compliance checklist (financing language,
  health claims, legal advertising), every post that touches those topics passes it
  before anyone sees the draft

### Step 2 — Draft
- Write FOR the specific platform — never one post pasted across all platforms
- Hook, body, CTA; suggested visual; recommended hashtags; best posting time

### Step 3 — Present for review
```
DRAFT POST — [Platform] — [Date]
================================
[Full post text]
---
Hashtags: #tag1 #tag2 #tag3
Image suggestion: [concept]
Best time to post: [day, time]
Pillar: [content pillar]
CTA: [the one action asked of the reader]

Ready to post? Or want a different angle?
```

### Step 4 — Log it
After approval and posting, close the <TASK SYSTEM> content task (attach the final
text), and append to the account's content log
(`clients/<client-slug>/deliverables/content/content-log.md` or your venture's
equivalent — `mkdir -p` on first use):
```
| Date | Platform | Topic | Engagement | Notes |
```
Engagement data gets filled in later from platform analytics.

---

## Hashtag research

Build per-account hashtag sets on first use and store them in the account's brand file:
- **Local:** #<City> #<Region> #<City>Business #ShopLocal #SupportLocal
- **Industry:** e.g. restaurants #LocalEats · HVAC #HVACcontractor #HomeServices ·
  dental #DentalMarketing · legal #LawFirmMarketing · real estate #RealtorLife
- **Own-agency:** #DigitalMarketing #SmallBusinessMarketing #WebDesign #MarketingTips

## Batch writing

For "write this week's posts":
1. Pull all open content tasks from <TASK SYSTEM> for the period
2. Write everything in one session, grouped by platform (voice stays consistent,
   variety is visible across the week)
3. Save drafts to `<content-folder>/<YYYY-MM-DD>-batch/`
4. Present a summary of everything drafted

## Reactive posts (timely content)

For "post about [thing that just happened]": write fast — timeliness beats polish.
Short and punchy; connect to the business only if it's natural; on controversial
topics, thoughtful beats hot-take. Draft for the most relevant platform first.

---

## Production principles (apply to every post)

- **Pre-work beats post-production:** before writing, know (1) exactly who this is for,
  (2) what they'll learn or feel, (3) the one action you want.
- **Language beats razzle-dazzle:** "we helped a flooring contractor go from 2 calls a
  week to 14" beats "transform your business with innovative solutions". Concrete
  numbers, names, places — specificity is credibility. Real ones only; never invent.
- **Education-first:** every post teaches something or solves a problem. For business
  audiences, pure education outperforms edutainment.
- **Assume nothing:** write as if the reader has never heard of the business — no
  inside references, no "as you know".
- **Narrow over wide:** one specific reader per post. If it could apply to everyone,
  it applies to no one.
