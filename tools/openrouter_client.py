"""
openrouter_client.py — OpenRouter API client with 60/30/10 model routing.

Reusable wrapper for calling LLMs via OpenRouter: 60% of calls should hit cheap
models (bulk work), 30% mid-tier (content), 10% premium (orchestration/complex
reasoning). Never prints or logs the API key.

Usage:
    from openrouter_client import complete, complete_cheap, complete_mid, complete_premium

    # Auto-route by tier
    result = complete_cheap("Summarize this website content: ...")
    result = complete_mid("Write a marketing plan based on: ...")
    result = complete_premium("Build an HTML page with conversion-focused copy: ...")

    # Direct model call
    result = complete("Your prompt", model="anthropic/claude-haiku-4.5")

    # With system prompt
    result = complete("User message", system="You are a marketing analyst.", tier="mid")

    # With JSON mode
    result = complete("Return competitor data as JSON", tier="cheap", json_mode=True)

Requires:
    - OPENROUTER_API_KEY in .env
    - pip install requests python-dotenv
"""

import os
import json
import time
import logging
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests python-dotenv")
    exit(1)

load_dotenv()

logger = logging.getLogger("openrouter")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# Optional attribution shown on OpenRouter's dashboard — set in .env or leave blank.
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "business-brain")

# ============================================================================
# MODEL ROUTING (60/30/10 rule)
# ============================================================================
# Cheap: bulk work, scraping, classification, data extraction
# Mid:   content writing, research synthesis, structured analysis
# Premium: complex builds (websites, proposals), strategic reasoning
#
# Validate slugs against the live API before editing (slugs rot):
#   curl -s https://openrouter.ai/api/v1/models | python3 -c "import json,sys; \
#     print('\n'.join(m['id'] for m in json.load(sys.stdin)['data']))" | grep -i <family>
MODELS = {
    "cheap": [
        "google/gemini-2.5-flash-lite",
        "meta-llama/llama-3.1-8b-instruct",
    ],
    "mid": [
        "anthropic/claude-haiku-4.5",
        "openai/gpt-4o-mini",
    ],
    "premium": [
        "anthropic/claude-sonnet-4.6",
    ],
}

# Fallback chain: if primary fails, try next in tier, then escalate
ESCALATION = {"cheap": "mid", "mid": "premium", "premium": None}

# Rate limiting
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds, doubles each retry


def _get_model(tier="cheap", index=0):
    """Get model string for a tier. Index selects fallback within tier."""
    models = MODELS.get(tier, MODELS["cheap"])
    return models[min(index, len(models) - 1)]


def complete(
    prompt,
    system=None,
    model=None,
    tier="cheap",
    max_tokens=4000,
    temperature=0.3,
    json_mode=False,
    timeout=60,
):
    """
    Call OpenRouter with automatic retry and fallback.

    Args:
        prompt:      User message (string)
        system:      System prompt (optional)
        model:       Specific model string (overrides tier)
        tier:        "cheap", "mid", or "premium" — picks from MODELS dict
        max_tokens:  Max response tokens
        temperature: 0.0 = deterministic, 1.0 = creative
        json_mode:   If True, request JSON response format
        timeout:     Request timeout in seconds

    Returns:
        str: The model's response text

    Raises:
        RuntimeError: If all retries and fallbacks exhausted
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set in .env")

    # Build messages
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # Try primary model, then fallbacks within tier, then escalate
    current_tier = tier
    model_index = 0

    while current_tier is not None:
        current_model = model if model else _get_model(current_tier, model_index)

        for attempt in range(MAX_RETRIES):
            try:
                payload = {
                    "model": current_model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }

                if json_mode:
                    payload["response_format"] = {"type": "json_object"}

                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                }
                if OPENROUTER_SITE_URL:
                    headers["HTTP-Referer"] = OPENROUTER_SITE_URL
                if OPENROUTER_APP_NAME:
                    headers["X-Title"] = OPENROUTER_APP_NAME

                resp = requests.post(
                    f"{OPENROUTER_BASE}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})

                    logger.info(
                        f"[{current_model}] "
                        f"in={usage.get('prompt_tokens', '?')} "
                        f"out={usage.get('completion_tokens', '?')} "
                        f"tokens"
                    )

                    return content

                # Rate limited — wait and retry
                if resp.status_code == 429:
                    delay = RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limited on {current_model}, waiting {delay}s...")
                    time.sleep(delay)
                    continue

                # Server error — retry
                if resp.status_code >= 500:
                    delay = RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Server error {resp.status_code} on {current_model}, retrying in {delay}s...")
                    time.sleep(delay)
                    continue

                # Client error — log and try fallback
                error_msg = resp.json().get("error", {}).get("message", resp.text[:200])
                logger.error(f"Error {resp.status_code} on {current_model}: {error_msg}")
                break  # Don't retry client errors, fall through to fallback

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on {current_model} (attempt {attempt + 1}/{MAX_RETRIES})")
                continue
            except requests.exceptions.ConnectionError:
                delay = RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Connection error, retrying in {delay}s...")
                time.sleep(delay)
                continue

        # Current model exhausted — try next in tier
        if not model:  # Only fallback if we're using tier routing
            model_index += 1
            if model_index < len(MODELS.get(current_tier, [])):
                logger.info(f"Falling back to next model in {current_tier} tier...")
                continue

            # Tier exhausted — escalate
            next_tier = ESCALATION.get(current_tier)
            if next_tier:
                logger.info(f"Escalating from {current_tier} to {next_tier} tier...")
                current_tier = next_tier
                model_index = 0
                continue

        # All options exhausted
        break

    raise RuntimeError(f"All models exhausted for tier '{tier}'. Check API key and OpenRouter status.")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def complete_cheap(prompt, system=None, **kwargs):
    """Cheap tier. For scraping, classification, extraction, bulk work."""
    return complete(prompt, system=system, tier="cheap", temperature=0.2, **kwargs)


def complete_mid(prompt, system=None, **kwargs):
    """Mid tier. For content writing, research synthesis, analysis."""
    return complete(prompt, system=system, tier="mid", temperature=0.4, **kwargs)


def complete_premium(prompt, system=None, max_tokens=8000, **kwargs):
    """Premium tier. For complex builds, proposals, strategic reasoning."""
    return complete(prompt, system=system, tier="premium", temperature=0.5, max_tokens=max_tokens, **kwargs)


def complete_json(prompt, system=None, tier="cheap", **kwargs):
    """Call any tier with JSON mode enabled. Returns parsed dict."""
    raw = complete(prompt, system=system, tier=tier, json_mode=True, **kwargs)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Some models wrap JSON in markdown code blocks
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        return json.loads(raw)


# ============================================================================
# COST TRACKING
# ============================================================================

def check_usage():
    """Check current OpenRouter usage. Returns dict with credits info."""
    if not OPENROUTER_API_KEY:
        return {"error": "No API key"}

    resp = requests.get(
        f"{OPENROUTER_BASE}/auth/key",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        timeout=10,
    )
    if resp.status_code == 200:
        return resp.json().get("data", {})
    return {"error": f"Status {resp.status_code}"}


# ============================================================================
# CLI for testing
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test OpenRouter API client")
    parser.add_argument("prompt", nargs="?", default="Say hello in one sentence.", help="Test prompt")
    parser.add_argument("--tier", default="cheap", choices=["cheap", "mid", "premium"])
    parser.add_argument("--model", default=None, help="Specific model override")
    parser.add_argument("--system", default=None, help="System prompt")
    parser.add_argument("--usage", action="store_true", help="Check API usage/credits")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.usage:
        info = check_usage()
        print(json.dumps(info, indent=2))
    else:
        result = complete(args.prompt, system=args.system, tier=args.tier, model=args.model)
        print(result)
