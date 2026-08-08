#!/usr/bin/env python3
"""
shot.py — the screenshot-critique harness.

Renders a real page in headless Chromium and captures what a code review cannot
see: widows, muddy contrast, dead zones, broken layout. Also captures console
errors and document height, so a silent JS failure can't hide behind a pretty
screenshot — a page whose script crashed often still LOOKS fine at the top.

Method: render -> LOOK AT THE PIXELS -> fix -> add one deliberate upgrade.

Usage:
    python3 tools/shot.py <url> <outdir> [--viewports 1440x900,390x844] [--full]

Mobile QA discipline: viewport-only screenshots at real device sizes with
sequential scrolls — never full_page=True, which lies about what a phone shows.

Requires:
    pip install playwright && playwright install chromium
"""
import sys, os, json, argparse
from playwright.sync_api import sync_playwright

DEFAULT_VIEWPORTS = ["1440x900", "768x1024", "390x844", "375x667"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("outdir")
    ap.add_argument("--viewports", default=",".join(DEFAULT_VIEWPORTS))
    ap.add_argument("--wait", type=int, default=2500, help="ms to settle (fonts, video, IO)")
    ap.add_argument("--full", action="store_true", help="also take one full-page desktop shot")
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    report = {"url": a.url, "viewports": {}, "errors": []}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vp in a.viewports.split(","):
            w, h = (int(x) for x in vp.split("x"))
            ctx = browser.new_context(viewport={"width": w, "height": h},
                                      device_scale_factor=2 if w <= 768 else 1)
            page = ctx.new_page()
            errs = []
            page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errs.append(str(e)))

            page.goto(a.url, wait_until="networkidle")
            page.wait_for_timeout(a.wait)

            doc_h = page.evaluate("document.body.scrollHeight")
            # Scroll positions: top / mid / bottom. Viewport-only, never full_page.
            spots = {"top": 0, "mid": max(0, (doc_h - h) // 2), "bot": max(0, doc_h - h)}
            for name, y in spots.items():
                page.evaluate(f"window.scrollTo(0,{y})")
                page.wait_for_timeout(900)  # entrance transitions are ~.7s; do not shoot mid-fade
                page.screenshot(path=os.path.join(a.outdir, f"{vp}-{name}.png"))

            # Horizontal overflow is a hard fail on mobile.
            overflow = page.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth")

            report["viewports"][vp] = {"docHeight": doc_h, "hOverflow": overflow, "errors": errs}
            report["errors"] += errs
            ctx.close()

        if a.full:
            ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            page = ctx.new_page()
            page.goto(a.url, wait_until="networkidle")
            page.wait_for_timeout(a.wait)
            page.screenshot(path=os.path.join(a.outdir, "full.png"), full_page=True)
            ctx.close()

        browser.close()

    print(json.dumps(report, indent=2))
    # Non-zero exit if anything is objectively broken.
    broken = report["errors"] or any(v["hOverflow"] for v in report["viewports"].values())
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
