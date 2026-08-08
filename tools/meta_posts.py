#!/usr/bin/env python3
"""
meta_posts.py — fetch recent posts from a Facebook Page and Instagram Business
account via the Meta Graph API.

Usage:
  python3 tools/meta_posts.py --days 60
  python3 tools/meta_posts.py --days 30 --json
  python3 tools/meta_posts.py --days 30 --save clients/<slug>/research/posted-content.md

Requires in .env (values from your own Meta app — how to create the app, page
token, and IDs is covered in guides/meta-graph-api-setup.md; never hardcode
IDs or tokens in this file):
  META_ACCESS_TOKEN   Page access token (long-lived)
  META_PAGE_ID        Facebook Page ID
  META_IG_ID          Instagram Business account ID

Stdlib-only — no pip installs needed.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError

GRAPH = "https://graph.facebook.com/v21.0"


def load_env():
    """Read repo-root .env into a dict, overlaid by real environment variables."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    env = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    env.update({k: v for k, v in os.environ.items() if k.startswith("META_")})
    return env


def graph_get(path, params):
    url = f"{GRAPH}/{path}?{urlencode(params)}"
    try:
        with urlopen(url, timeout=30) as r:
            return json.loads(r.read())
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Graph API error {e.code} on {path}:\n{body}")


def fetch_fb_posts(page_id, token, since_unix):
    fields = "id,message,created_time,permalink_url,full_picture,attachments{media_type,media,url,subattachments}"
    params = {"fields": fields, "since": since_unix, "limit": 100, "access_token": token}
    data = graph_get(f"{page_id}/posts", params)
    return data.get("data", [])


def fetch_ig_posts(ig_user_id, token, since_dt):
    fields = "id,caption,media_type,media_product_type,media_url,thumbnail_url,permalink,timestamp"
    params = {"fields": fields, "limit": 100, "access_token": token}
    data = graph_get(f"{ig_user_id}/media", params)
    items = data.get("data", [])
    # IG endpoint doesn't support `since` directly — filter in memory
    out = []
    for p in items:
        ts = datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00"))
        if ts >= since_dt:
            p["_ts"] = ts
            out.append(p)
    return out


def truncate(s, n):
    if not s:
        return ""
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


def render_markdown(fb_posts, ig_posts):
    lines = []
    lines.append("# Posted Content — Meta (FB + IG)")
    lines.append(f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_\n")

    lines.append(f"## Facebook ({len(fb_posts)} posts)\n")
    lines.append("| Date | Type | Caption | Link |")
    lines.append("|------|------|---------|------|")
    for p in fb_posts:
        dt = datetime.fromisoformat(p["created_time"].replace("+0000", "+00:00")).strftime("%Y-%m-%d %H:%M")
        media_type = "text"
        att = p.get("attachments", {}).get("data", [])
        if att:
            media_type = att[0].get("media_type", "post")
        caption = truncate(p.get("message", ""), 140)
        link = p.get("permalink_url", "")
        link_md = f"[view]({link})" if link else ""
        lines.append(f"| {dt} | {media_type} | {caption} | {link_md} |")

    lines.append(f"\n## Instagram ({len(ig_posts)} posts)\n")
    lines.append("| Date | Type | Caption | Link |")
    lines.append("|------|------|---------|------|")
    for p in ig_posts:
        dt = p["_ts"].strftime("%Y-%m-%d %H:%M")
        mt = p.get("media_product_type") or p.get("media_type", "")
        caption = truncate(p.get("caption", ""), 140)
        link = p.get("permalink", "")
        link_md = f"[view]({link})" if link else ""
        lines.append(f"| {dt} | {mt} | {caption} | {link_md} |")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=60, help="Look back N days (default 60)")
    ap.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    ap.add_argument("--save", type=str, default=None, help="Write output to this path")
    args = ap.parse_args()

    env = load_env()
    page_id = env.get("META_PAGE_ID")
    page_token = env.get("META_ACCESS_TOKEN")
    ig_user_id = env.get("META_IG_ID")

    missing = [k for k, v in {"META_PAGE_ID": page_id, "META_ACCESS_TOKEN": page_token, "META_IG_ID": ig_user_id}.items() if not v]
    if missing:
        sys.exit(f"Missing env variables: {', '.join(missing)}\nSee guides/meta-graph-api-setup.md")

    since_dt = datetime.now(timezone.utc) - timedelta(days=args.days)
    since_unix = int(since_dt.timestamp())

    fb_posts = fetch_fb_posts(page_id, page_token, since_unix)
    ig_posts = fetch_ig_posts(ig_user_id, page_token, since_dt)

    if args.json:
        out = json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "days_back": args.days,
                "facebook": fb_posts,
                "instagram": [{**{k: v for k, v in p.items() if k != "_ts"}, "timestamp_parsed": p["_ts"].isoformat()} for p in ig_posts],
            },
            indent=2,
            default=str,
        )
    else:
        out = render_markdown(fb_posts, ig_posts)

    if args.save:
        Path(args.save).write_text(out)
        print(f"Saved to {args.save}")
    else:
        print(out)


if __name__ == "__main__":
    main()
