#!/usr/bin/env python3
"""
meta_insights.py — page/account-level stats plus per-post engagement insights
from the Meta Graph API (Facebook Page + Instagram Business account).

Outputs:
  - FB/IG follower counts
  - Per-post reach, engagement, reactions, comments, shares
  - For IG reels: plays, saves
  - Top-10 posts by reach and by engagement

Usage:
  python3 tools/meta_insights.py --days 60
  python3 tools/meta_insights.py --days 60 --save clients/<slug>/research/meta-insights-60d.md

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


def require_env(env):
    page_id = env.get("META_PAGE_ID")
    token = env.get("META_ACCESS_TOKEN")
    ig_id = env.get("META_IG_ID")
    missing = [k for k, v in {
        "META_PAGE_ID": page_id,
        "META_ACCESS_TOKEN": token,
        "META_IG_ID": ig_id,
    }.items() if not v]
    if missing:
        sys.exit(f"Missing env variables: {', '.join(missing)}\nSee guides/meta-graph-api-setup.md")
    return page_id, token, ig_id


def graph_get(path, params, silent=False):
    url = f"{GRAPH}/{path}?{urlencode(params)}"
    try:
        with urlopen(url, timeout=30) as r:
            return json.loads(r.read())
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if silent:
            return {"_error": body, "_code": e.code}
        raise SystemExit(f"Graph API error {e.code} on {path}:\n{body}")


def fetch_page_info(page_id, token):
    params = {"fields": "name,followers_count,fan_count", "access_token": token}
    return graph_get(page_id, params, silent=True)


def fetch_ig_info(ig_id, token):
    params = {"fields": "username,followers_count,media_count,name", "access_token": token}
    return graph_get(ig_id, params, silent=True)


def fetch_fb_posts(page_id, token, since_unix):
    fields = (
        "id,message,created_time,permalink_url,attachments{media_type},"
        "reactions.summary(total_count).limit(0),"
        "comments.summary(total_count).limit(0),"
        "shares"
    )
    params = {"fields": fields, "since": since_unix, "limit": 100, "access_token": token}
    data = graph_get(f"{page_id}/posts", params)
    posts = data.get("data", [])
    for p in posts:
        p["_insights"] = fetch_fb_post_insights(p["id"], token)
    return posts


def fetch_fb_post_insights(post_id, token):
    metrics_to_try = [
        "post_impressions",
        "post_impressions_unique",
        "post_reactions_by_type_total",
        "post_clicks",
        "post_video_views_organic",
    ]
    out = {}
    for m in metrics_to_try:
        params = {"metric": m, "access_token": token}
        data = graph_get(f"{post_id}/insights", params, silent=True)
        if "_error" in data:
            continue
        for item in data.get("data", []):
            vals = item.get("values", [])
            if vals:
                out[item["name"]] = vals[0].get("value", 0)
    return out


def fetch_ig_posts(ig_user_id, token, since_dt):
    fields = (
        "id,caption,media_type,media_product_type,permalink,timestamp,"
        "like_count,comments_count"
    )
    params = {"fields": fields, "limit": 100, "access_token": token}
    data = graph_get(f"{ig_user_id}/media", params)
    items = data.get("data", [])
    out = []
    for p in items:
        ts = datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00"))
        if ts >= since_dt:
            p["_ts"] = ts
            out.append(p)
    return out


def fetch_ig_post_insights(media_id, media_product_type, token):
    if media_product_type == "REELS":
        metrics = "reach,plays,saved,shares,total_interactions"
    elif media_product_type == "STORY":
        metrics = "reach,impressions"
    else:
        metrics = "reach,saved,shares,total_interactions"
    params = {"metric": metrics, "access_token": token}
    data = graph_get(f"{media_id}/insights", params, silent=True)
    out = {}
    for item in data.get("data", []):
        name = item.get("name")
        vals = item.get("values", [])
        if vals:
            out[name] = vals[0].get("value", 0)
    return out


def summarize_fb(p):
    msg = (p.get("message") or "").strip()
    att = p.get("attachments", {}).get("data", [])
    media_type = att[0].get("media_type", "text") if att else "text"
    reactions = p.get("reactions", {}).get("summary", {}).get("total_count", 0)
    comments = p.get("comments", {}).get("summary", {}).get("total_count", 0)
    shares = p.get("shares", {}).get("count", 0) if p.get("shares") else 0
    insights = p.get("_insights", {})
    impressions = insights.get("post_impressions", 0)
    reach = insights.get("post_impressions_unique", 0)
    video_views = insights.get("post_video_views_organic", 0)
    clicks = insights.get("post_clicks", 0)
    engagement = reactions + comments + shares
    return {
        "date": p["created_time"][:10],
        "type": media_type,
        "caption": (msg[:90] + "…") if len(msg) > 90 else msg,
        "reach": reach,
        "impressions": impressions,
        "video_views": video_views,
        "clicks": clicks,
        "reactions": reactions,
        "comments": comments,
        "shares": shares,
        "engagement": engagement,
        "eng_rate_pct": round(engagement / reach * 100, 1) if reach else 0,
        "link": p.get("permalink_url", ""),
    }


def summarize_ig(p, insights):
    cap = (p.get("caption") or "").strip()
    mpt = p.get("media_product_type") or p.get("media_type")
    likes = p.get("like_count", 0)
    comments = p.get("comments_count", 0)
    reach = insights.get("reach", 0)
    plays = insights.get("plays", 0)
    saved = insights.get("saved", 0)
    shares = insights.get("shares", 0)
    total_inter = insights.get("total_interactions", 0)
    engagement = total_inter or (likes + comments + saved + shares)
    return {
        "date": p["_ts"].strftime("%Y-%m-%d"),
        "type": mpt,
        "caption": (cap[:90] + "…") if len(cap) > 90 else cap,
        "reach": reach,
        "plays": plays,
        "likes": likes,
        "comments": comments,
        "saved": saved,
        "shares": shares,
        "engagement": engagement,
        "eng_rate_pct": round(engagement / reach * 100, 1) if reach else 0,
        "link": p.get("permalink", ""),
    }


def render_markdown(page_info, ig_info, fb, ig, days):
    lines = []
    lines.append(f"# {page_info.get('name', 'Page')} — Meta Analytics Snapshot")
    lines.append(f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · Lookback: {days} days_\n")

    lines.append("## Page-Level")
    lines.append(f"- **Facebook Page:** {page_info.get('name', '?')}")
    lines.append(f"  - Followers: **{page_info.get('followers_count', 'n/a')}**")
    lines.append(f"  - Fans (likes): **{page_info.get('fan_count', 'n/a')}**")
    lines.append(f"- **Instagram:** @{ig_info.get('username', '?')}")
    lines.append(f"  - Followers: **{ig_info.get('followers_count', 'n/a')}**")
    lines.append(f"  - Total posts: **{ig_info.get('media_count', 'n/a')}**")
    lines.append("")

    # FB aggregates
    if fb:
        total_reach = sum(p["reach"] for p in fb)
        total_eng = sum(p["engagement"] for p in fb)
        avg_reach = round(total_reach / len(fb)) if fb else 0
        avg_eng = round(total_eng / len(fb)) if fb else 0
        avg_eng_rate = round(sum(p["eng_rate_pct"] for p in fb) / len(fb), 1)
        lines.append(f"## Facebook — {len(fb)} posts (last {days}d)")
        lines.append(f"- Avg reach/post: **{avg_reach}**")
        lines.append(f"- Avg engagement/post: **{avg_eng}** (reactions+comments+shares)")
        lines.append(f"- Avg engagement rate: **{avg_eng_rate}%**")
        lines.append("")

        lines.append("### FB Top 10 by Reach")
        lines.append("| Date | Type | Reach | Eng | ER% | Caption |")
        lines.append("|------|------|-------|-----|-----|---------|")
        for p in sorted(fb, key=lambda x: x["reach"], reverse=True)[:10]:
            lines.append(
                f"| {p['date']} | {p['type']} | {p['reach']} | {p['engagement']} | {p['eng_rate_pct']} | {p['caption']} |"
            )
        lines.append("")

        lines.append("### FB Top 10 by Engagement Rate")
        eligible = [p for p in fb if p["reach"] >= 50]
        lines.append("| Date | Type | Reach | Eng | ER% | Caption |")
        lines.append("|------|------|-------|-----|-----|---------|")
        for p in sorted(eligible, key=lambda x: x["eng_rate_pct"], reverse=True)[:10]:
            lines.append(
                f"| {p['date']} | {p['type']} | {p['reach']} | {p['engagement']} | {p['eng_rate_pct']} | {p['caption']} |"
            )
        lines.append("")

    # IG aggregates
    if ig:
        ig_with_reach = [p for p in ig if p["reach"] > 0]
        if ig_with_reach:
            total_reach = sum(p["reach"] for p in ig_with_reach)
            total_eng = sum(p["engagement"] for p in ig_with_reach)
            avg_reach = round(total_reach / len(ig_with_reach))
            avg_eng = round(total_eng / len(ig_with_reach))
            avg_eng_rate = round(sum(p["eng_rate_pct"] for p in ig_with_reach) / len(ig_with_reach), 1)
            lines.append(f"## Instagram — {len(ig)} posts (last {days}d)")
            lines.append(f"- Avg reach/post: **{avg_reach}**")
            lines.append(f"- Avg engagement/post: **{avg_eng}**")
            lines.append(f"- Avg engagement rate: **{avg_eng_rate}%**")
            lines.append("")

            lines.append("### IG Top 10 by Reach")
            lines.append("| Date | Type | Reach | Plays | Likes | Cmt | Save | Shr | ER% | Caption |")
            lines.append("|------|------|-------|-------|-------|-----|------|-----|-----|---------|")
            for p in sorted(ig, key=lambda x: x["reach"], reverse=True)[:10]:
                lines.append(
                    f"| {p['date']} | {p['type']} | {p['reach']} | {p['plays']} | {p['likes']} | {p['comments']} | {p['saved']} | {p['shares']} | {p['eng_rate_pct']} | {p['caption']} |"
                )
            lines.append("")

            lines.append("### IG Top 10 by Engagement Rate")
            eligible = [p for p in ig if p["reach"] >= 50]
            lines.append("| Date | Type | Reach | Likes | Cmt | Save | Shr | ER% | Caption |")
            lines.append("|------|------|-------|-------|-----|------|-----|-----|---------|")
            for p in sorted(eligible, key=lambda x: x["eng_rate_pct"], reverse=True)[:10]:
                lines.append(
                    f"| {p['date']} | {p['type']} | {p['reach']} | {p['likes']} | {p['comments']} | {p['saved']} | {p['shares']} | {p['eng_rate_pct']} | {p['caption']} |"
                )
            lines.append("")

    # Format breakdown
    if ig:
        by_type = {}
        for p in ig:
            by_type.setdefault(p["type"], []).append(p)
        lines.append("### IG Format Breakdown")
        lines.append("| Type | Count | Avg Reach | Avg Eng | Avg Saves |")
        lines.append("|------|-------|-----------|---------|-----------|")
        for t, items in by_type.items():
            avg_r = round(sum(x["reach"] for x in items) / len(items))
            avg_e = round(sum(x["engagement"] for x in items) / len(items))
            avg_s = round(sum(x["saved"] for x in items) / len(items), 1)
            lines.append(f"| {t} | {len(items)} | {avg_r} | {avg_e} | {avg_s} |")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--save", type=str, default=None)
    args = ap.parse_args()

    env = load_env()
    page_id, token, ig_id = require_env(env)

    since_dt = datetime.now(timezone.utc) - timedelta(days=args.days)
    since_unix = int(since_dt.timestamp())

    print("Fetching page info…", file=sys.stderr)
    page_info = fetch_page_info(page_id, token)
    ig_info = fetch_ig_info(ig_id, token)

    print("Fetching FB posts + insights…", file=sys.stderr)
    fb_posts = fetch_fb_posts(page_id, token, since_unix)
    fb_summary = [summarize_fb(p) for p in fb_posts]

    print("Fetching IG posts…", file=sys.stderr)
    ig_posts = fetch_ig_posts(ig_id, token, since_dt)

    print(f"Fetching insights for {len(ig_posts)} IG posts…", file=sys.stderr)
    ig_summary = []
    for p in ig_posts:
        mpt = p.get("media_product_type") or p.get("media_type")
        ins = fetch_ig_post_insights(p["id"], mpt, token)
        ig_summary.append(summarize_ig(p, ins))

    out = render_markdown(page_info, ig_info, fb_summary, ig_summary, args.days)

    if args.save:
        Path(args.save).write_text(out)
        print(f"Saved to {args.save}")
    else:
        print(out)


if __name__ == "__main__":
    main()
