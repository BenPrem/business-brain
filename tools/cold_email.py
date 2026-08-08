"""
cold_email.py — Cold Email Campaign Builder

Loads qualified lead (deal) records from the workspace pipeline folder
(crm/pipeline/*.md by default — markdown files with YAML-ish frontmatter),
generates personalized cold email copy via tools/openrouter_client.py, and
exports an ESP-agnostic CSV (import it into whatever sending tool you use)
to crm/cold-email-exports/.

Your task system remains the stage/execution layer: after export + send,
update the matching tasks via tools/asana_cli.py (move/comment) and log an
activity note per lead in your CRM.

Writing rules live in .claude/skills/cold-email/SKILL.md. Never send without
the founder's explicit approval.

Usage:
    python3 tools/cold_email.py --list                       # $0 check: show loadable leads
    python3 tools/cold_email.py --niche "HVAC" --limit 5 --dry-run
    python3 tools/cold_email.py --stage "New Lead" --limit 20
    python3 tools/cold_email.py --stage "New Lead" --sender "Alex" --agency "Northside Digital"

Requires:
    - OPENROUTER_API_KEY in .env (via tools/openrouter_client.py)
    - Optionally SENDER_NAME and AGENCY_NAME in .env (or pass --sender/--agency)
"""

import os
import re
import sys
import json
import csv
import time
import argparse
from datetime import date
from dotenv import load_dotenv

# Reuse the shared OpenRouter wrapper (never talks to the API key directly here)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openrouter_client import complete  # noqa: E402

load_dotenv()

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Durable lead records live in the workspace pipeline folder (see the
# lead-scraper skill: the agent writes one record per qualified lead).
DEFAULT_PIPELINE_DIR = os.path.join(REPO_ROOT, "crm", "pipeline")
DEFAULT_EXPORT_DIR = os.path.join(REPO_ROOT, "crm", "cold-email-exports")

SYSTEM_PROMPT_TEMPLATE = """You are a senior cold email strategist writing on behalf of {sender_name} at {agency_name}, a digital marketing agency serving local businesses.

Your philosophy: Cold emails fail because they make the sender the hero. Never do that. The prospect is always the hero. Their problem is the villain. You are the quiet, confident guide who noticed something, has seen this before, and knows how to fix it.

Story roles: Prospect = Hero | Their problem = Villain | {agency_name} = Guide | The audit = The plan | CTA = First step, not a commitment

---

## STEP 1 — PICK THE RIGHT HOOK FORMULA

Read the lead's pain points and choose the best formula. The email must feel like it was written only for this one business.

**Formula 1 — Observation Open** (website issues, mobile problems, outdated tech)
You were on their turf and noticed something real.
Pattern: "[Doing relevant thing] in [city] — [specific thing you noticed]."
Example: "I was looking up HVAC companies in Springfield yesterday — and your site came up."
USE WHEN: Mobile issues, slow load, outdated tech, general site problems.

**Formula 2 — Data Open** (few reviews, rating gap, visible metric problem)
Lead with their own number to reveal the gap.
Pattern: "[Real metric about them] — but [the gap it reveals]."
Example: "Your Google reviews average 4.9 stars. But your website doesn't come up for 'AC repair Springfield.'"
USE WHEN: Lead has very few reviews (< 10) OR has a good rating but a weak online presence. Requires a real data point — never invent one.

**Formula 4 — Compliment Redirect** (strong reviews + weak website)
Start with something genuinely true, pivot to the gap.
Pattern: "[Genuine specific positive] — which is exactly why [the problem] caught my eye."
Example: "Your Google reviews are genuinely impressive — which is why I was surprised your website doesn't reflect that same quality."
USE WHEN: Lead has good ratings (4.5+) but weak site/no website. Never fake the compliment.

**Formula 5 — Problem-First Open** (no website, or very clear provable problem)
Skip the setup. Name the villain in sentence one.
Pattern: "[The specific problem] is [costing them something specific]."
Example: "Your business doesn't have a website — which means every customer who searches for you online finds your competitor instead."
USE WHEN: Lead has NO website. Bold and direct.

**Formula 6 — Story Open** (urgent service businesses: HVAC, plumbing, electrical, emergency services)
A one-sentence micro-story putting them in the shoes of their customer right now.
Pattern: "A [customer type] in [local area] searches for [their service] at [urgent moment] — [what happens on their site]."
Example: "A homeowner in Springfield searches for emergency AC repair at 9pm — your site loads slowly, they hit back, and call your competitor."
USE WHEN: The business handles urgent or time-sensitive calls. Most powerful formula for HVAC, plumbing, electrical.

**Formula 7 — Curiosity Gap Open** (when you want intrigue over directness)
State something incomplete that makes them want to know more.
Pattern: "Found something on your [website/listing] worth [small time investment]."
Example: "Found something on your website worth 5 minutes."
USE WHEN: Pairing with a strong curiosity-gap subject line. Best when the problem is better revealed inside the email.

---

## STEP 2 — WRITE THE EMAIL (in this exact order)

1. **HOOK** — Use the formula you selected. Never start with "I" as the first word. Never open with a compliment unless using Formula 4.

2. **PROBLEM** — Name the villain. Not them — the thing costing them business. Name both:
   - External: the visible, specific issue (slow mobile site, no website, 4 reviews)
   - Internal: what it actually costs them (customers choosing a competitor, losing emergency calls, working hard but being invisible online)
   Use seasons ("a homeowner in July"), local details (their actual city), real scenarios.

   **SECONDARY PAIN POINT RULE:** If the lead has multiple pain points, pick the strongest one for the hook — then weave a second signal into the Problem section to reinforce the same villain. Do NOT introduce a second hook or change subjects. The second pain point should make the primary problem feel bigger, not introduce a new complaint.
   Good: Hook on slow mobile load → Problem mentions "and there's no meta description, so Google isn't sending traffic anyway"
   Bad: Hook on slow mobile load → Problem pivots to "also your reviews are low" (that's a different villain)

3. **STAKES** — What does losing look like? One or two sentences. Real, not dramatic.

4. **CREDIBILITY** — One sentence or three punchy fragments. You've seen this. You've fixed it.
   Good: "Faster sites. More calls. Measurable difference."
   Never invent percentages, dollar figures, or statistics.

5. **CTA** — Free 15-minute website and marketing audit. "No pitch" language required. Tell them what they WON'T get (a sales pitch) and what they WILL get (a clear look at the problem).
   Close with: "Worth a quick look?" / "Curious what we'd find?" / "Want me to show you what I'm seeing?"

6. **SIGN-OFF** — "{sender_name}" only. No "Best regards," no title, no fluff.

---

## STEP 3 — PICK THE MATCHING SUBJECT LINE

After writing the email, choose the subject line category that pairs with your hook formula:

| Hook Used | Best Subject Line Style |
|---|---|
| Formula 1 (Observation) | Specific Observation: "[Business] — your mobile load time" |
| Formula 2 (Data) | Specific Observation or Question: "Your Yelp vs. your Google" |
| Formula 4 (Compliment Redirect) | Curiosity Gap: "Found something on your site" |
| Formula 5 (Problem-First) | Direct Offer: "Free site audit — [Business name]" |
| Formula 6 (Story) | Question or Curiosity Gap: "What's your site doing at 9pm?" |
| Formula 7 (Curiosity Gap) | Curiosity Gap: "Found something on your site worth 5 minutes" |

Subject line rules: All lowercase — no capital letters anywhere, not even the first word. Under 7 words. No exclamation points. No spam words. Feels like a colleague sent it, not a marketing blast.
Examples of correct casing: "your site at 9pm" / "found something on your site" / "springfield hvac — your mobile load"
Examples of wrong casing: "Your Site At 9pm" / "Found Something" / "Quick Question"

---

## TONE RULES
- Write like a sharp human, not a marketer
- Short sentences. One idea per line. White space matters.
- Specificity beats cleverness — city names, seasonal details, industry terms beat generic claims every time
- Never use: "synergy," "leverage," "solutions," "I wanted to reach out," "hope this finds you well," "innovative," "best-in-class," "cutting-edge," "circle back"

## WHAT NOT TO INCLUDE (Touch 1)
- Never invent numbers specific to the prospect's business. If no load speed data appears in the pain points provided, do NOT write "your site takes X seconds" or any specific time/score — you don't know that. Write around the problem without a made-up number.
- Never invent dollar amounts specific to the prospect ("that's a few thousand in lost jobs") — you don't know their pricing.
- General industry statistics are acceptable ("slow mobile sites lose the majority of visitors before they load") but never present them as measured facts about this specific business.
- No "we helped X increase Y by Z%" — that's Touch 2
- No differentiator pitch — that's Touch 3
- No asking for a 30-minute call on first contact

## TARGET LENGTH
Under 75 words. Hard cap. Every sentence must earn its place.

## QUALITY CHECK BEFORE OUTPUTTING
- Did you pick the right hook formula for this lead's specific data?
- Does it name the internal cost, not just the external issue?
- If multiple pain points exist, does the Problem section weave in a second one to reinforce the villain (without introducing a second complaint)?
- Is there zero fabricated data?
- Would you reply to this if you received it cold?

Output valid JSON only, no markdown, no preamble:
{{"subject": "...", "body": "..."}}"""


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Minimal YAML-ish frontmatter parser (no external deps).
    Returns (frontmatter_dict, body). Handles `key: value  # comment` lines."""
    fm = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]
            for line in parts[1].splitlines():
                line = line.strip()
                if not line or line.startswith("#") or ":" not in line:
                    continue
                key, value = line.split(":", 1)
                value = value.strip()
                # strip inline comments (template files carry them)
                if "#" in value:
                    quote_count = value[: value.index("#")].count('"')
                    if quote_count % 2 == 0:
                        value = value.split("#", 1)[0].strip()
                value = value.strip().strip('"').strip("'")
                fm[key.strip().lower()] = value
    return fm, body


def _normalize_stage(stage: str) -> str:
    """Map skill/task-system stage labels onto record stages ('New Lead' -> 'new')."""
    s = (stage or "").strip().lower()
    return {"new lead": "new", "newlead": "new"}.get(s, s)


def load_leads(stage="New Lead", pipeline_dir=None) -> list[dict]:
    """Load deal records at the given stage from the pipeline folder.

    Expected record shape: markdown frontmatter with stage/name plus (added by
    the lead-scraper skill or by hand) industry, location, website, email;
    pain points as a 'Pain points: ...' line in frontmatter notes or anywhere
    in the body.
    """
    pipeline_dir = pipeline_dir or DEFAULT_PIPELINE_DIR
    want = _normalize_stage(stage)
    leads = []
    if not os.path.isdir(pipeline_dir):
        print(f"ERROR: pipeline folder not found: {os.path.normpath(pipeline_dir)}")
        print("Create it (crm/pipeline/) and add one .md record per lead — see the lead-scraper skill.")
        return leads
    for fname in sorted(os.listdir(pipeline_dir)):
        if not fname.endswith(".md") or fname.startswith("_"):
            continue
        path = os.path.join(pipeline_dir, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"  WARN: could not read {fname}: {e}")
            continue
        fm, body = _parse_frontmatter(text)
        if _normalize_stage(fm.get("stage", "")) != want:
            continue
        # Pain points may live in frontmatter notes or the record body.
        notes = fm.get("notes", "")
        if "Pain points:" not in notes and "Pain points:" in body:
            for line in body.splitlines():
                if "Pain points:" in line:
                    notes = (notes + " | " + line.strip()).strip(" |")
                    break
        leads.append({
            "id": os.path.splitext(fname)[0],
            "company": fm.get("name") or os.path.splitext(fname)[0],
            "name": fm.get("name", ""),
            "industry": fm.get("industry", ""),
            "location": fm.get("location", ""),
            "website": fm.get("website", ""),
            "email": fm.get("email", ""),
            "notes": notes or body.strip()[:300],
        })
    return leads


def parse_pain_points(notes: str) -> str:
    """Extract the pain points string from the scraper's notes format."""
    if not notes:
        return ""
    if "Pain points:" in notes:
        # Format: "Score: X/10 | Pain points: A, B, C | Rating: ..."
        after = notes.split("Pain points:")[-1]
        pain = after.split("|")[0].strip()
        return pain
    return notes[:200]  # fallback: use first 200 chars of notes


def parse_rating_info(notes: str) -> tuple[str, str]:
    """Extract rating and review count from scraper notes. Returns (rating, review_count)."""
    if not notes:
        return "", ""
    # Format: "Score: X/10 | Pain points: A, B, C | Rating: 4.9 (49 reviews)"
    rating = ""
    review_count = ""
    if "Rating:" in notes:
        rating_part = notes.split("Rating:")[-1].strip().split("|")[0].strip()
        # rating_part is like "4.9 (49 reviews)" or "4.9 (49 reviews) | ..."
        m = re.match(r"([\d.]+)\s*\((\d+)\s*reviews?\)", rating_part)
        if m:
            rating = m.group(1)
            review_count = m.group(2)
        else:
            m2 = re.match(r"[\d.]+", rating_part)
            if m2:
                rating = m2.group(0)
    return rating, review_count


def generate_email(lead: dict, system_prompt: str) -> dict | None:
    """Generate personalized cold email copy for a single lead via the LLM router."""
    notes = lead.get("notes", "")
    pain_text = parse_pain_points(notes)
    rating, review_count = parse_rating_info(notes)
    has_website = "yes" if lead.get("website") else "no"
    website_line = f" — {lead['website']}" if lead.get("website") else ""

    rating_line = ""
    if rating:
        rating_line = f"\nGoogle rating: {rating}★"
        if review_count:
            rating_line += f" ({review_count} reviews)"

    user_prompt = f"""Business: {lead.get('company') or lead.get('name', 'Unknown')}
Type: {lead.get('industry') or 'local business'}
Location: {lead.get('location') or 'their local area'}
Website: {has_website}{website_line}{rating_line}
Pain points identified: {pain_text or 'needs digital presence improvement'}

Write the subject line and email body now."""

    content = ""
    try:
        # Mid tier: bulk copy generation with quality (see openrouter_client MODELS)
        content = complete(
            user_prompt,
            system=system_prompt,
            tier="mid",
            temperature=0.75,
            max_tokens=400,
        ).strip()

        # Strip any markdown code fences if the model adds them
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        # Extract JSON object
        if "{" in content:
            start = content.index("{")
            end = content.rindex("}") + 1
            content = content[start:end]

        return json.loads(content)

    except json.JSONDecodeError as e:
        # Model sometimes puts literal newlines inside JSON string values (invalid JSON).
        # Fix by replacing newlines that appear inside string values with a space.
        try:
            in_str = False
            chars = []
            for i, c in enumerate(content):
                if c == '"' and (i == 0 or content[i - 1] != '\\'):
                    in_str = not in_str
                chars.append(' ' if (c == '\n' and in_str) else c)
            return json.loads(''.join(chars))
        except Exception:
            print(f"  ERROR parsing JSON response: {e}")
            print(f"  Raw response: {content[:300]}")
            return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def run_campaign_builder(stage="New Lead", niche=None, limit=20, dry_run=False,
                         list_only=False, pipeline_dir=None, out_dir=None,
                         sender_name=None, agency_name=None):
    """Main pipeline: load pipeline leads → generate copy → export CSV."""
    sender_name = sender_name or os.getenv("SENDER_NAME") or "[Your first name]"
    agency_name = agency_name or os.getenv("AGENCY_NAME") or "your agency"
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        sender_name=sender_name, agency_name=agency_name
    )

    leads = load_leads(stage=stage, pipeline_dir=pipeline_dir)
    print(f"Loaded {len(leads)} lead(s) at stage '{stage}'")

    if not leads:
        print("No leads found. Create deal records in crm/pipeline/ (stage: new) — "
              "run the lead-scraper skill first.")
        return

    # Filter by niche if specified
    if niche:
        niche_lower = niche.lower()
        leads = [l for l in leads if niche_lower in (l.get("industry") or "").lower()
                 or niche_lower in (l.get("company") or "").lower()]
        print(f"Filtered to {len(leads)} leads matching niche: {niche}")

    if not leads:
        print(f"No leads found for niche '{niche}'. Try a broader search.")
        return

    leads = leads[:limit]

    if list_only:
        print("\n--list mode ($0 structural check — no API calls, nothing written):")
        for l in leads:
            print(f"  {l['id']} | {l['company']} | {l.get('industry','')} | "
                  f"{l.get('location','')} | website={'yes' if l.get('website') else 'no'}")
        return leads

    print(f"\nGenerating email copy for {len(leads)} leads...\n")

    results = []
    failed = 0

    for i, lead in enumerate(leads, 1):
        company = lead.get("company") or lead.get("name", "Unknown")
        print(f"[{i}/{len(leads)}] {company}...", end=" ", flush=True)

        email_copy = generate_email(lead, system_prompt)

        if email_copy:
            results.append({
                "lead_id": lead["id"],
                "first_name": "",          # fill in manually or via an enrichment tool
                "last_name": "",
                "email": lead.get("email") or "",  # blank if not found
                "company": company,
                "website": lead.get("website") or "",
                "industry": lead.get("industry") or "",
                "location": lead.get("location") or "",
                "subject": email_copy.get("subject", ""),
                "body": email_copy.get("body", ""),
                "pain_points": parse_pain_points(lead.get("notes", "")),
                "source_record": lead["id"],
            })
            print("ok")
        else:
            failed += 1
            print("FAILED")

        # Brief pause to avoid rate limiting
        if i < len(leads):
            time.sleep(0.5)

    # Summary
    print(f"\n{'='*60}")
    print(f"Generated: {len(results)}/{len(leads)} emails  |  Failed: {failed}")
    print(f"{'='*60}\n")

    if not results:
        print("No emails generated. Check your OpenRouter API key.")
        return results

    # Preview top 3
    print("=== PREVIEW (first 3 emails) ===\n")
    for r in results[:3]:
        print(f"Company:  {r['company']}")
        print(f"Subject:  {r['subject']}")
        print(f"Body:\n{r['body']}")
        print(f"Pain pts: {r['pain_points']}")
        print("-" * 50)

    if dry_run:
        print("\nDRY RUN — CSV not saved, nothing else updated.")
        return results

    # Export CSV (ESP-agnostic: subject/body columns import into any sending tool)
    timestamp = date.today().isoformat()
    output_dir = out_dir or DEFAULT_EXPORT_DIR
    os.makedirs(output_dir, exist_ok=True)
    niche_slug = (niche or stage).lower().replace(" ", "-")
    filename = os.path.join(output_dir, f"cold-email-{niche_slug}-{timestamp}.csv")

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "first_name", "last_name", "email", "company",
            "website", "industry", "location",
            "subject", "body", "pain_points", "source_record",
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({k: r[k] for k in writer.fieldnames})

    print(f"\nCSV saved: {os.path.normpath(filename)}")
    print("Next step: fill in the first_name/last_name/email columns before importing")
    print("into your sending tool (use an email-finding service by company + domain).\n")

    print("After send/import is confirmed: move the matching tasks to Contacted and comment via")
    print('  python3 tools/asana_cli.py move --task <gid> --section <contacted-section-gid>')
    print('  python3 tools/asana_cli.py comment --task <gid> --message "Cold email touch 1 sent"')
    print("and log an activity note per lead in your CRM.")

    return results


def main():
    parser = argparse.ArgumentParser(description="Cold Email Campaign Builder")
    parser.add_argument("--stage", default="New Lead",
                        help='Pipeline stage to pull from (default: "New Lead")')
    parser.add_argument("--niche", default=None,
                        help='Filter by industry/niche (e.g. "HVAC", "dental")')
    parser.add_argument("--limit", type=int, default=20,
                        help="Max leads to process (default: 20)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate and preview emails without saving CSV (still calls the LLM)")
    parser.add_argument("--list", action="store_true", dest="list_only",
                        help="List loadable leads and exit — no API calls, nothing written ($0 check)")
    parser.add_argument("--pipeline-dir", default=None,
                        help="Override the pipeline records folder (default: crm/pipeline/)")
    parser.add_argument("--out-dir", default=None,
                        help="Override the CSV export folder (default: crm/cold-email-exports/)")
    parser.add_argument("--sender", default=None,
                        help="Sender first name for the sign-off (or set SENDER_NAME in .env)")
    parser.add_argument("--agency", default=None,
                        help="Agency name for the prompt (or set AGENCY_NAME in .env)")
    args = parser.parse_args()

    run_campaign_builder(
        stage=args.stage,
        niche=args.niche,
        limit=args.limit,
        dry_run=args.dry_run,
        list_only=args.list_only,
        pipeline_dir=args.pipeline_dir,
        out_dir=args.out_dir,
        sender_name=args.sender,
        agency_name=args.agency,
    )


if __name__ == "__main__":
    main()
