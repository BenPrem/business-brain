---
name: access-transfer-tracker
description: Per-client access/asset transfer matrix for agency handoffs — asset, owner, transfer method, status — with verified-only-after-a-real-login discipline, a chase list with drafted nudges, and <TASK SYSTEM> sync. Triggers - "access matrix", "what access are we missing", "transfer status", "account handoff", taking over a client from another agency. NOT for agent tool connections — use mcp-integration.
---

# Access Transfer Tracker

Tracks every access and asset handoff when you take over a client from another agency (or
from the client's own scattered accounts). One living matrix per client; nothing counts
as "have it" until proven by a real authenticated action.

## The matrix file

Location: `clients/<slug>/access/access-matrix.md` (`mkdir -p` the `access/` dir on first
run). Frontmatter: `type: access_matrix`, `client: <slug>`, `updated: YYYY-MM-DD`. If the
engagement started with a client access-intake note, keep that note as a dated record —
never rewrite it; the living matrix supersedes it.

Standard asset rows (add/remove per client; for multi-business clients, one status column
per business line):

| Asset | What "admin-level" means here |
|---|---|
| Domain registrar | Account access or a transfer-out auth code |
| DNS zone control | Can view/export AND edit records (often differs from registrar) |
| Hosting / CMS | Administrator role, not Editor |
| Google Business Profile | Manager/Owner invite to your Google account |
| Social ads (Meta or equivalent) | Page + ad account + pixel shared to YOUR business manager as a partner |
| Search ads / LSA | Admin invite or manager-account link |
| Analytics / tag manager | Administrator on the property/container |
| Search Console | Delegated Owner (not just Full user) |
| Email / workspace admin | Admin-console access or a documented sending setup |
| Review platforms | Business-profile access covered above; other platform logins listed separately |
| Social account logins | Note the 2FA plan — 2FA tied to a client's personal phone is a standing friction to record |
| <CRM> / call tracking | CRM admin login + ownership of any tracking numbers |

Fields per row: **current owner** (client / losing agency / unknown) · **access level
needed** · **transfer method** (invite to your account, credential handover, registrar
transfer, partner share) · **status**: `not-requested → requested → received → verified`
· **verified date + how**.

**Credentials never go in the matrix or any workspace markdown.** Secrets live in a
gitignored env/credentials file — verify that file actually exists before directing
anyone to it. The matrix stores only *who has access*, never the secrets themselves.

## Verification discipline — `received` is not done

Status reaches `verified` ONLY after a real authenticated action, recorded with date + method:

- **Hosting/CMS:** log in as the granted admin, or make an authenticated API call that
  returns real site data
- **Registrar/DNS:** view or export the zone from inside the account; prove edit rights
  by reading a record you *could* change — don't change it (see the hard gate below)
- **Business profile:** the location appears in YOUR profile manager with the granted role
- **Social ads:** the page/ad account/pixel shows under YOUR business manager with the
  expected role
- **Analytics/Search Console:** a UI or API read returns the client's real property data
- **Workspace:** the admin console loads under your access

Credential handovers: before testing, grep any saved config for placeholder strings
(`PASTE_`, `YOUR_`, `xxx`) — placeholders get pasted literally and then reported as "received."

**Hard gate:** never change a single setting on an asset still under the losing agency's
control until ownership is verified — verification is read-only. DNS changes, business-
profile edits, and live-site publishes each need the founder's or the client's explicit
yes regardless of access status.

## Outputs each run

1. **Updated matrix** — bump `updated`; adjust statuses only with evidence (a forwarded
   invite = `received`; your own successful login = `verified`).
2. **Chase list** — a section at the bottom of the matrix: every non-`verified` row → who
   to nudge (client vs. losing agency vs. platform support), exactly what to ask for, and
   which deliverable it blocks. Consolidate: ONE bundled request per recipient beats a
   drip of asks. Draft the actual nudge lines to
   `clients/<slug>/_drafts/YYYY-MM-DD/access-nudges.md` for the founder's review — never
   send directly. Voice: client = plain and direct, no agency-speak; losing agency =
   professional "we", factual, zero blame. Never state platform facts you haven't verified.
3. **<TASK SYSTEM> sync** — one task per outstanding transfer (created at `requested`), a
   comment on every status change, completed only at `verified`. Confirm each API call
   returned a real payload before claiming the sync happened — never report task-system
   writes on exit code alone.

## New-client takeover

`mkdir -p clients/<slug>/access/`, copy the standard rows, all statuses `not-requested`.
The first deliverable is the consolidated request: one email to the client (what they
own), one to the losing agency (what they hold). Route the drafting through
email-composer — this skill produces the *content requirements*, not the relationship email.

## Write-back (every run that changes anything)

- Log an activity note on the client's workspace record (append-only — never modify
  existing activity records)
- Mirror status changes into the <TASK SYSTEM> tasks the same session
