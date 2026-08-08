"""
competitor_analyzer.py — Competitor Analysis Tool

Finds 4-5 competitors for a prospect, scrapes their websites, and builds
a feature comparison matrix. Phase 2 of the prospect workup pipeline
(see tools/prospect_workup.py and .claude/skills/prospect-workup/SKILL.md).

Usage:
    python3 tools/competitor_analyzer.py --business "Example HVAC" --location "Springfield, IL"
    python3 tools/competitor_analyzer.py --business "Main Street Dental" --location "Springfield, IL" --limit 5
    python3 tools/competitor_analyzer.py --business "Example HVAC" --location "Springfield, IL" --dry-run

Requires (env vars only — see guides/connecting-tools.md; never hardcode values):
    - GOOGLE_PLACES_API_KEY    (Places API New + PageSpeed Insights)
    - FIRECRAWL_API_KEY        (competitor site scraping)
    - OPENROUTER_API_KEY       (analysis synthesis via tools/openrouter_client.py)
    - pip install requests python-dotenv
"""

import os
import sys
import json
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests python-dotenv")
    sys.exit(1)

# Add tools directory for imports
sys.path.insert(0, os.path.dirname(__file__))
from openrouter_client import complete_cheap

load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
PLACES_BASE = "https://places.googleapis.com/v1"
FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"

CLIENTS_DIR = Path(__file__).parent.parent / "clients"


def find_competitors(business_name, location, niche=None, limit=5):
    """
    Find competitors using the Google Places API. Searches for similar
    businesses in the same area, excluding the prospect itself.
    """
    # Infer niche from business name if not provided
    if not niche:
        niche = complete_cheap(
            f"What type of business is '{business_name}'? Reply with just the industry category "
            f"(e.g., 'HVAC', 'dental', 'restaurant', 'flooring'). One or two words only.",
        ).strip().strip('"').strip("'")

    print(f"Searching for {niche} competitors near {location}...")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.formattedAddress,"
            "places.nationalPhoneNumber,places.websiteUri,places.rating,"
            "places.userRatingCount,nextPageToken"
        ),
    }

    body = {
        "textQuery": f"{niche} in {location}",
        "pageSize": min(20, limit * 3),  # Over-fetch to filter out the prospect
    }

    resp = requests.post(f"{PLACES_BASE}/places:searchText", headers=headers, json=body)
    data = resp.json()

    if resp.status_code != 200:
        print(f"ERROR: Google Places returned {resp.status_code}")
        return [], niche

    places = data.get("places", [])

    # Filter out the prospect itself (fuzzy match on name)
    prospect_lower = business_name.lower()
    competitors = []
    for place in places:
        name = place.get("displayName", {}).get("text", "")
        if prospect_lower in name.lower() or name.lower() in prospect_lower:
            continue  # Skip the prospect itself
        competitors.append({
            "name": name,
            "address": place.get("formattedAddress", ""),
            "phone": place.get("nationalPhoneNumber", ""),
            "website": place.get("websiteUri", ""),
            "rating": place.get("rating", 0),
            "reviews": place.get("userRatingCount", 0),
        })

    return competitors[:limit], niche


def scrape_competitor(competitor):
    """Scrape a single competitor's website via Firecrawl. Returns enriched dict."""
    url = competitor.get("website", "")
    if not url or not FIRECRAWL_API_KEY:
        competitor["scrape_status"] = "no_website" if not url else "no_api_key"
        competitor["features"] = {}
        return competitor

    try:
        resp = requests.post(
            f"{FIRECRAWL_BASE}/scrape",
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"url": url, "formats": ["markdown", "html"]},
            timeout=20,
        )

        if resp.status_code != 200:
            competitor["scrape_status"] = f"error_{resp.status_code}"
            competitor["features"] = {}
            return competitor

        data = resp.json().get("data", {})
        content = data.get("markdown", "") or ""
        html = data.get("html", "") or ""
        metadata = data.get("metadata", {}) or {}
        html_lower = html.lower()

        # Extract features by checking for common patterns
        competitor["features"] = {
            "has_online_booking": any(kw in html_lower for kw in [
                "book now", "schedule", "calendly", "acuity", "cal.com",
                "book online", "appointment", "book a time",
            ]),
            "has_chat_widget": any(kw in html_lower for kw in [
                "livechat", "intercom", "drift", "crisp", "tawk",
                "chat with us", "messenger", "chatbot",
            ]),
            "has_reviews_displayed": any(kw in html_lower for kw in [
                "testimonial", "review", "★", "star rating", "google review",
                "customer said", "what our clients",
            ]),
            "has_blog": any(kw in html_lower for kw in [
                "/blog", "blog post", "articles", "news", "insights",
            ]),
            "has_social_links": any(kw in html_lower for kw in [
                "facebook.com", "instagram.com", "twitter.com", "x.com",
                "linkedin.com", "youtube.com", "tiktok.com",
            ]),
            "has_financing": any(kw in html_lower for kw in [
                "financing", "payment plan", "credit", "affirm", "klarna",
                "pay over time",
            ]),
            "has_ssl": url.startswith("https://"),
            "has_mobile_viewport": "width=device-width" in html_lower,
            "has_schema": "schema.org" in html_lower or "application/ld+json" in html_lower,
            "has_meta_description": bool(metadata.get("description", "").strip()),
            "page_count_estimate": html_lower.count("<a href") // 3,  # Rough estimate
        }

        # Get PageSpeed score
        competitor["pagespeed"] = _check_pagespeed(url)
        competitor["scrape_status"] = "success"
        competitor["content_preview"] = content[:500]

    except Exception as e:
        competitor["scrape_status"] = f"exception: {str(e)[:100]}"
        competitor["features"] = {}

    return competitor


def _check_pagespeed(url):
    """Check mobile PageSpeed score. Returns dict or None."""
    if not url or not GOOGLE_PLACES_API_KEY:
        return None
    try:
        resp = requests.get(
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params={"url": url, "strategy": "mobile", "key": GOOGLE_PLACES_API_KEY, "category": "performance"},
            timeout=20,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score")
        fcp = data.get("lighthouseResult", {}).get("audits", {}).get("first-contentful-paint", {}).get("numericValue")
        if score is None:
            return None
        return {"score": round(score * 100), "load_seconds": round(fcp / 1000, 1) if fcp else None}
    except Exception:
        return None


def build_comparison_matrix(prospect_data, competitors, niche):
    """
    Use LLM to synthesize the scraped data into a comparison matrix
    and competitive analysis report.
    """
    # Build structured input for the LLM
    comp_summaries = []
    for i, c in enumerate(competitors, 1):
        features = c.get("features", {})
        ps = c.get("pagespeed", {}) or {}
        comp_summaries.append(
            f"Competitor {i}: {c['name']}\n"
            f"  Website: {c.get('website', 'None')}\n"
            f"  Rating: {c.get('rating', 'N/A')}★ ({c.get('reviews', 0)} reviews)\n"
            f"  Mobile Speed: {ps.get('score', 'N/A')}/100 ({ps.get('load_seconds', '?')}s)\n"
            f"  Online Booking: {'Yes' if features.get('has_online_booking') else 'No'}\n"
            f"  Chat Widget: {'Yes' if features.get('has_chat_widget') else 'No'}\n"
            f"  Reviews Displayed: {'Yes' if features.get('has_reviews_displayed') else 'No'}\n"
            f"  Blog/Content: {'Yes' if features.get('has_blog') else 'No'}\n"
            f"  Social Links: {'Yes' if features.get('has_social_links') else 'No'}\n"
            f"  Financing Options: {'Yes' if features.get('has_financing') else 'No'}\n"
            f"  SSL (HTTPS): {'Yes' if features.get('has_ssl') else 'No'}\n"
            f"  Mobile Responsive: {'Yes' if features.get('has_mobile_viewport') else 'No'}\n"
            f"  Schema/SEO: {'Yes' if features.get('has_schema') else 'No'}\n"
            f"  Meta Description: {'Yes' if features.get('has_meta_description') else 'No'}\n"
        )

    prospect_features = prospect_data.get("features", {})
    prospect_ps = prospect_data.get("pagespeed", {}) or {}

    prompt = f"""You are a competitive analysis expert for a digital marketing agency.

Analyze the following {niche} businesses in their local market and produce a competitive analysis report.

## THE PROSPECT (our potential client):
Name: {prospect_data.get('name', 'Unknown')}
Website: {prospect_data.get('website', 'None')}
Rating: {prospect_data.get('rating', 'N/A')}★ ({prospect_data.get('reviews', 0)} reviews)
Mobile Speed: {prospect_ps.get('score', 'N/A')}/100
Online Booking: {'Yes' if prospect_features.get('has_online_booking') else 'No'}
Reviews Displayed: {'Yes' if prospect_features.get('has_reviews_displayed') else 'No'}
Social Links: {'Yes' if prospect_features.get('has_social_links') else 'No'}
Schema/SEO: {'Yes' if prospect_features.get('has_schema') else 'No'}

## COMPETITORS:
{chr(10).join(comp_summaries)}

## OUTPUT FORMAT (Markdown):

# Competitive Analysis: [Prospect Name] vs. Local {niche} Market

## Executive Summary
2-3 sentences: Where the prospect stands vs. their competition. What's the biggest gap?

## Feature Comparison Matrix
| Feature | [Prospect] | [Competitor 1] | [Competitor 2] | ... |
Use checkmarks (✓) and X marks (✗).

## Competitor Breakdown
For each competitor, 2-3 sentences: What they're doing well, what they're doing better than the prospect, and any weaknesses.

## Prospect's Competitive Gaps
Numbered list of specific things the prospect is missing that competitors have. Rank by business impact.

## Opportunities
What the prospect could do to leapfrog the competition. Be specific — don't say "improve SEO", say "add local schema markup and business-profile optimization to appear in map pack results."

## Threat Assessment
Which competitors are the biggest threat and why? Who is actively investing in their digital presence?
"""

    return complete_cheap(prompt, max_tokens=4000)


def run_analysis(business_name, location, limit=5, dry_run=False, output_dir=None):
    """Main analysis pipeline."""
    print(f"\n{'='*60}")
    print(f"Competitor Analysis: {business_name} ({location})")
    print(f"{'='*60}\n")

    # Step 1: Find competitors
    competitors, niche = find_competitors(business_name, location, limit=limit)
    if not competitors:
        print("No competitors found. Try a different location or business name.")
        return None

    print(f"\nFound {len(competitors)} competitors ({niche}):")
    for i, c in enumerate(competitors, 1):
        print(f"  {i}. {c['name']} — {c.get('website', 'No website')} ({c.get('rating', 'N/A')}★)")

    if dry_run:
        print("\nDRY RUN — skipping scraping and analysis.")
        return {"competitors": competitors, "niche": niche}

    # Step 2: Scrape the prospect's own site (for comparison)
    print("\nScraping prospect and competitors...")
    prospect_data = {
        "name": business_name,
        "website": None,  # Will be filled by Phase 1 research
        "features": {},
    }

    # Scrape all competitors in parallel (3 threads to respect rate limits)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(scrape_competitor, c): c for c in competitors}
        scraped_competitors = []
        for future in as_completed(futures):
            result = future.result()
            status = result.get("scrape_status", "unknown")
            print(f"  Scraped: {result['name']} ({status})")
            scraped_competitors.append(result)

    # Step 3: Build comparison matrix with LLM
    print("\nBuilding comparison matrix...")
    report = build_comparison_matrix(prospect_data, scraped_competitors, niche)

    # Step 4: Save output
    if output_dir:
        out_path = Path(output_dir)
    else:
        slug = business_name.lower().replace("'", "").replace(" ", "-").replace(".", "")
        out_path = CLIENTS_DIR / slug / "research"

    out_path.mkdir(parents=True, exist_ok=True)
    report_file = out_path / "competitor-analysis.md"
    report_file.write_text(report)
    print(f"\nReport saved: {report_file}")

    # Save raw data as JSON for use by other phases
    raw_data = {
        "prospect": prospect_data,
        "competitors": scraped_competitors,
        "niche": niche,
    }
    data_file = out_path / "competitor-data.json"
    data_file.write_text(json.dumps(raw_data, indent=2, default=str))
    print(f"Raw data saved: {data_file}")

    return {"report": report, "data": raw_data, "report_file": str(report_file)}


def main():
    parser = argparse.ArgumentParser(description="Competitor Analyzer")
    parser.add_argument("--business", required=True, help="Prospect business name")
    parser.add_argument("--location", required=True, help="City, State")
    parser.add_argument("--limit", type=int, default=5, help="Number of competitors (default: 5)")
    parser.add_argument("--output", default=None, help="Output directory (default: clients/[slug]/research/)")
    parser.add_argument("--dry-run", action="store_true", help="Find competitors without scraping")
    args = parser.parse_args()

    run_analysis(
        business_name=args.business,
        location=args.location,
        limit=args.limit,
        dry_run=args.dry_run,
        output_dir=args.output,
    )


if __name__ == "__main__":
    main()
