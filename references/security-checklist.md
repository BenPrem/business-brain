# Security Checklist

80/20 security: cover the low-hanging fruit that stops 90% of attacks. Don't overcomplicate it, but don't ignore it either.

---

## Principle: Everything Is Hackable — Just Make It Not Worth the Effort

The goal isn't perfect security. It's making the cost of attacking your system exceed the value of what's inside. A fence and a camera stop most burglars — that's what we're building here.

---

## The 5 Low-Hanging Fruit

### 1. API Keys Leak Through Conversation History

**The risk:** Every Claude Code conversation is stored as JSONL files in `~/.claude/`. If you paste API keys in plain text during a chat, they're now sitting in unencrypted logs on your machine. An attacker who gets file access can grep for key patterns (sk-*, sk_live_*, etc.) and exfiltrate them instantly.

**The fix:**
- ALWAYS store API keys in `.env` files — never paste them directly in conversation
- Reference keys by variable name: "I put the key in .env as ANTHROPIC_API_KEY" instead of pasting the actual key
- Add `.env`, `.env.local`, and any credential files to `.gitignore` BEFORE the first commit
- Periodically audit `~/.claude/` conversation logs for accidentally leaked keys

### 2. AI Models Hallucinate Package Names (Supply Chain Attack)

**The risk:** Models sometimes invent package names with small misspellings (e.g., "acorns" instead of "acorn"). Malicious actors register these misspelled packages on npm/pip with malware inside. When the agent runs `npm install` with the hallucinated name, you've just installed an attacker's code.

**The fix:**
- Before any `npm install` or `pip install`, ask the agent: "Audit the dependency list — are all packages legitimate, well-maintained, and spelled correctly?"
- Check package download counts and publish dates. A package with 12 downloads published yesterday is suspicious.
- For any new project, review `package.json` / `requirements.txt` manually before running install
- Use `npm audit` or equivalent after installation

### 3. Database Row-Level Security (RLS)

**The risk:** Supabase (and similar) does NOT enable RLS by default. Without it, any authenticated user can read, write, and delete every row in every table — not just their own data. Entire databases have been exfiltrated in seconds this way.

**The fix:**
- Enable RLS on EVERY table immediately after creation
- Create policies that restrict users to their own rows
- Test by trying to access another user's data — if you can, RLS isn't working
- This applies to any client project that uses a database

### 4. Public-Facing Servers Get Scanned Constantly

**The risk:** The moment you deploy anything to a public URL (VPS, static host with server functions, etc.), bot farms start scanning every open port looking for vulnerabilities. Thousands of requests per day, automated, 24/7.

**The fix:**
- Never store sensitive data (SSNs, passwords, credit cards) on any server you manage
- Use established platforms (managed static hosting, managed payments) that handle security for you
- Client demos deployed as static HTML have minimal attack surface — which is good
- If you ever spin up a VPS: firewall, SSH key auth only (no passwords), fail2ban, keep packages updated
- Never expose admin panels or API endpoints without authentication

### 5. Never Touch Credit Card Data

**The risk:** Storing credit card numbers anywhere in your system (files, database, conversation history) creates enormous liability — both legal (PCI compliance) and practical (breach consequences).

**The fix:**
- Use a managed payment processor (Stripe, Square, PayPal) for ALL payment processing — they handle PCI compliance
- Never ask clients to send credit card info via email, chat, or any channel you manage
- If building e-commerce for a client: always use an embedded checkout from a managed processor — never build a custom payment form

---

## Security Audit Prompt

Run this on any project before deploying publicly. **Always use a fresh conversation** (no context from the development session — the dev agent will be biased toward its own work):

```
I need you to perform a comprehensive security audit on this project. Check for:

1. SECRETS EXPOSURE
   - Search for hardcoded API keys, tokens, passwords (patterns: sk-*, sk_live_*, sk_test_*, bearer, password=, secret=)
   - Verify .gitignore includes: .env, .env.local, .env.production, credentials.json, *.pem, *.key
   - Check if any secrets appear in conversation logs or committed files
   - Sweep example/demo/seed content for real names, emails, IDs, and keys — "example" data is where leaks hide

2. DEPENDENCY AUDIT
   - Review all packages in package.json / requirements.txt
   - Flag any unfamiliar, low-download, or recently-published packages
   - Check for known vulnerabilities (npm audit / pip audit)

3. DATABASE SECURITY (if applicable)
   - Verify RLS is enabled on ALL tables
   - Check that API keys are not exposed in client-side code
   - Verify no admin/service role keys are used in frontend

4. INPUT VALIDATION
   - Check all user inputs for SQL injection, XSS, and path traversal
   - Verify file upload restrictions (type, size, sanitization)

5. AUTHENTICATION & AUTHORIZATION
   - Verify protected routes actually check auth
   - Check for privilege escalation (can a regular user access admin endpoints?)

6. DEPLOYMENT
   - Verify no debug modes or verbose error messages in production
   - Check CORS configuration
   - Verify HTTPS is enforced

Return a structured report with:
- Architecture summary
- Each finding with: severity (CRITICAL/HIGH/MEDIUM/LOW), description, fix
- Pass/Fail for each category
- Prioritized fix list
```

### Important: Use a Different Agent for the Audit

The agent that built the project is biased — it "thinks" its own code is secure. For the best results:
1. Run the security audit in a fresh conversation (no shared history)
2. Optionally, run a second audit through a different model/provider for diversification
3. Have the original dev agent implement the fixes
4. Run the audit again to verify

---

## House Rules

- Client website demos as static HTML on a managed host — low attack surface by default
- API keys live in `.env` only — reference by variable name everywhere else
- Never push `.env` to GitHub — verify `.gitignore` on every new repo
- Any client project with a database: RLS is mandatory, no exceptions
- Managed payment processor for anything touching money — never a custom payment form

---

## Related Files
- `.claude/rules/business-rules.md` — Security section
- `.claude/rules/learned-rules.md` — Security-related learned rules
- `references/advanced-agent-patterns.md` — Diversification strategy (security through non-monoculture)
