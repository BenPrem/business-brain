"""
prospect_workup.py — Prospect Workup Pipeline

Master orchestrator that runs the full 6-phase prospect workup autonomously
(see .claude/skills/prospect-workup/SKILL.md).

Phases 1-3 run in PARALLEL on cheap models (research, competitors, audit),
then 4-6 run SEQUENTIALLY on mid/premium tiers (demo site, marketing plan,
proposal + preview). Output lands under clients/<slug>/research/ and
clients/<slug>/deliverables/; the final build is STAGED for the founder's
review — nothing deploys without an explicit green-light.

Prompt templates live in templates/prospect-workup/ — they are tool-owned
output templates bound to this script by filename; do not relocate them.

Usage:
    # Full workup
    python3 tools/prospect_workup.py --business "Example HVAC" --location "Springfield, IL"

    # With contact name (personalizes proposal/preview)
    python3 tools/prospect_workup.py --business "Example HVAC" --location "Springfield, IL" --contact "Jordan Smith"

    # With known website URL (skips lookup)
    python3 tools/prospect_workup.py --business "Example HVAC" --location "Springfield, IL" --url "https://example.com"

    # Dry run (no deploy staging)
    python3 tools/prospect_workup.py --business "Example HVAC" --location "Springfield, IL" --dry-run

    # Run only specific phases
    python3 tools/prospect_workup.py --business "Example HVAC" --location "Springfield, IL" --phases 1,2,3

Requires (env vars only — see guides/connecting-tools.md):
    - OPENROUTER_API_KEY       (all LLM phases via tools/openrouter_client.py)
    - FIRECRAWL_API_KEY        (site scraping)
    - GOOGLE_PLACES_API_KEY    (business lookup + PageSpeed)
    - pip install requests python-dotenv
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Add tools directory for imports
sys.path.insert(0, os.path.dirname(__file__))

from openrouter_client import complete_cheap, complete_mid, complete_premium
from competitor_analyzer import run_analysis as run_competitor_analysis
from website_auditor import run_audit as run_website_audit

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests python-dotenv")
    sys.exit(1)

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"
PLACES_BASE = "https://places.googleapis.com/v1"

BASE_DIR = Path(__file__).parent.parent
CLIENTS_DIR = BASE_DIR / "clients"
TEMPLATES_DIR = BASE_DIR / "templates" / "prospect-workup"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("workup")


def slugify(name):
    """Convert business name to a filesystem-safe slug."""
    return (
        name.lower()
        .replace("'", "")
        .replace("'", "")
        .replace("&", "and")
        .replace(" ", "-")
        .replace(".", "")
        .replace(",", "")
        .strip("-")
    )


def load_template(name):
    """Load a prompt template file."""
    path = TEMPLATES_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text()


def ensure_client_dirs(slug):
    """Create the client directory structure. Returns (research_dir, deliverables_dir)."""
    client_dir = CLIENTS_DIR / slug
    research_dir = client_dir / "research"
    deliverables_dir = client_dir / "deliverables"
    research_dir.mkdir(parents=True, exist_ok=True)
    for subdir in ["demo-site", "proposal", "preview", "deploy", "deploy/demo", "deploy/proposal"]:
        (deliverables_dir / subdir).mkdir(parents=True, exist_ok=True)
    return research_dir, deliverables_dir


# ============================================================================
# PHASE 1: SCRAPE & RESEARCH
# ============================================================================

def phase1_research(business_name, location, website_url=None, research_dir=None):
    """
    Scrape the prospect's website and research their online presence.
    Model: cheap tier.
    """
    log.info(f"PHASE 1: Scraping & researching {business_name}...")
    start = time.time()

    # Step 1: Find the business via the Places API if no URL provided
    places_data = {}
    if GOOGLE_PLACES_API_KEY:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": (
                "places.displayName,places.formattedAddress,places.nationalPhoneNumber,"
                "places.websiteUri,places.rating,places.userRatingCount,"
                "places.regularOpeningHours"
            ),
        }
        resp = requests.post(
            f"{PLACES_BASE}/places:searchText",
            headers=headers,
            json={"textQuery": f"{business_name} in {location}", "pageSize": 1},
        )
        if resp.status_code == 200:
            places = resp.json().get("places", [])
            if places:
                p = places[0]
                places_data = {
                    "name": p.get("displayName", {}).get("text", ""),
                    "address": p.get("formattedAddress", ""),
                    "phone": p.get("nationalPhoneNumber", ""),
                    "website": p.get("websiteUri", ""),
                    "rating": p.get("rating", 0),
                    "reviews": p.get("userRatingCount", 0),
                    "hours": p.get("regularOpeningHours", {}),
                }
                if not website_url:
                    website_url = places_data.get("website", "")

    # Step 2: Scrape the website via Firecrawl
    scraped_content = ""
    if website_url and FIRECRAWL_API_KEY:
        try:
            resp = requests.post(
                f"{FIRECRAWL_BASE}/scrape",
                headers={
                    "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"url": website_url, "formats": ["markdown", "html"]},
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                scraped_content = data.get("markdown", "")[:8000]  # Cap for token limits
        except Exception as e:
            log.warning(f"Firecrawl error: {e}")

    # Step 3: LLM analysis
    template = load_template("phase1-research.md")
    prompt = template.replace("{business_name}", business_name)
    prompt = prompt.replace("{location}", location)
    prompt = prompt.replace("{scraped_content}", scraped_content[:6000] if scraped_content else "No website content available — business may not have a website.")
    prompt = prompt.replace("{google_maps_data}", json.dumps(places_data, indent=2) if places_data else "No business-listing data available.")

    report = complete_cheap(prompt, max_tokens=3000)

    # Save outputs
    if research_dir:
        (research_dir / "research-scrape.md").write_text(report)
        (research_dir / "research-data.json").write_text(json.dumps({
            "places_data": places_data,
            "website_url": website_url,
            "scrape_length": len(scraped_content),
        }, indent=2, default=str))

    elapsed = round(time.time() - start, 1)
    log.info(f"PHASE 1 complete ({elapsed}s)")
    return {
        "report": report,
        "places_data": places_data,
        "website_url": website_url,
        "scraped_content": scraped_content,
    }


# ============================================================================
# PHASE 2: COMPETITOR ANALYSIS (delegates to competitor_analyzer.py)
# ============================================================================

def phase2_competitors(business_name, location, research_dir=None):
    """
    Find and analyze 4-5 competitors.
    Model: cheap tier — handled by competitor_analyzer.py.
    """
    log.info(f"PHASE 2: Competitor analysis for {business_name}...")
    start = time.time()

    result = run_competitor_analysis(
        business_name=business_name,
        location=location,
        limit=5,
        output_dir=str(research_dir) if research_dir else None,
    )

    elapsed = round(time.time() - start, 1)
    log.info(f"PHASE 2 complete ({elapsed}s)")
    return result


# ============================================================================
# PHASE 3: WEBSITE AUDIT (delegates to website_auditor.py)
# ============================================================================

def phase3_audit(business_name, website_url, research_dir=None):
    """
    Score the prospect's website out of 100 with detailed breakdown.
    Model: mid tier — handled by website_auditor.py.
    """
    log.info(f"PHASE 3: Website audit for {business_name}...")
    start = time.time()

    if not website_url:
        log.warning("No website URL — skipping audit, will note 'no website' as the finding")
        no_site_report = (
            f"# Website Audit: {business_name}\n\n"
            f"**Overall Score: 0/100**\n\n"
            f"## Finding\n\n"
            f"{business_name} does not have a website. This is the single biggest gap "
            f"in their digital presence. Every competitor with a website is capturing "
            f"customers that {business_name} is invisible to.\n"
        )
        if research_dir:
            (research_dir / "website-audit.md").write_text(no_site_report)
        return {"report": no_site_report, "data": {"total_score": 0, "no_website": True}}

    competitor_data_path = str(research_dir / "competitor-data.json") if research_dir and (research_dir / "competitor-data.json").exists() else None

    result = run_website_audit(
        url=website_url,
        business_name=business_name,
        competitor_data_path=competitor_data_path,
        output_dir=str(research_dir) if research_dir else None,
    )

    elapsed = round(time.time() - start, 1)
    log.info(f"PHASE 3 complete ({elapsed}s)")
    return result


# ============================================================================
# SYNTHESIS: Merge Phase 1-3 outputs into a creative brief
# ============================================================================

def synthesize(phase1, phase2, phase3):
    """
    Merge research, competitor, and audit data into a brief for creative phases.
    Model: cheap tier.
    """
    log.info("SYNTHESIS: Building creative brief from Phases 1-3...")

    template = load_template("synthesis-brief.md")
    prompt = template.replace("{phase1_output}", phase1.get("report", "No research data")[:3000])
    prompt = prompt.replace("{phase2_output}", (phase2 or {}).get("report", "No competitor data")[:3000])
    prompt = prompt.replace("{phase3_output}", (phase3 or {}).get("report", "No audit data")[:3000])

    brief = complete_cheap(prompt, max_tokens=2000)
    return brief


# ============================================================================
# PHASE 4: DEMO WEBSITE BUILD
# ============================================================================

def _strip_code_fences(html):
    """Clean up if the model wrapped output in code fences."""
    if html.startswith("```"):
        html = html.split("\n", 1)[1] if "\n" in html else html
        if html.endswith("```"):
            html = html[:-3]
        html = html.strip()
    return html


def phase4_demo_site(business_name, synthesis_brief, phase1_data, deliverables_dir):
    """
    Generate a customer-problem-first demo website.
    Model: premium tier — creative work needs quality.
    """
    log.info(f"PHASE 4: Building demo site for {business_name}...")
    start = time.time()

    template = load_template("phase4-demo-site.md")

    # Extract key data from phase 1 for the template
    places = phase1_data.get("places_data", {})
    website_url = phase1_data.get("website_url", "")

    prompt = f"""{template}

## SYNTHESIS BRIEF (from research phases):
{synthesis_brief}

## RAW RESEARCH DATA:
- Business: {business_name}
- Website: {website_url or 'No current website'}
- Location: {places.get('address', 'Unknown')}
- Phone: {places.get('phone', 'Unknown')}
- Rating: {places.get('rating', 'N/A')}★ ({places.get('reviews', 0)} reviews)

## INSTRUCTION:
Generate the complete index.html file now. Output ONLY the HTML — no explanation, no markdown code fences. Start with <!DOCTYPE html> and end with </html>.
"""

    html = _strip_code_fences(complete_premium(prompt, max_tokens=12000))

    # Save
    demo_path = deliverables_dir / "demo-site" / "index.html"
    demo_path.write_text(html)

    # Also copy to deploy folder
    deploy_demo = deliverables_dir / "deploy" / "demo" / "index.html"
    deploy_demo.write_text(html)

    elapsed = round(time.time() - start, 1)
    log.info(f"PHASE 4 complete ({elapsed}s) — {len(html)} bytes")
    return {"html": html, "path": str(demo_path)}


# ============================================================================
# PHASE 5: MARKETING PLAN
# ============================================================================

def phase5_marketing_plan(business_name, synthesis_brief, phase3_data, research_dir):
    """
    Generate a comprehensive marketing plan.
    Model: mid tier — strategic but not as token-heavy as the website build.
    """
    log.info(f"PHASE 5: Generating marketing plan for {business_name}...")
    start = time.time()

    template = load_template("phase5-marketing-plan.md")

    audit_score = "N/A"
    audit_summary = "No audit data available"
    if phase3_data and phase3_data.get("data"):
        data = phase3_data["data"]
        audit_score = data.get("total_score", "N/A")
        audit_summary = phase3_data.get("report", "")[:2000]

    prompt = f"""{template}

## CONTEXT:
- Business: {business_name}
- Audit Score: {audit_score}/100
- Audit Summary: {audit_summary}

## SYNTHESIS BRIEF:
{synthesis_brief}

## INSTRUCTION:
Generate the complete marketing plan as a markdown document. Be specific with numbers, timelines, and tool recommendations. Use realistic revenue projections for a local service business.
"""

    plan = complete_mid(prompt, max_tokens=5000)

    # Save
    plan_path = research_dir / "marketing-plan.md"
    plan_path.write_text(plan)

    elapsed = round(time.time() - start, 1)
    log.info(f"PHASE 5 complete ({elapsed}s)")
    return {"report": plan, "path": str(plan_path)}


# ============================================================================
# PHASE 6: PROPOSAL + PREVIEW PAGE
# ============================================================================

def phase6_proposal(business_name, contact_name, synthesis_brief, phase3_data, phase5_data, deliverables_dir):
    """
    Generate branded HTML proposal + preview landing page.
    Model: premium tier — client-facing quality.
    """
    log.info(f"PHASE 6: Building proposal and preview page for {business_name}...")
    start = time.time()

    # --- 6A: Proposal ---
    proposal_template = load_template("phase6-proposal.md")
    audit_score = (phase3_data or {}).get("data", {}).get("total_score", "N/A")

    proposal_prompt = f"""{proposal_template}

## CONTEXT:
- Business: {business_name}
- Contact: {contact_name or 'Business Owner'}
- Audit Score: {audit_score}/100

## SYNTHESIS BRIEF:
{synthesis_brief}

## MARKETING PLAN SUMMARY:
{(phase5_data or {}).get('report', '')[:2000]}

## INSTRUCTION:
Generate the complete proposal as a single HTML file. Output ONLY the HTML — no explanation. Start with <!DOCTYPE html>.
"""

    proposal_html = _strip_code_fences(complete_premium(proposal_prompt, max_tokens=8000))

    proposal_path = deliverables_dir / "proposal" / "index.html"
    proposal_path.write_text(proposal_html)
    (deliverables_dir / "deploy" / "proposal" / "index.html").write_text(proposal_html)

    # --- 6B: Preview Page ---
    preview_template = load_template("phase6-preview-page.md")

    # Build feature comparison lists from audit data
    audit_details = (phase3_data or {}).get("data", {}).get("details", {})
    missing = []
    built = []
    for category, detail in audit_details.items():
        if detail and "Missing" in detail or "No " in str(detail):
            missing.append(detail)
            built.append(f"✓ {category.replace('_', ' ').title()} — addressed in our demo")

    preview_prompt = f"""{preview_template}

## CONTEXT:
- Business: {business_name}
- Contact: {contact_name or 'there'}
- Demo URL: demo/index.html
- Proposal URL: proposal/index.html
- Missing Features (red cards): {json.dumps(missing[:6])}
- Built Features (green cards): {json.dumps(built[:6])}

## NOTE ON SCREENSHOTS:
Screenshots will be added after this page is generated. Use placeholder image divs with
data-screenshot attributes that the orchestrator will replace with actual screenshot paths.
Use gray placeholder boxes with text like "Current Site - Desktop" etc.

## INSTRUCTION:
Generate the complete preview landing page as a single HTML file. Output ONLY the HTML — no explanation. Start with <!DOCTYPE html>.
"""

    preview_html = _strip_code_fences(complete_premium(preview_prompt, max_tokens=8000))

    preview_path = deliverables_dir / "preview" / "index.html"
    preview_path.write_text(preview_html)
    (deliverables_dir / "deploy" / "index.html").write_text(preview_html)

    elapsed = round(time.time() - start, 1)
    log.info(f"PHASE 6 complete ({elapsed}s)")
    return {
        "proposal_path": str(proposal_path),
        "preview_path": str(preview_path),
    }


# ============================================================================
# CRM + TASK-SYSTEM LOGGING
# ============================================================================

def log_to_crm(business_name, slug, dry_run=False):
    """Remind that CRM/task-system persistence is the agent's job, not this script's."""
    if dry_run:
        log.info("DRY RUN — skipping CRM/task-system reminder")
        return

    log.info("This script does NOT write to your CRM or task system.")
    log.info(f"Create/update the deal record for {business_name} ({slug}) and the")
    log.info("matching task (tools/asana_cli.py), then VERIFY both writes landed.")


# ============================================================================
# DEPLOY STAGING
# ============================================================================

def stage_deploy(slug, dry_run=False):
    """Stage the deploy folder for the founder's review. Never deploys."""
    if dry_run:
        log.info("DRY RUN — skipping deploy staging")
        return

    try:
        from netlify_deploy import stage
        stage(slug)
        log.info("Deploy staged. After the founder's explicit green-light:")
        log.info(f"  python3 tools/netlify_deploy.py {slug} --deploy --site <SITE_ID>")
    except Exception as e:
        log.warning(f"Deploy staging failed: {e}")


# ============================================================================
# MASTER ORCHESTRATOR
# ============================================================================

def run_workup(business_name, location, contact_name=None, website_url=None,
               phases=None, dry_run=False):
    """
    Run the full 6-phase prospect workup.

    Args:
        business_name:  Name of the prospect business
        location:       City, State
        contact_name:   Optional contact person name
        website_url:    Optional known website URL
        phases:         Optional list of phase numbers to run (e.g., [1,2,3])
        dry_run:        Skip deploy staging
    """
    run_all = phases is None
    phases = set(phases or [1, 2, 3, 4, 5, 6])

    slug = slugify(business_name)
    research_dir, deliverables_dir = ensure_client_dirs(slug)
    start_time = time.time()

    log.info(f"{'='*60}")
    log.info(f"PROSPECT WORKUP: {business_name}")
    log.info(f"Location: {location}")
    log.info(f"Contact: {contact_name or 'Unknown'}")
    log.info(f"Slug: {slug}")
    log.info(f"Research output: {research_dir}")
    log.info(f"Deliverables output: {deliverables_dir}")
    log.info(f"Phases: {sorted(phases)}")
    log.info(f"Dry run: {dry_run}")
    log.info(f"{'='*60}\n")

    results = {}

    # ── PHASES 1-3: PARALLEL (cheap models) ───────────────────────────
    if any(p in phases for p in [1, 2, 3]):
        log.info("Starting Phases 1-3 (parallel)...\n")

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}

            if 1 in phases:
                futures[executor.submit(
                    phase1_research, business_name, location, website_url, research_dir
                )] = "phase1"

            if 2 in phases:
                futures[executor.submit(
                    phase2_competitors, business_name, location, research_dir
                )] = "phase2"

            if 3 in phases and website_url:
                futures[executor.submit(
                    phase3_audit, business_name, website_url, research_dir
                )] = "phase3"

            for future in as_completed(futures):
                phase_name = futures[future]
                try:
                    results[phase_name] = future.result()
                except Exception as e:
                    log.error(f"{phase_name} failed: {e}")
                    results[phase_name] = {"error": str(e)}

        # If Phase 1 found a website and we haven't run Phase 3 yet
        if 3 in phases and not website_url:
            found_url = results.get("phase1", {}).get("website_url", "")
            if found_url:
                log.info(f"Phase 1 found website: {found_url} — running Phase 3 now...")
                try:
                    results["phase3"] = phase3_audit(business_name, found_url, research_dir)
                except Exception as e:
                    log.error(f"Phase 3 failed: {e}")
                    results["phase3"] = {"error": str(e)}
            else:
                results["phase3"] = phase3_audit(business_name, None, research_dir)

    # ── SYNTHESIS ─────────────────────────────────────────────────────
    synthesis_brief = ""
    if any(p in phases for p in [4, 5, 6]):
        # Load from files if phases 1-3 were run in a previous invocation
        if "phase1" not in results and (research_dir / "research-scrape.md").exists():
            results["phase1"] = {"report": (research_dir / "research-scrape.md").read_text()}
        if "phase2" not in results and (research_dir / "competitor-analysis.md").exists():
            results["phase2"] = {"report": (research_dir / "competitor-analysis.md").read_text()}
        if "phase3" not in results and (research_dir / "website-audit.md").exists():
            results["phase3"] = {"report": (research_dir / "website-audit.md").read_text()}

        synthesis_brief = synthesize(
            results.get("phase1", {}),
            results.get("phase2", {}),
            results.get("phase3", {}),
        )
        (research_dir / "synthesis-brief.md").write_text(synthesis_brief)

    # ── PHASES 4-6: SEQUENTIAL (mid/premium tiers) ────────────────────
    if 4 in phases:
        try:
            results["phase4"] = phase4_demo_site(
                business_name, synthesis_brief, results.get("phase1", {}), deliverables_dir
            )
        except Exception as e:
            log.error(f"Phase 4 failed: {e}")
            results["phase4"] = {"error": str(e)}

    if 5 in phases:
        try:
            results["phase5"] = phase5_marketing_plan(
                business_name, synthesis_brief, results.get("phase3", {}), research_dir
            )
        except Exception as e:
            log.error(f"Phase 5 failed: {e}")
            results["phase5"] = {"error": str(e)}

    if 6 in phases:
        try:
            results["phase6"] = phase6_proposal(
                business_name, contact_name, synthesis_brief,
                results.get("phase3", {}), results.get("phase5", {}), deliverables_dir
            )
        except Exception as e:
            log.error(f"Phase 6 failed: {e}")
            results["phase6"] = {"error": str(e)}

    # ── POST-PIPELINE ─────────────────────────────────────────────────
    total_time = round(time.time() - start_time, 1)

    # CRM + task-system persistence reminder
    if run_all:
        log_to_crm(business_name, slug, dry_run)

    # Stage deploy
    if 6 in phases:
        stage_deploy(slug, dry_run)

    # ── SUMMARY ───────────────────────────────────────────────────────
    log.info(f"\n{'='*60}")
    log.info(f"WORKUP COMPLETE: {business_name}")
    log.info(f"{'='*60}")
    log.info(f"Total time: {total_time}s")
    log.info(f"Output: {CLIENTS_DIR / slug}")

    for phase_name, result in sorted(results.items()):
        if "error" in result:
            log.info(f"  {phase_name}: FAILED — {result['error'][:80]}")
        else:
            log.info(f"  {phase_name}: OK")

    if 6 in phases and not dry_run:
        log.info("\nReady for the founder's review — do not deploy without a green-light.")
        log.info(f"Deploy command: python3 tools/netlify_deploy.py {slug} --deploy --site <SITE_ID>")

    # Save run metadata
    run_meta = {
        "business_name": business_name,
        "location": location,
        "contact_name": contact_name,
        "slug": slug,
        "phases_run": sorted(phases),
        "total_time_seconds": total_time,
        "completed_at": datetime.now().isoformat(),
        "dry_run": dry_run,
        "phase_status": {k: "error" if "error" in v else "ok" for k, v in results.items()},
    }
    (research_dir / "workup-meta.json").write_text(json.dumps(run_meta, indent=2))

    return results


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Prospect Workup Pipeline",
        epilog="Runs the full 6-phase prospect workup autonomously.",
    )
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--location", required=True, help="City, State")
    parser.add_argument("--contact", default=None, help="Contact person name")
    parser.add_argument("--url", default=None, help="Known website URL")
    parser.add_argument("--phases", default=None, help="Comma-separated phase numbers (e.g., 1,2,3)")
    parser.add_argument("--dry-run", action="store_true", help="Skip deploy staging")
    args = parser.parse_args()

    phases = None
    if args.phases:
        phases = [int(p.strip()) for p in args.phases.split(",")]

    run_workup(
        business_name=args.business,
        location=args.location,
        contact_name=args.contact,
        website_url=args.url,
        phases=phases,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
