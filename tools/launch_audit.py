#!/usr/bin/env python3
"""
launch_audit.py — deterministic pre-launch security and readiness scanner.

Runs deterministic pre-launch checks against a local app/repo and writes a
ship/no-ship report. It is intentionally dependency-free so it can run inside
client projects, one-off exports, and AI-built app folders without setup.

Usage:
    python tools/launch_audit.py --target ./clients/<slug>/app
    python tools/launch_audit.py --target ../some-app --url https://app.example.com
    python tools/launch_audit.py --target . --client <slug> --json
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_REPORT_DIR = BASE_DIR / "reports" / "launch-audits"

TEXT_EXTENSIONS = {
    ".astro", ".cjs", ".conf", ".config", ".css", ".env", ".example", ".graphql",
    ".html", ".js", ".jsx", ".json", ".md", ".mdx", ".mjs", ".php", ".prisma",
    ".py", ".rb", ".rs", ".sh", ".sql", ".svelte", ".toml", ".ts", ".tsx",
    ".txt", ".vue", ".yaml", ".yml",
}

SKIP_DIRS = {
    ".git", ".next", ".netlify", ".nuxt", ".output", ".parcel-cache", ".turbo",
    ".vercel", "__pycache__", "build", "coverage", "dist", "node_modules",
    "public/assets", "vendor",
}

SECRET_PATTERNS = [
    ("OpenAI API key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{20,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b")),
    ("Stripe live secret key", re.compile(r"\bsk_live_[A-Za-z0-9]{20,}\b")),
    ("Stripe restricted/live key", re.compile(r"\brk_live_[A-Za-z0-9]{20,}\b")),
    ("Supabase service role JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\b")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)?PRIVATE KEY-----")),
    ("Generic secret assignment", re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-/.+=]{24,}")),
]

CLIENT_PATH_HINTS = (
    "/app/", "/pages/", "/src/", "/components/", "/public/", "/site/", "/static/"
)

API_ROUTE_HINTS = (
    "/api/", "/netlify/functions/", "/functions/", "/server/", "/routes/"
)

AUTH_MARKERS = (
    "getserversession", "auth()", "currentuser", "getuser(", "requireauth",
    "withauth", "clerk", "nextauth", "supabase.auth.getuser",
    "supabase.auth.getsession", "jwt.verify", "verifytoken", "firebase.auth",
)

AUTHZ_MARKERS = (
    "owner_id", "ownerid", "user_id", "userid", "profile_id", "tenant_id",
    "organization_id", "org_id", "auth.uid()", "where:", ".eq('user_id'",
    '.eq("user_id"', "role", "isadmin", "permission",
)

RATE_LIMIT_MARKERS = (
    "ratelimit", "rate-limit", "upstash/ratelimit", "arcjet", "limiter",
    "slow_down", "express-rate-limit", "redis.incr", "429",
)

EXPENSIVE_SERVICE_MARKERS = (
    "openai", "anthropic", "claude", "replicate", "elevenlabs",
    "stripe.checkout", "stripe.payment", "sendgrid", "resend.emails",
)


@dataclass
class Finding:
    severity: str
    category: str
    title: str
    path: str
    line: int
    evidence: str
    fix: str


def rel(path: Path, target: Path) -> str:
    try:
        return str(path.relative_to(target))
    except ValueError:
        return str(path)


def redact(value: str) -> str:
    value = value.strip()
    if len(value) <= 12:
        return "[redacted]"
    return value[:6] + "..." + value[-4:]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def iter_files(target: Path) -> Iterable[Path]:
    self_path = Path(__file__).resolve()
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        if path.resolve() == self_path:
            continue
        parts = set(path.relative_to(target).parts)
        if parts & SKIP_DIRS:
            continue
        rel_path = str(path.relative_to(target))
        if any(skip in rel_path for skip in ["/node_modules/", "/.git/", "/dist/", "/build/"]):
            continue
        if path.stat().st_size > 1_500_000:
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name in {
            ".env", ".env.local", ".env.production", ".gitignore", "Dockerfile",
            "Procfile", "next.config.js", "next.config.mjs", "netlify.toml",
        }:
            yield path


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def is_tracked_by_git(target: Path, path: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(target), "ls-files", "--error-unmatch", str(path.relative_to(target))],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def gitignore_patterns(target: Path) -> list[str]:
    gitignore = target / ".gitignore"
    if not gitignore.exists():
        return []
    patterns = []
    for line in read_text(gitignore).splitlines():
        clean = line.strip()
        if clean and not clean.startswith("#"):
            patterns.append(clean)
    return patterns


def gitignore_covers(patterns: list[str], name: str) -> bool:
    variants = {name, f"/{name}", f"*{name}*", f"{name}*"}
    return any(p in variants or fnmatch.fnmatch(name, p) for p in patterns)


def add(findings: list[Finding], severity: str, category: str, title: str,
        path: str, line: int, evidence: str, fix: str) -> None:
    findings.append(Finding(severity, category, title, path, line, evidence.strip(), fix.strip()))


def scan_secrets(target: Path, files: list[Path], findings: list[Finding]) -> None:
    ignore_patterns = gitignore_patterns(target)
    if not ignore_patterns:
        add(findings, "HIGH", "Secrets", "Missing .gitignore", ".gitignore", 1,
            "No .gitignore found in target project.",
            "Add .env, .env.local, .env.production, credentials.json, *.pem, and *.key before committing.")
    else:
        for required in [".env", ".env.local", ".env.production", "credentials.json", "*.pem", "*.key"]:
            if not gitignore_covers(ignore_patterns, required):
                add(findings, "MEDIUM", "Secrets", f".gitignore may not cover {required}", ".gitignore", 1,
                    f"Pattern not found: {required}",
                    "Update .gitignore to block committed secrets and private keys.")

    for path in files:
        text = read_text(path)
        relative = rel(path, target)

        if path.name.startswith(".env") and is_tracked_by_git(target, path):
            add(findings, "CRITICAL", "Secrets", "Tracked environment file", relative, 1,
                f"{relative} is tracked by git.",
                "Remove it from git history, rotate exposed credentials, and commit only a .env.example.")

        for label, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                raw = match.group(0)
                if "example" in raw.lower() or "your_" in raw.lower() or "placeholder" in raw.lower():
                    continue
                sev = "CRITICAL" if is_tracked_by_git(target, path) else "HIGH"
                add(findings, sev, "Secrets", f"Possible hardcoded {label}", relative,
                    line_number(text, match.start()), redact(raw),
                    "Move the secret to environment variables, rotate it if committed or shared, and add a safe example value only.")


def scan_supabase(target: Path, files: list[Path], findings: list[Finding]) -> None:
    sql_files = [p for p in files if p.suffix.lower() == ".sql" or "migration" in str(p).lower()]
    for path in sql_files:
        text = read_text(path)
        lower = text.lower()
        relative = rel(path, target)

        tables = re.findall(r"create\s+table\s+(?:if\s+not\s+exists\s+)?([a-zA-Z0-9_.\"]+)", lower)
        for table in tables:
            unquoted = table.replace('"', "")
            if f"enable row level security" not in lower and f"alter table {unquoted} enable row level security" not in lower:
                add(findings, "HIGH", "Supabase RLS", "Table created without visible RLS enablement", relative, 1,
                    f"CREATE TABLE {table} found without ENABLE ROW LEVEL SECURITY in the same file.",
                    "Enable RLS for every public table and add least-privilege SELECT/INSERT/UPDATE/DELETE policies.")

        for pattern in [r"using\s*\(\s*true\s*\)", r"with\s+check\s*\(\s*true\s*\)"]:
            for match in re.finditer(pattern, lower):
                add(findings, "CRITICAL", "Supabase RLS", "Permissive RLS policy", relative,
                    line_number(text, match.start()), text.splitlines()[line_number(text, match.start()) - 1][:180],
                    "Replace blanket true policies with ownership checks such as auth.uid() = user_id or scoped role checks.")

        if "create policy" in lower and "auth.uid()" not in lower and "service_role" not in lower:
            add(findings, "MEDIUM", "Supabase RLS", "Policy file lacks auth.uid ownership checks", relative, 1,
                "CREATE POLICY appears without auth.uid().",
                "Verify each policy enforces tenant/user ownership, not just authenticated role access.")

    for path in files:
        text = read_text(path)
        lower = text.lower()
        relative = rel(path, target)
        if "service_role" in lower and any(hint in f"/{relative}" for hint in CLIENT_PATH_HINTS):
            add(findings, "CRITICAL", "Supabase", "Service role referenced in client-facing path", relative, 1,
                "service_role appears in a client/source path.",
                "Service role keys must only exist on trusted server runtimes and never in browser-bundled code.")
        if "next_public" in lower and ("supabase_service" in lower or "service_role" in lower):
            add(findings, "CRITICAL", "Supabase", "Service role exposed through public env name", relative, 1,
                "NEXT_PUBLIC plus Supabase service role marker found.",
                "Never prefix secret keys with NEXT_PUBLIC. Rotate the key and move it to server-only env.")


def scan_api_routes(target: Path, files: list[Path], findings: list[Finding]) -> None:
    for path in files:
        relative = rel(path, target)
        rel_lower = f"/{relative.lower()}"
        if not any(hint in rel_lower for hint in API_ROUTE_HINTS):
            continue
        text = read_text(path)
        lower = text.lower()

        has_db_or_service = any(marker in lower for marker in [
            "supabase.", "prisma.", "db.", "mongodb", "mongoose", "stripe.", "openai",
            "anthropic", "fetch(", "axios.", "resend.", "sendgrid",
        ])
        if not has_db_or_service:
            continue

        if not any(marker in lower for marker in AUTH_MARKERS):
            add(findings, "HIGH", "Authentication", "API route has no obvious auth check", relative, 1,
                "Route performs database, payment, or service work but no auth marker was detected.",
                "Require a server-side session/user check before performing work. Do not rely on client-side route hiding.")

        if any(marker in lower for marker in EXPENSIVE_SERVICE_MARKERS) and not any(marker in lower for marker in RATE_LIMIT_MARKERS):
            add(findings, "HIGH", "Rate Limiting", "Expensive endpoint lacks rate limiting", relative, 1,
                "AI/payment/email provider marker found without a rate-limit marker.",
                "Add per-user and per-IP rate limits before invoking paid APIs or write-heavy workflows.")

        takes_object_id = re.search(r"(params\.|searchparams|query\.|req\.query|body\.).{0,80}\b(id|user_id|project_id|invoice_id|order_id)\b", lower)
        writes_or_reads = any(marker in lower for marker in [".update(", ".delete(", ".insert(", ".select(", "findunique", "findfirst", "findmany"])
        if takes_object_id and writes_or_reads and not any(marker in lower for marker in AUTHZ_MARKERS):
            add(findings, "CRITICAL", "Authorization", "Possible object-level authorization gap", relative,
                line_number(text, takes_object_id.start()), takes_object_id.group(0)[:180],
                "When an endpoint accepts an object ID, verify the authenticated user owns or is allowed to access that specific object.")

        if "access-control-allow-origin" in lower and "*" in lower:
            add(findings, "MEDIUM", "Deployment", "Wildcard CORS in API route", relative, 1,
                "Access-Control-Allow-Origin wildcard detected.",
                "Restrict CORS to known origins when credentials, private data, or write APIs are involved.")


def scan_stripe(target: Path, files: list[Path], findings: list[Finding]) -> None:
    for path in files:
        text = read_text(path)
        lower = text.lower()
        if "stripe" not in lower or "webhook" not in lower:
            continue
        relative = rel(path, target)
        has_signature = "stripe-signature" in lower or "constructevent" in lower or "webhooks.constructevent" in lower
        if not has_signature:
            add(findings, "CRITICAL", "Stripe", "Stripe webhook may not verify signatures", relative, 1,
                "Webhook handler mentions Stripe but no Stripe-Signature/constructEvent marker was detected.",
                "Verify webhook signatures with Stripe's official library before trusting any event payload.")
        if "json()" in lower and "constructevent" in lower and "raw" not in lower:
            add(findings, "MEDIUM", "Stripe", "Webhook may parse JSON before signature verification", relative, 1,
                "constructEvent appears near JSON parsing without a raw body marker.",
                "Use the raw request body for Stripe signature verification, then parse the verified event.")


def scan_validation_and_errors(target: Path, files: list[Path], findings: list[Finding]) -> None:
    for path in files:
        relative = rel(path, target)
        rel_lower = f"/{relative.lower()}"
        text = read_text(path)
        lower = text.lower()
        if not any(hint in rel_lower for hint in API_ROUTE_HINTS):
            continue

        accepts_input = any(marker in lower for marker in ["req.body", "request.json", "formdata", "searchparams", "req.query"])
        if accepts_input and not any(marker in lower for marker in ["zod", "yup", "joi", "valibot", "safeparse", "schema.parse", "validator"]):
            add(findings, "MEDIUM", "Input Validation", "Endpoint accepts input without obvious schema validation", relative, 1,
                "Request body/query marker found without common validation library or schema marker.",
                "Validate all client-controlled input at the server boundary with a schema and reject unknown fields.")

        does_external_work = any(marker in lower for marker in ["fetch(", "axios.", "stripe.", "openai", "supabase.", "prisma."])
        if does_external_work and "try" not in lower and "catch" not in lower:
            add(findings, "LOW", "Reliability", "No obvious error handling around external work", relative, 1,
                "External API/database marker found without try/catch.",
                "Add explicit error handling, safe logging, and user-safe error responses for failed external calls.")


def scan_dependencies(target: Path, files: list[Path], findings: list[Finding]) -> None:
    dep_files = [p for p in files if p.name in {"package.json", "requirements.txt", "pyproject.toml", "Gemfile"}]
    for path in dep_files:
        relative = rel(path, target)
        text = read_text(path)
        if path.name == "package.json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                add(findings, "MEDIUM", "Dependencies", "Invalid package.json", relative, 1,
                    "Could not parse package.json.",
                    "Fix JSON syntax before installing or deploying dependencies.")
                continue
            deps = {}
            deps.update(data.get("dependencies", {}))
            deps.update(data.get("devDependencies", {}))
            for name, version in sorted(deps.items()):
                if version in {"*", "latest"} or str(version).startswith("git+") or "github:" in str(version):
                    add(findings, "MEDIUM", "Dependencies", "Unpinned or remote dependency", relative, 1,
                        f"{name}: {version}",
                        "Pin dependencies to reviewed semver ranges and verify package legitimacy before install.")
            scripts = data.get("scripts", {})
            for script_name, command in scripts.items():
                if any(token in command for token in ["curl ", "wget ", "rm -rf /", "chmod 777"]):
                    add(findings, "HIGH", "Dependencies", "Risky package script", relative, 1,
                        f"{script_name}: {command[:160]}",
                        "Review install/build scripts for supply-chain risk before running in CI or production.")


def scan_deployment(target: Path, files: list[Path], findings: list[Finding]) -> None:
    names = {p.name for p in files}
    if {"next.config.js", "next.config.mjs", "next.config.ts"} & names:
        next_files = [p for p in files if p.name.startswith("next.config")]
        combined = "\n".join(read_text(p).lower() for p in next_files)
        if "headers()" not in combined and "content-security-policy" not in combined:
            add(findings, "LOW", "Deployment", "No security headers found in Next config", "next.config", 1,
                "Next config exists without obvious headers() or CSP marker.",
                "Add baseline headers: Content-Security-Policy, X-Frame-Options/frame-ancestors, Referrer-Policy, and Permissions-Policy.")

    for path in files:
        text = read_text(path)
        lower = text.lower()
        relative = rel(path, target)
        if "debug=true" in lower or "debug: true" in lower or ("development" in lower and "production" in lower and "todo" in lower):
            add(findings, "LOW", "Deployment", "Possible debug/development flag", relative, 1,
                "Debug/development marker found.",
                "Verify production deploys disable debug output and verbose errors.")


def fetch_url_headers(url: str, findings: list[Finding]) -> dict[str, str]:
    if not url:
        return {}
    parsed = urlparse(url)
    if parsed.scheme != "https":
        add(findings, "HIGH", "Deployment", "URL is not HTTPS", url, 1,
            "Audit URL does not use https://.",
            "Force HTTPS for all production sites and redirect HTTP to HTTPS.")
    try:
        req = Request(url, headers={"User-Agent": "LaunchAudit/1.0"})
        with urlopen(req, timeout=12) as response:
            headers = {k.lower(): v for k, v in response.headers.items()}
    except Exception as exc:
        add(findings, "LOW", "Live URL", "Could not fetch live URL", url, 1,
            str(exc), "Manually verify deployment status and public headers.")
        return {}

    required = {
        "content-security-policy": "Add a Content-Security-Policy appropriate for the app.",
        "x-frame-options": "Add X-Frame-Options or CSP frame-ancestors to reduce clickjacking risk.",
        "referrer-policy": "Add Referrer-Policy to control cross-origin referrer leakage.",
    }
    for header, fix in required.items():
        if header not in headers:
            add(findings, "LOW", "Live URL", f"Missing {header} header", url, 1,
                f"{header} not present in live response.", fix)
    return headers


def detect_stack(files: list[Path]) -> list[str]:
    names = {p.name for p in files}
    stack = []
    if "next.config.js" in names or "next.config.mjs" in names or any("/app/" in str(p) for p in files):
        stack.append("Next.js")
    if "package.json" in names:
        stack.append("Node/TypeScript")
    if any("supabase" in read_text(p).lower() for p in files if p.suffix.lower() in {".ts", ".tsx", ".js", ".jsx", ".sql"}):
        stack.append("Supabase")
    if any("stripe" in read_text(p).lower() for p in files if p.suffix.lower() in {".ts", ".tsx", ".js", ".jsx", ".py"}):
        stack.append("Stripe")
    if any("openai" in read_text(p).lower() or "anthropic" in read_text(p).lower() for p in files if p.suffix.lower() in {".ts", ".tsx", ".js", ".jsx", ".py"}):
        stack.append("AI APIs")
    if "netlify.toml" in names:
        stack.append("Netlify")
    if "vercel.json" in names:
        stack.append("Vercel")
    return sorted(set(stack))


def severity_counts(findings: list[Finding]) -> dict[str, int]:
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return counts


def verdict(counts: dict[str, int]) -> tuple[str, str]:
    if counts.get("CRITICAL", 0) > 0:
        return "DO NOT SHIP", "High"
    if counts.get("HIGH", 0) >= 3:
        return "DO NOT SHIP", "High"
    if counts.get("HIGH", 0) > 0 or counts.get("MEDIUM", 0) >= 5:
        return "SHIP WITH FIXES", "Medium"
    return "OK TO SHIP AFTER MANUAL REVIEW", "Low"


def render_markdown(target: Path, url: str, stack: list[str], findings: list[Finding]) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    counts = severity_counts(findings)
    ship_verdict, risk = verdict(counts)
    sorted_findings = sorted(findings, key=lambda f: ["CRITICAL", "HIGH", "MEDIUM", "LOW"].index(f.severity))
    blocking = [f for f in sorted_findings if f.severity in {"CRITICAL", "HIGH"}]

    lines = [
        "# Launch Audit Report",
        "",
        f"- **Target:** `{target}`",
        f"- **URL:** {url or 'Not provided'}",
        f"- **Generated:** {now}",
        f"- **Detected stack:** {', '.join(stack) if stack else 'Unknown/static'}",
        f"- **Verdict:** {ship_verdict}",
        f"- **Launch risk:** {risk}",
        f"- **Findings:** {counts['CRITICAL']} critical, {counts['HIGH']} high, {counts['MEDIUM']} medium, {counts['LOW']} low",
        "",
        "## Fix First",
    ]

    if not blocking:
        lines.append("No critical or high findings from deterministic checks. Manual review is still required for business logic.")
    else:
        for index, finding in enumerate(blocking[:10], start=1):
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            lines.extend([
                f"{index}. **{finding.severity} - {finding.title}**",
                f"   - Location: `{location}`",
                f"   - Evidence: {finding.evidence}",
                f"   - Fix: {finding.fix}",
            ])

    lines.extend(["", "## All Findings"])
    if not sorted_findings:
        lines.append("No deterministic findings. This does not replace a human security review.")
    else:
        for finding in sorted_findings:
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            lines.extend([
                f"### {finding.severity} - {finding.title}",
                f"- Category: {finding.category}",
                f"- Location: `{location}`",
                f"- Evidence: {finding.evidence}",
                f"- Recommended fix: {finding.fix}",
                "",
            ])

    lines.extend([
        "## Manual Review Checklist",
        "- Verify object-level authorization by trying to access another user's records.",
        "- Confirm Supabase RLS policies against real anon and authenticated sessions.",
        "- Confirm Stripe webhook signature verification with a test event.",
        "- Exercise paid/AI endpoints repeatedly and confirm rate limits return 429.",
        "- Review production logs for safe errors, no secrets, and enough context to debug failures.",
        "- Run dependency tooling where available: `npm audit`, `pip-audit`, Semgrep, CodeQL, or Snyk.",
        "",
        "## Coding-Agent Fix Prompt",
        "```text",
        "You are doing a pre-launch security hardening pass. Fix the Launch Audit findings below without unrelated refactors.",
        "Prioritize CRITICAL and HIGH findings first. Add focused tests or verification notes where practical.",
        "",
        *[
            f"- {f.severity}: {f.title} at {f.path}:{f.line}. Fix: {f.fix}"
            for f in blocking[:8]
        ],
        "```",
    ])

    return "\n".join(lines) + "\n"


def run_audit(target: Path, url: str = "") -> dict:
    target = target.resolve()
    files = list(iter_files(target))
    findings: list[Finding] = []

    scan_secrets(target, files, findings)
    scan_supabase(target, files, findings)
    scan_api_routes(target, files, findings)
    scan_stripe(target, files, findings)
    scan_validation_and_errors(target, files, findings)
    scan_dependencies(target, files, findings)
    scan_deployment(target, files, findings)
    if url:
        fetch_url_headers(url, findings)

    stack = detect_stack(files)
    counts = severity_counts(findings)
    ship_verdict, risk = verdict(counts)
    return {
        "target": str(target),
        "url": url,
        "stack": stack,
        "verdict": ship_verdict,
        "risk": risk,
        "counts": counts,
        "findings": [asdict(f) for f in findings],
        "markdown": render_markdown(target, url, stack, findings),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic pre-launch security and readiness checks.")
    parser.add_argument("--target", required=True, help="Local project/app directory to audit.")
    parser.add_argument("--url", default="", help="Optional deployed URL for live header checks.")
    parser.add_argument("--client", default="", help="Optional client slug for report naming.")
    parser.add_argument("--output-dir", default=str(DEFAULT_REPORT_DIR), help="Directory for markdown/json reports.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout instead of markdown summary.")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists() or not target.is_dir():
        raise SystemExit(f"Target directory does not exist: {target}")

    result = run_audit(target, args.url)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    date = dt.datetime.now().strftime("%Y-%m-%d-%H%M")
    client = args.client or target.name
    safe_client = re.sub(r"[^A-Za-z0-9_.-]+", "-", client).strip("-").lower()
    md_path = output_dir / f"{date}-{safe_client}-launch-audit.md"
    json_path = output_dir / f"{date}-{safe_client}-launch-audit.json"
    md_path.write_text(result["markdown"], encoding="utf-8")
    json_path.write_text(json.dumps({k: v for k, v in result.items() if k != "markdown"}, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps({k: v for k, v in result.items() if k != "markdown"}, indent=2))
    else:
        print(result["markdown"])
        print(f"Saved markdown: {md_path}")
        print(f"Saved JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
