"""
netlify_deploy.py — stage-then-deploy-on-approval helper.

Stages prospect demo/preview builds for review, then deploys AFTER the founder
gives an explicit green-light. Netlify is the worked example; swap the CLI
commands for your host while keeping the shape (stage → approve → deploy).

Doctrine (enforced by tools/hooks/deploy-guard.sh — do not route around it):
    - Every deploy passes an explicit `--site <SITE_ID>`. Never rely on
      `netlify link` state; this script never links, and the site ID comes
      from --site or the NETLIFY_SITE_ID env var — never from a hardcoded value.
    - Production deploys require a human confirmation (the hook asks).
    - Staging is free; deploying is gated on the founder's approval.

Usage:
    # Stage a build for review (after building clients/<slug>/deliverables/deploy/)
    python3 tools/netlify_deploy.py <slug> --stage

    # Deploy after approval (site ID from --site or NETLIFY_SITE_ID)
    python3 tools/netlify_deploy.py <slug> --deploy --site <SITE_ID>

    # First-time deploy for a new prospect: create the site, then deploy to it
    python3 tools/netlify_deploy.py <slug> --deploy --create-site <slug>-preview

    # Check what's staged and ready
    python3 tools/netlify_deploy.py --list

Requires:
    - netlify-cli installed globally (npm install -g netlify-cli) and logged in
      (`netlify login` — the token lives in the CLI's own config, or set
      NETLIFY_AUTH_TOKEN in the environment; never in this repo).
"""

import subprocess
import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

CLIENTS_DIR = Path(__file__).parent.parent / "clients"


def get_deploy_dir(slug):
    return CLIENTS_DIR / slug / "deliverables" / "deploy"


def get_marker_path(slug):
    return CLIENTS_DIR / slug / "deploy-ready.json"


def stage(slug):
    deploy_dir = get_deploy_dir(slug)
    if not deploy_dir.exists():
        print(f"Error: {deploy_dir} does not exist. Build the site first.")
        sys.exit(1)

    index = deploy_dir / "index.html"
    if not index.exists():
        print(f"Error: No index.html in {deploy_dir}. Build looks incomplete.")
        sys.exit(1)

    # Count files
    files = list(deploy_dir.rglob("*"))
    file_count = len([f for f in files if f.is_file()])
    html_count = len([f for f in files if f.suffix == ".html"])
    total_size = sum(f.stat().st_size for f in files if f.is_file())

    # Check for key deliverables
    has_demo = (deploy_dir / "demo" / "index.html").exists()
    has_proposal = (deploy_dir / "proposal" / "index.html").exists()

    marker = {
        "slug": slug,
        "staged_at": datetime.now().isoformat(),
        "deploy_dir": str(deploy_dir),
        "suggested_site_name": f"{slug}-preview",
        "file_count": file_count,
        "html_pages": html_count,
        "total_size_kb": round(total_size / 1024, 1),
        "has_demo": has_demo,
        "has_proposal": has_proposal,
        "status": "awaiting_approval",
        "deploy_command": f"python3 tools/netlify_deploy.py {slug} --deploy --site <SITE_ID>",
    }

    marker_path = get_marker_path(slug)
    with open(marker_path, "w") as f:
        json.dump(marker, f, indent=2)

    print(f"\nStaged for deploy: {slug}")
    print(f"  Deploy dir:   {deploy_dir}")
    print(f"  Files:        {file_count} ({html_count} HTML pages)")
    print(f"  Size:         {marker['total_size_kb']} KB")
    print(f"  Demo site:    {'Yes' if has_demo else 'No'}")
    print(f"  Proposal:     {'Yes' if has_proposal else 'No'}")
    print("\nAwaiting the founder's approval — do NOT deploy without an explicit green-light.")
    print(f"To deploy: python3 tools/netlify_deploy.py {slug} --deploy --site <SITE_ID>")
    print(f"No site yet? python3 tools/netlify_deploy.py {slug} --deploy --create-site {slug}-preview")


def create_site(site_name):
    """Create a new Netlify site and return its site ID."""
    print(f"Creating new Netlify site: {site_name}...")
    create = subprocess.run(
        ["netlify", "sites:create", "--name", site_name, "--json"],
        capture_output=True, text=True,
    )
    if create.returncode != 0:
        print(f"Error creating site '{site_name}' (name may be taken — pick another):")
        print(create.stderr.strip())
        sys.exit(1)
    try:
        site = json.loads(create.stdout)
        site_id = site.get("id") or site.get("site_id")
    except json.JSONDecodeError:
        site_id = None
    if not site_id:
        print("Error: could not read the new site's ID from the CLI output.")
        print("Find it with `netlify sites:list` and pass it via --site.")
        sys.exit(1)
    print(f"  Created site {site_name} (id: {site_id})")
    return site_id


def deploy(slug, site_id=None, create_site_name=None):
    marker_path = get_marker_path(slug)
    if not marker_path.exists():
        print(f"Error: No staged build found for '{slug}'. Run --stage first.")
        sys.exit(1)

    with open(marker_path) as f:
        marker = json.load(f)

    deploy_dir = get_deploy_dir(slug)

    # Resolve the target site — explicit only, never link state, never hardcoded.
    if create_site_name:
        site_id = create_site(create_site_name)
    site_id = site_id or os.environ.get("NETLIFY_SITE_ID")
    if not site_id:
        print("Error: no target site. Pass --site <SITE_ID>, set NETLIFY_SITE_ID,")
        print("or use --create-site <name> for a brand-new preview site.")
        print("(The deploy-guard hook blocks deploys without an explicit --site anyway.)")
        sys.exit(1)

    # Deploy — explicit --site always (deploy-guard doctrine). --dir is fine here
    # because staged prospect builds carry no netlify.toml of their own.
    print(f"Deploying {deploy_dir} to site {site_id}...")
    result = subprocess.run(
        ["netlify", "deploy", "--prod", "--dir", str(deploy_dir), "--site", str(site_id)],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        print(f"Deploy failed: {result.stderr}")
        sys.exit(1)

    # Extract URL from output
    url = None
    for line in result.stdout.split("\n"):
        if "https://" in line:
            parts = line.split("https://")
            if len(parts) > 1:
                url = "https://" + parts[-1].strip()
                break

    # Update marker
    marker["status"] = "deployed"
    marker["deployed_at"] = datetime.now().isoformat()
    marker["live_url"] = url
    marker["site_id"] = str(site_id)
    with open(marker_path, "w") as f:
        json.dump(marker, f, indent=2)

    print("\nDeploy command succeeded.")
    if url:
        print(f"  Live URL: {url}")
    print(f"  Site:     {site_id}")
    print("\nNot 'shipped' yet: re-fetch the live URL and confirm your content is in the")
    print("response body before telling anyone it's live (an HTTP 200 is not verification).")


def list_staged():
    staged = []
    if not CLIENTS_DIR.exists():
        print("No clients directory found.")
        return

    for client_dir in CLIENTS_DIR.iterdir():
        if client_dir.is_dir():
            marker = client_dir / "deploy-ready.json"
            if marker.exists():
                with open(marker) as f:
                    data = json.load(f)
                staged.append(data)

    if not staged:
        print("No staged builds awaiting deployment.")
        return

    print(f"\n{'Slug':<25} {'Status':<20} {'Staged At':<22} {'Files':<8}")
    print("-" * 75)
    for s in staged:
        status = s.get("status", "unknown")
        staged_at = s.get("staged_at", "?")[:19]
        print(f"{s['slug']:<25} {status:<20} {staged_at:<22} {s.get('file_count', '?'):<8}")

    awaiting = [s for s in staged if s.get("status") == "awaiting_approval"]
    if awaiting:
        print(f"\n{len(awaiting)} build(s) awaiting approval:")
        for s in awaiting:
            print(f"  python3 tools/netlify_deploy.py {s['slug']} --deploy --site <SITE_ID>")


def main():
    parser = argparse.ArgumentParser(description="Stage-then-deploy-on-approval helper (Netlify worked example)")
    parser.add_argument("slug", nargs="?", help="Client slug (folder name under clients/)")
    parser.add_argument("--stage", action="store_true", help="Stage build for review")
    parser.add_argument("--deploy", action="store_true", help="Deploy after the founder's approval")
    parser.add_argument("--site", default=None, help="Netlify site ID (or set NETLIFY_SITE_ID)")
    parser.add_argument("--create-site", default=None, metavar="NAME",
                        help="Create a new site with this name, then deploy to it")
    parser.add_argument("--list", action="store_true", help="List all staged builds")
    args = parser.parse_args()

    if args.list:
        list_staged()
        return

    if not args.slug:
        parser.print_help()
        return

    if args.stage:
        stage(args.slug)
    elif args.deploy:
        deploy(args.slug, site_id=args.site, create_site_name=args.create_site)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
