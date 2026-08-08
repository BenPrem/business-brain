"""
lead_scraper.py — places-API lead finder + digital-weakness scorer.

Finds local businesses by niche + location using the Google Places API (New),
scores them for digital weakness (how much they need marketing help), and
optionally scrapes their website via Firecrawl for deeper signals.

This tool only SCORES. It writes nothing to your CRM or task system — the
agent (or you) creates one pipeline record and one "New Lead" task per
qualified lead, then verifies the writes. See .claude/skills/lead-scraper/SKILL.md.

Usage:
    python3 tools/lead_scraper.py --niche "HVAC" --location "Springfield, IL" --limit 20
    python3 tools/lead_scraper.py --niche "restaurants" --location "Springfield, IL" --limit 50 --min-score 4
    python3 tools/lead_scraper.py --niche "dentist" --location "Springfield, IL" --dry-run

Requires (env vars only — see guides/connecting-tools.md):
    - GOOGLE_PLACES_API_KEY    (Places API New + PageSpeed Insights)
    - FIRECRAWL_API_KEY        (optional — website scraping for weakness signals)
"""

import os
import sys
import time
import argparse
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip3 install requests python-dotenv")
    sys.exit(1)

load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
PLACES_BASE = "https://places.googleapis.com/v1"
FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"

# Industry mapping for CRM records
INDUSTRY_MAP = {
    "hvac": "HVAC",
    "heating": "HVAC",
    "air conditioning": "HVAC",
    "dentist": "Healthcare",
    "dental": "Healthcare",
    "doctor": "Healthcare",
    "medical": "Healthcare",
    "chiropractor": "Healthcare",
    "lawyer": "Legal",
    "attorney": "Legal",
    "legal": "Legal",
    "real estate": "Real Estate",
    "realtor": "Real Estate",
    "restaurant": "Restaurant",
    "cafe": "Restaurant",
    "diner": "Restaurant",
    "retail": "Retail",
    "shop": "Retail",
    "store": "Retail",
    "plumber": "Home Services",
    "roofing": "Home Services",
    "landscaping": "Home Services",
}


def get_industry(niche):
    niche_lower = niche.lower()
    for keyword, industry in INDUSTRY_MAP.items():
        if keyword in niche_lower:
            return industry
    return "Other"


def search_places(niche, location, limit=20):
    """Search the Places API (New) for businesses matching niche + location."""
    if not GOOGLE_PLACES_API_KEY:
        print("ERROR: GOOGLE_PLACES_API_KEY not set (see guides/connecting-tools.md)")
        sys.exit(1)

    print(f"\nSearching Google Places: '{niche}' in '{location}'...")

    results = []
    next_page_token = None
    query = f"{niche} in {location}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,nextPageToken",
    }

    while len(results) < limit:
        body = {"textQuery": query, "pageSize": min(20, limit - len(results))}
        if next_page_token:
            body["pageToken"] = next_page_token
            time.sleep(2)

        resp = requests.post(f"{PLACES_BASE}/places:searchText", headers=headers, json=body)
        data = resp.json()

        if resp.status_code != 200:
            print(f"ERROR from Google Places: {resp.status_code} — {data.get('error', {}).get('message', str(data))}")
            break

        batch = data.get("places", [])
        results.extend(batch)
        print(f"  Found {len(batch)} businesses (total: {len(results)})")

        next_page_token = data.get("nextPageToken")
        if not next_page_token or len(results) >= limit:
            break

    return results[:limit]


def get_place_details(place):
    """Extract details from a Places API (New) result object."""
    return {
        "name": place.get("displayName", {}).get("text", ""),
        "formatted_address": place.get("formattedAddress", ""),
        "formatted_phone_number": place.get("nationalPhoneNumber", ""),
        "website": place.get("websiteUri", ""),
        "rating": place.get("rating", 0),
        "user_ratings_total": place.get("userRatingCount", 0),
    }


def score_lead(details, scraped=None):
    """
    Score a business for how much they need marketing help.
    Higher score = better lead (more pain points = more opportunity).
    Max score: 10
    """
    score = 0
    reasons = []

    # No website — biggest signal
    if not details.get("website"):
        score += 4
        reasons.append("No website")
    else:
        # Has website but it might be outdated
        score += 1
        if scraped:
            # Mobile load speed — most compelling pain point (real number)
            ps = scraped.get("pagespeed")
            if ps:
                ps_score = ps.get("score", 100)
                load_sec = ps.get("load_seconds")
                if ps_score < 50:
                    score += 3
                    label = f"Slow mobile load ({load_sec}s, score {ps_score}/100)" if load_sec else f"Slow mobile load (score {ps_score}/100)"
                    reasons.append(label)
                elif ps_score < 75:
                    score += 1
                    label = f"Below-average mobile speed ({load_sec}s, score {ps_score}/100)" if load_sec else f"Below-average mobile speed (score {ps_score}/100)"
                    reasons.append(label)

            # Check for mobile issues, old tech, low content
            if scraped.get("old_tech"):
                score += 2
                reasons.append("Outdated website technology")
            if scraped.get("not_mobile"):
                score += 2
                reasons.append("Not mobile-friendly")
            if scraped.get("thin_content"):
                score += 1
                reasons.append("Thin website content")
            # SEO signals
            if scraped.get("no_meta_description"):
                score += 1
                reasons.append("No meta description (SEO gap)")
            if scraped.get("no_schema"):
                score += 1
                reasons.append("No structured data / schema (SEO gap)")

    # Low rating or few reviews — social proof gap
    rating = details.get("rating", 0)
    review_count = details.get("user_ratings_total", 0)

    if review_count < 10:
        score += 2
        reasons.append(f"Very few reviews ({review_count})")
    elif review_count < 50:
        score += 1
        reasons.append(f"Low review count ({review_count})")

    if rating and rating < 4.0:
        score += 1
        reasons.append(f"Low rating ({rating}★)")

    return score, reasons


def check_page_speed(url):
    """
    Check mobile load speed via Google PageSpeed Insights API (free).
    Returns dict with score (0-100), load_seconds, or None on failure.
    Uses the same GOOGLE_PLACES_API_KEY — no extra setup needed.
    """
    if not url or not GOOGLE_PLACES_API_KEY:
        return None
    try:
        resp = requests.get(
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params={
                "url": url,
                "strategy": "mobile",
                "key": GOOGLE_PLACES_API_KEY,
                "category": "performance",
            },
            timeout=20,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        categories = data.get("lighthouseResult", {}).get("categories", {})
        audits = data.get("lighthouseResult", {}).get("audits", {})

        score = categories.get("performance", {}).get("score")
        fcp = audits.get("first-contentful-paint", {}).get("numericValue")  # ms

        if score is None:
            return None

        score_int = round(score * 100)
        load_seconds = round(fcp / 1000, 1) if fcp else None
        return {"score": score_int, "load_seconds": load_seconds}
    except Exception:
        return None


def scrape_website(url):
    """Use Firecrawl to scrape a website and check for digital weakness signals."""
    if not url or not FIRECRAWL_API_KEY:
        return None

    try:
        resp = requests.post(
            f"{FIRECRAWL_BASE}/scrape",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"},
            json={"url": url, "formats": ["markdown", "html"]},
            timeout=15,
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        content = data.get("data", {}).get("markdown", "") or ""
        html = data.get("data", {}).get("html", "") or ""
        metadata = data.get("data", {}).get("metadata", {}) or {}

        content_lower = content.lower()
        html_lower = html.lower()

        # Simple heuristics for digital weakness
        result = {
            "old_tech": False,
            "not_mobile": False,
            "thin_content": len(content) < 500,
            "no_meta_description": False,
            "no_schema": False,
            "pagespeed": check_page_speed(url),  # mobile performance score + load time
        }

        # Check for old tech signals in metadata/content
        old_signals = ["wordpress 2", "2018", "2017", "2016", "2015", "jquery 1.", "flash"]
        result["old_tech"] = any(sig in content_lower for sig in old_signals)

        # Strict mobile check — requires BOTH signals to fire:
        # 1. No proper viewport meta (width=device-width) in actual HTML
        # 2. Fixed-width layout indicators in CSS/HTML
        no_responsive_viewport = "width=device-width" not in html_lower
        fixed_width_patterns = ["width: 960px", "width: 980px", "width: 1024px", "min-width: 960", "min-width: 980", "width:960px", "width:980px"]
        has_fixed_width = any(p in html_lower for p in fixed_width_patterns)
        result["not_mobile"] = no_responsive_viewport and has_fixed_width

        # SEO signals
        meta_desc = metadata.get("description", "") or ""
        result["no_meta_description"] = len(meta_desc.strip()) < 20
        result["no_schema"] = "application/ld+json" not in html_lower and "schema.org" not in html_lower

        return result

    except Exception:
        return None


def run_scraper(niche, location, limit=20, min_score=3, dry_run=False, skip_scrape=False):
    """Main scraper pipeline."""

    industry = get_industry(niche)
    places = search_places(niche, location, limit)

    if not places:
        print("No businesses found. Try a different niche or location.")
        return

    print(f"\nScoring {len(places)} businesses...\n")
    qualified = []
    skipped = 0

    for i, place in enumerate(places, 1):
        details = get_place_details(place)

        name = details.get("name") or ""
        address = details.get("formatted_address", "")
        phone = details.get("formatted_phone_number", "")
        website = details.get("website", "")
        rating = details.get("rating", "N/A")
        reviews = details.get("user_ratings_total", 0)

        # Website scrape — Firecrawl (structure) + PageSpeed (performance)
        # PageSpeed runs independently so a Firecrawl failure doesn't prevent speed data
        scraped = None
        if website and not skip_scrape:
            scraped = scrape_website(website)
            # If Firecrawl failed but we have a website, still get PageSpeed data
            if scraped is None:
                ps = check_page_speed(website)
                if ps:
                    scraped = {"old_tech": False, "not_mobile": False, "thin_content": False,
                               "no_meta_description": False, "no_schema": False, "pagespeed": ps}

        score, reasons = score_lead(details, scraped)

        status = "QUALIFIED" if score >= min_score else "SKIPPED"
        if score < min_score:
            skipped += 1

        print(f"[{i}/{len(places)}] {status} (score: {score}/10) — {name}")
        if reasons:
            print(f"         Reasons: {', '.join(reasons)}")

        if score >= min_score:
            qualified.append({
                "name": name,
                "address": address,
                "phone": phone,
                "website": website,
                "rating": rating,
                "reviews": reviews,
                "score": score,
                "reasons": reasons,
                "industry": industry,
            })

    print(f"\n{'='*50}")
    print(f"Results: {len(qualified)} qualified leads, {skipped} skipped (min score: {min_score})")
    print(f"{'='*50}\n")

    if dry_run:
        print("DRY RUN — preview only. Qualified leads:")
        for lead in qualified:
            print(f"  • {lead['name']} | Score: {lead['score']} | {lead['address']}")
        return qualified

    # NOTE: this script does NOT persist anything. CRM + task-system writes are manual.
    print("NOTE: this script does NOT write to your CRM or task system — persistence is manual.")
    print("The agent (or you) must create one pipeline record and one 'New Lead' task")
    print("(tools/asana_cli.py create-task) per lead below, then VERIFY the writes landed.")
    print("See .claude/skills/lead-scraper/SKILL.md Step 3.")
    print("Qualified leads to add:")
    for lead in qualified:
        notes = f"Score: {lead['score']}/10 | Pain points: {', '.join(lead['reasons'])} | Rating: {lead['rating']}★ ({lead['reviews']} reviews)"
        print(f"  • {lead['name']} | {lead['address']} | {lead['website']} | {notes}")

    return qualified


def main():
    parser = argparse.ArgumentParser(description="Places-API lead finder + weakness scorer")
    parser.add_argument("--niche", required=True, help='Business type to search (e.g. "HVAC", "dentist")')
    parser.add_argument("--location", required=True, help='City and state (e.g. "Springfield, IL")')
    parser.add_argument("--limit", type=int, default=20, help="Max businesses to fetch (default: 20)")
    parser.add_argument("--min-score", type=int, default=3, help="Minimum score to qualify a lead (default: 3)")
    parser.add_argument("--dry-run", action="store_true", help="Preview results only")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip Firecrawl website scraping (faster, less accurate)")
    args = parser.parse_args()

    run_scraper(
        niche=args.niche,
        location=args.location,
        limit=args.limit,
        min_score=args.min_score,
        dry_run=args.dry_run,
        skip_scrape=args.skip_scrape,
    )


if __name__ == "__main__":
    main()
