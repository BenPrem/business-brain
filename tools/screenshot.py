"""
screenshot.py — headless website screenshot tool.

Takes screenshots of websites at desktop and mobile viewports. Designed to run
headless (no display needed) — useful for side-by-side current-vs-redesign
comparisons in prospect workups and pre-delivery QA.

Usage:
    python tools/screenshot.py --url "https://example.com" --output screenshots/
    python tools/screenshot.py --url "https://example.com" --viewport mobile
    python tools/screenshot.py --url "https://example.com" --viewport both --output clients/<slug>/preview/

Requires:
    - pip install playwright
    - playwright install chromium
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERROR: playwright not installed.")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)


VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 375, "height": 812},
    "tablet": {"width": 768, "height": 1024},
}

DEFAULT_OUTPUT = Path(__file__).parent.parent / "screenshots"


async def take_screenshot(url, viewport_name="desktop", output_dir=None, filename=None, full_page=True):
    """
    Take a screenshot of a URL at a specific viewport.

    Args:
        url:           URL to screenshot
        viewport_name: "desktop", "mobile", or "tablet"
        output_dir:    Directory to save screenshot (default: screenshots/)
        filename:      Custom filename (default: auto-generated from URL + viewport)
        full_page:     Capture full scrollable page (default: True)

    Returns:
        str: Path to saved screenshot
    """
    viewport = VIEWPORTS.get(viewport_name, VIEWPORTS["desktop"])
    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT
    out_dir.mkdir(parents=True, exist_ok=True)

    if not filename:
        # Generate filename from URL
        slug = url.replace("https://", "").replace("http://", "").replace("/", "_").rstrip("_")
        slug = slug[:50]  # Truncate long URLs
        filename = f"{slug}_{viewport_name}.png"

    out_path = out_dir / filename

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport=viewport,
            device_scale_factor=2,  # Retina quality
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            # Wait a bit for lazy-loaded content
            await page.wait_for_timeout(2000)

            await page.screenshot(path=str(out_path), full_page=full_page)
            print(f"  Screenshot saved: {out_path}")

        except Exception as e:
            print(f"  Error screenshotting {url}: {e}")
            out_path = None

        finally:
            await browser.close()

    return str(out_path) if out_path else None


async def take_both(url, output_dir=None, prefix=None):
    """Take both desktop and mobile screenshots. Returns dict of paths."""
    results = {}
    for vp in ["desktop", "mobile"]:
        fname = f"{prefix}_{vp}.png" if prefix else None
        path = await take_screenshot(url, viewport_name=vp, output_dir=output_dir, filename=fname)
        results[vp] = path
    return results


async def take_comparison(current_url, demo_url, output_dir):
    """
    Take all 4 screenshots needed for a side-by-side preview page:
    current site (desktop + mobile) and demo site (desktop + mobile).
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    print(f"Screenshotting current site: {current_url}")
    results["current_desktop"] = await take_screenshot(
        current_url, "desktop", output_dir, "current_desktop.png"
    )
    results["current_mobile"] = await take_screenshot(
        current_url, "mobile", output_dir, "current_mobile.png"
    )

    print(f"Screenshotting demo site: {demo_url}")
    results["demo_desktop"] = await take_screenshot(
        demo_url, "desktop", output_dir, "demo_desktop.png"
    )
    results["demo_mobile"] = await take_screenshot(
        demo_url, "mobile", output_dir, "demo_mobile.png"
    )

    return results


def screenshot(url, viewport="desktop", output_dir=None, filename=None, full_page=True):
    """Synchronous wrapper for take_screenshot."""
    return asyncio.run(take_screenshot(url, viewport, output_dir, filename, full_page))


def screenshot_both(url, output_dir=None, prefix=None):
    """Synchronous wrapper for take_both."""
    return asyncio.run(take_both(url, output_dir, prefix))


def screenshot_comparison(current_url, demo_url, output_dir):
    """Synchronous wrapper for take_comparison."""
    return asyncio.run(take_comparison(current_url, demo_url, output_dir))


def main():
    parser = argparse.ArgumentParser(description="Headless website screenshot tool")
    parser.add_argument("--url", required=True, help="URL to screenshot")
    parser.add_argument("--viewport", default="both", choices=["desktop", "mobile", "tablet", "both"])
    parser.add_argument("--output", default=None, help="Output directory")
    parser.add_argument("--filename", default=None, help="Custom filename")
    parser.add_argument("--no-full-page", action="store_true", help="Capture viewport only, not full page")
    args = parser.parse_args()

    if args.viewport == "both":
        results = screenshot_both(args.url, args.output)
        print(f"\nDesktop: {results.get('desktop')}")
        print(f"Mobile:  {results.get('mobile')}")
    else:
        path = screenshot(args.url, args.viewport, args.output, args.filename, not args.no_full_page)
        print(f"\nSaved: {path}")


if __name__ == "__main__":
    main()
