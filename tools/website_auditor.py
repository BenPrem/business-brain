"""
website_auditor.py — Website Audit Tool

Scores a prospect's website out of 100 with page-by-page breakdown,
SEO analysis, mobile performance, and gap analysis vs. competitors.
Phase 3 of the prospect workup pipeline (see tools/prospect_workup.py and
.claude/skills/prospect-workup/SKILL.md).

Usage:
    python3 tools/website_auditor.py --url "https://example.com" --business "Example HVAC"
    python3 tools/website_auditor.py --url "https://example.com" --business "Example HVAC" \
        --competitor-data clients/example-hvac/research/competitor-data.json

Requires (env vars only — see guides/connecting-tools.md; never hardcode values):
    - FIRECRAWL_API_KEY        (site scraping)
    - GOOGLE_PLACES_API_KEY    (PageSpeed Insights — same Google Cloud key as Places)
    - OPENROUTER_API_KEY       (report generation via tools/openrouter_client.py)
    - pip install requests python-dotenv
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests python-dotenv")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(__file__))
from openrouter_client import complete_mid

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"

CLIENTS_DIR = Path(__file__).parent.parent / "clients"


# ============================================================================
# SCORING RUBRIC (100 points total)
# ============================================================================
# Each category has a max score. Sum = 100.

RUBRIC = {
    "mobile_performance": {"max": 20, "description": "Mobile PageSpeed score"},
    "seo_basics": {"max": 15, "description": "Title tags, meta descriptions, headings"},
    "local_seo": {"max": 15, "description": "Schema markup, NAP consistency, business-profile signals"},
    "content_quality": {"max": 15, "description": "Depth, uniqueness, service page coverage"},
    "conversion_elements": {"max": 15, "description": "CTAs, forms, booking, phone, trust signals"},
    "design_ux": {"max": 10, "description": "Mobile responsive, modern design, accessibility"},
    "technical": {"max": 10, "description": "SSL, fast load, no broken elements, clean HTML"},
}


def scrape_site(url):
    """Scrape the full site via Firecrawl. Returns structured data."""
    if not FIRECRAWL_API_KEY:
        return {"error": "No Firecrawl API key (set FIRECRAWL_API_KEY in .env)"}

    print(f"  Scraping {url}...")
    try:
        # Scrape main page
        resp = requests.post(
            f"{FIRECRAWL_BASE}/scrape",
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"url": url, "formats": ["markdown", "html"]},
            timeout=30,
        )
        if resp.status_code != 200:
            return {"error": f"Firecrawl returned {resp.status_code}"}

        data = resp.json().get("data", {})
        return {
            "markdown": data.get("markdown", ""),
            "html": data.get("html", ""),
            "metadata": data.get("metadata", {}),
            "url": url,
        }
    except Exception as e:
        return {"error": str(e)}


def check_pagespeed(url):
    """Run Google PageSpeed Insights (mobile). Returns detailed metrics."""
    if not GOOGLE_PLACES_API_KEY:
        return None

    print("  Running PageSpeed analysis...")
    try:
        resp = requests.get(
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params={
                "url": url,
                "strategy": "mobile",
                "key": GOOGLE_PLACES_API_KEY,
                "category": ["performance", "accessibility", "seo", "best-practices"],
            },
            timeout=30,
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        audits = lighthouse.get("audits", {})

        return {
            "performance_score": round(categories.get("performance", {}).get("score", 0) * 100),
            "accessibility_score": round(categories.get("accessibility", {}).get("score", 0) * 100),
            "seo_score": round(categories.get("seo", {}).get("score", 0) * 100),
            "best_practices_score": round(categories.get("best-practices", {}).get("score", 0) * 100),
            "fcp_ms": audits.get("first-contentful-paint", {}).get("numericValue"),
            "lcp_ms": audits.get("largest-contentful-paint", {}).get("numericValue"),
            "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
            "tbt_ms": audits.get("total-blocking-time", {}).get("numericValue"),
        }
    except Exception:
        return None


def extract_signals(scrape_data):
    """Extract audit signals from scraped HTML/content."""
    html = (scrape_data.get("html", "") or "").lower()
    markdown = scrape_data.get("markdown", "") or ""
    metadata = scrape_data.get("metadata", {}) or {}

    return {
        # SEO signals
        "has_title": bool(metadata.get("title", "").strip()),
        "title": metadata.get("title", ""),
        "has_meta_description": len((metadata.get("description", "") or "").strip()) > 20,
        "meta_description": metadata.get("description", ""),
        "has_h1": "<h1" in html,
        "has_schema": "schema.org" in html or "application/ld+json" in html,
        "has_og_tags": 'property="og:' in html or "property='og:" in html,

        # Local SEO
        "has_address_on_page": any(kw in html for kw in ["street", "suite", "blvd", "ave ", "road"]),
        "has_phone_on_page": any(kw in html for kw in ["tel:", "phone", "call us", "call today"]),
        "has_google_maps_embed": "maps.google" in html or "google.com/maps" in html,
        "has_local_schema": "localbusiness" in html,

        # Conversion elements
        "has_cta_button": any(kw in html for kw in [
            "book now", "schedule", "get started", "contact us", "free quote",
            "free estimate", "call now", "get a quote",
        ]),
        "has_booking_system": any(kw in html for kw in [
            "calendly", "cal.com", "acuity", "book online", "schedule appointment",
        ]),
        "has_contact_form": "form" in html and ("submit" in html or "send" in html),
        "has_phone_clickable": "tel:" in html,
        "has_testimonials": any(kw in html for kw in [
            "testimonial", "review", "what our", "customer said", "client said",
        ]),
        "has_trust_badges": any(kw in html for kw in [
            "bbb", "licensed", "insured", "certified", "accredited", "guarantee",
        ]),

        # Design/UX
        "has_mobile_viewport": "width=device-width" in html,
        "has_ssl": scrape_data.get("url", "").startswith("https://"),
        "has_favicon": "favicon" in html or "shortcut icon" in html,

        # Content signals
        "content_length": len(markdown),
        "word_count": len(markdown.split()),
        "has_service_pages": any(kw in html for kw in [
            "/services", "/our-services", "what we do", "our services",
        ]),
        "has_about_page": any(kw in html for kw in ["/about", "about us", "our story", "our team"]),
        "has_blog": any(kw in html for kw in ["/blog", "articles", "news", "insights"]),

        # Technical
        "has_social_links": any(kw in html for kw in [
            "facebook.com", "instagram.com", "twitter.com", "linkedin.com",
            "youtube.com", "tiktok.com",
        ]),
        "has_analytics": any(kw in html for kw in [
            "google-analytics", "gtag", "gtm", "analytics", "ga4",
        ]),
    }


def score_site(signals, pagespeed):
    """Calculate score out of 100 based on signals and PageSpeed data."""
    scores = {}
    details = {}

    # Mobile Performance (20 pts)
    ps_score = pagespeed.get("performance_score", 0) if pagespeed else 0
    scores["mobile_performance"] = round(ps_score * 0.2)  # Scale 0-100 → 0-20
    load_ms = pagespeed.get("fcp_ms", 0) if pagespeed else 0
    details["mobile_performance"] = (
        f"PageSpeed score: {ps_score}/100, "
        f"First paint: {round(load_ms/1000, 1) if load_ms else '?'}s"
    )

    # SEO Basics (15 pts)
    seo = 0
    seo_notes = []
    if signals["has_title"]:
        seo += 3
    else:
        seo_notes.append("Missing page title")
    if signals["has_meta_description"]:
        seo += 3
    else:
        seo_notes.append("Missing/short meta description")
    if signals["has_h1"]:
        seo += 3
    else:
        seo_notes.append("Missing H1 heading")
    if signals["has_og_tags"]:
        seo += 3
    else:
        seo_notes.append("Missing Open Graph tags")
    if signals["has_analytics"]:
        seo += 3
    else:
        seo_notes.append("No analytics tracking detected")
    scores["seo_basics"] = min(seo, 15)
    details["seo_basics"] = "; ".join(seo_notes) if seo_notes else "All basic SEO elements present"

    # Local SEO (15 pts)
    local = 0
    local_notes = []
    if signals["has_schema"]:
        local += 4
    else:
        local_notes.append("No structured data / schema markup")
    if signals["has_local_schema"]:
        local += 4
    else:
        local_notes.append("No LocalBusiness schema")
    if signals["has_address_on_page"]:
        local += 3
    else:
        local_notes.append("No address visible on page")
    if signals["has_google_maps_embed"]:
        local += 2
    else:
        local_notes.append("No Google Maps embed")
    if signals["has_phone_on_page"]:
        local += 2
    else:
        local_notes.append("No phone number visible")
    scores["local_seo"] = min(local, 15)
    details["local_seo"] = "; ".join(local_notes) if local_notes else "Strong local SEO signals"

    # Content Quality (15 pts)
    content = 0
    content_notes = []
    wc = signals["word_count"]
    if wc > 1000:
        content += 5
    elif wc > 500:
        content += 3
    elif wc > 200:
        content += 1
    else:
        content_notes.append(f"Very thin content ({wc} words)")
    if signals["has_service_pages"]:
        content += 4
    else:
        content_notes.append("No dedicated service pages")
    if signals["has_about_page"]:
        content += 3
    else:
        content_notes.append("No about page")
    if signals["has_blog"]:
        content += 3
    else:
        content_notes.append("No blog or content marketing")
    scores["content_quality"] = min(content, 15)
    details["content_quality"] = "; ".join(content_notes) if content_notes else "Good content coverage"

    # Conversion Elements (15 pts)
    conversion = 0
    conv_notes = []
    if signals["has_cta_button"]:
        conversion += 3
    else:
        conv_notes.append("No clear call-to-action buttons")
    if signals["has_booking_system"]:
        conversion += 4
    else:
        conv_notes.append("No online booking/scheduling system")
    if signals["has_contact_form"]:
        conversion += 2
    else:
        conv_notes.append("No contact form")
    if signals["has_phone_clickable"]:
        conversion += 2
    else:
        conv_notes.append("Phone number not clickable (tel: link)")
    if signals["has_testimonials"]:
        conversion += 2
    else:
        conv_notes.append("No testimonials or reviews displayed")
    if signals["has_trust_badges"]:
        conversion += 2
    else:
        conv_notes.append("No trust signals (licenses, badges, guarantees)")
    scores["conversion_elements"] = min(conversion, 15)
    details["conversion_elements"] = "; ".join(conv_notes) if conv_notes else "Strong conversion setup"

    # Design & UX (10 pts)
    design = 0
    design_notes = []
    if signals["has_mobile_viewport"]:
        design += 4
    else:
        design_notes.append("Not mobile-responsive")
    if signals["has_ssl"]:
        design += 3
    else:
        design_notes.append("No SSL (HTTP only)")
    if signals["has_favicon"]:
        design += 1
    else:
        design_notes.append("Missing favicon")
    if signals["has_social_links"]:
        design += 2
    else:
        design_notes.append("No social media links")
    scores["design_ux"] = min(design, 10)
    details["design_ux"] = "; ".join(design_notes) if design_notes else "Clean modern design signals"

    # Technical (10 pts)
    tech = 0
    tech_notes = []
    if pagespeed:
        accessibility = pagespeed.get("accessibility_score", 0)
        best_practices = pagespeed.get("best_practices_score", 0)
        if accessibility >= 80:
            tech += 3
        elif accessibility >= 60:
            tech += 1
        else:
            tech_notes.append(f"Poor accessibility score ({accessibility}/100)")

        if best_practices >= 80:
            tech += 3
        elif best_practices >= 60:
            tech += 1
        else:
            tech_notes.append(f"Low best-practices score ({best_practices}/100)")

        cls = pagespeed.get("cls", 1)
        if cls and cls < 0.1:
            tech += 2
        elif cls and cls < 0.25:
            tech += 1
        else:
            tech_notes.append(f"Layout shift issues (CLS: {cls:.2f})" if cls else "")

        tbt = pagespeed.get("tbt_ms", 999)
        if tbt and tbt < 200:
            tech += 2
        elif tbt and tbt < 600:
            tech += 1
        else:
            tech_notes.append(f"High blocking time ({round(tbt/1000, 1)}s)" if tbt else "")
    else:
        tech_notes.append("PageSpeed data unavailable")
    scores["technical"] = min(tech, 10)
    details["technical"] = "; ".join([n for n in tech_notes if n]) if any(tech_notes) else "Good technical health"

    total = sum(scores.values())
    return total, scores, details


def generate_report(business_name, url, total_score, scores, details, signals, pagespeed, competitor_data=None):
    """Use LLM to generate the full audit report from structured data."""

    # Build the scoring summary
    scoring_lines = []
    for category, score in scores.items():
        max_pts = RUBRIC[category]["max"]
        detail = details.get(category, "")
        scoring_lines.append(f"- **{category.replace('_', ' ').title()}**: {score}/{max_pts} — {detail}")

    competitor_context = ""
    if competitor_data:
        best_competitor = max(competitor_data.get("competitors", []), key=lambda c: c.get("rating", 0), default=None)
        if best_competitor:
            competitor_context = f"""
## Competitor Context
The strongest competitor is {best_competitor.get('name', 'Unknown')} with {best_competitor.get('rating', 'N/A')}★
({best_competitor.get('reviews', 0)} reviews). Compare the prospect's gaps against what competitors are doing well.
"""

    prompt = f"""You are a website audit expert for a digital marketing agency.
Write a comprehensive website audit report for a prospect.

## PROSPECT
Business: {business_name}
Website: {url}
Overall Score: {total_score}/100

## SCORING BREAKDOWN
{chr(10).join(scoring_lines)}

## KEY SIGNALS
- Content: {signals['word_count']} words on homepage
- Title: "{signals.get('title', 'N/A')}"
- Meta: "{signals.get('meta_description', 'N/A')}"
- Mobile: {'Responsive' if signals['has_mobile_viewport'] else 'NOT responsive'}
- SSL: {'Yes' if signals['has_ssl'] else 'No'}
- Booking: {'Yes' if signals['has_booking_system'] else 'No — using basic contact form or no form'}
- PageSpeed: {pagespeed.get('performance_score', 'N/A')}/100 (mobile)
{competitor_context}

## OUTPUT FORMAT (Markdown):

# Website Audit: {business_name}
**Overall Score: {total_score}/100**

## Executive Summary
3-4 sentences. What's the state of this website? What's the single biggest issue holding them back?

## Score Breakdown
Table format showing each category, score, and one-line finding.

## Critical Issues (Fix Immediately)
Numbered list of the most impactful problems. Include estimated revenue impact where possible.
For each issue, explain WHY it matters in business terms (not technical jargon).

## Quick Wins (Easy to Fix, High Impact)
Things that could be improved in a week or less. These are the "low-hanging fruit" to mention on a sales call.

## The Word-of-Mouth Ceiling
Explain how their weak online presence is capping the natural growth of their business.
Even if they do great work, new customers searching online won't find them or won't trust what they see.
Estimate the monthly revenue they're losing from an invisible or unconvincing online presence.
Use realistic numbers for a local {signals.get('niche', 'service')} business.

## Recommendations
Prioritized list of improvements, ordered by business impact.
For each: what to do, why it matters, and rough timeline.

## How This Compares to Competitors
Brief section on where the prospect falls in the local competitive landscape.
"""

    return complete_mid(prompt, max_tokens=4000)


def run_audit(url, business_name, competitor_data_path=None, output_dir=None):
    """Main audit pipeline."""
    print(f"\n{'='*60}")
    print(f"Website Audit: {business_name}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")

    # Step 1: Scrape
    scrape_data = scrape_site(url)
    if "error" in scrape_data:
        print(f"Scrape failed: {scrape_data['error']}")
        return None

    # Step 2: PageSpeed
    pagespeed = check_pagespeed(url)

    # Step 3: Extract signals
    print("  Analyzing signals...")
    signals = extract_signals(scrape_data)
    signals["niche"] = "service"  # Default, overridden by competitor data

    # Step 4: Score
    total, scores, details = score_site(signals, pagespeed)
    print(f"\n  Overall Score: {total}/100")
    for cat, score in scores.items():
        print(f"    {cat}: {score}/{RUBRIC[cat]['max']}")

    # Load competitor data if available
    competitor_data = None
    if competitor_data_path:
        try:
            with open(competitor_data_path) as f:
                competitor_data = json.load(f)
                signals["niche"] = competitor_data.get("niche", "service")
        except Exception as e:
            print(f"  Warning: Could not load competitor data: {e}")

    # Step 5: Generate report
    print("\n  Generating audit report...")
    report = generate_report(business_name, url, total, scores, details, signals, pagespeed, competitor_data)

    # Step 6: Save
    if output_dir:
        out_path = Path(output_dir)
    else:
        slug = business_name.lower().replace("'", "").replace(" ", "-").replace(".", "")
        out_path = CLIENTS_DIR / slug / "research"

    out_path.mkdir(parents=True, exist_ok=True)
    report_file = out_path / "website-audit.md"
    report_file.write_text(report)
    print(f"\n  Report saved: {report_file}")

    # Save raw audit data
    audit_data = {
        "url": url,
        "business_name": business_name,
        "total_score": total,
        "scores": scores,
        "details": details,
        "signals": signals,
        "pagespeed": pagespeed,
    }
    data_file = out_path / "audit-data.json"
    data_file.write_text(json.dumps(audit_data, indent=2, default=str))
    print(f"  Raw data saved: {data_file}")

    return {"report": report, "data": audit_data, "report_file": str(report_file)}


def main():
    parser = argparse.ArgumentParser(description="Website Auditor")
    parser.add_argument("--url", required=True, help="Website URL to audit")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--competitor-data", default=None, help="Path to competitor-data.json from Phase 2")
    parser.add_argument("--output", default=None, help="Output directory (default: clients/[slug]/research/)")
    args = parser.parse_args()

    run_audit(
        url=args.url,
        business_name=args.business,
        competitor_data_path=args.competitor_data,
        output_dir=args.output,
    )


if __name__ == "__main__":
    main()
