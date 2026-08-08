---
name: invoice-tracker
description: Track invoices, payments, and outstanding balances across clients; also extracts date/amount/vendor/category from uploaded invoice files. Triggers on "who owes me", "invoice <CLIENT>", "payment status", "revenue report", "what's outstanding". Ledger lives at finances/invoices.md; payment follow-ups live in <TASK SYSTEM>. NOT an accounting tool — a visibility tool so nothing falls through the cracks.
---

# Invoice & Payment Tracker

Know exactly who owes what, what's been paid, and what's overdue — at a glance.

## When to use
- The operator creates or sends an invoice
- A payment comes in
- "Who owes me money" / "what's my revenue this month"
- End-of-month reconciliation or the weekly review

## Ledger

The durable ledger is a file; <TASK SYSTEM> is the follow-up layer.

- `finances/invoices.md` — the master invoice table (create it on first use)
- `clients/<slug>/deliverables/invoices/` — the invoice documents themselves; the ledger records actual file paths

Ledger columns: Invoice # · Client/Vendor · Amount · Type (One-Time, Retainer, Deposit, Final Payment, Expense) · Status (Draft, Sent, Paid, Overdue, Void, Received) · Date Sent · Date Due · Date Paid · Notes · File path.

Numbering: `<PREFIX>-<YEAR>-<sequential>` (pick a prefix from your business name once and keep it). Next number = highest in the ledger + 1; never re-issue a number.

---

## Creating an Invoice Record

When the operator says "invoice <CLIENT> for [amount]":

### Step 1 — Gather details
- **Client name** (must exist in the client records, or be confirmed by the operator)
- **Amount** — always supplied by the operator; NEVER invent, estimate, or auto-fill an amount
- **Type**: One-Time (project), Retainer (monthly), Deposit (upfront), Final Payment (on delivery)
- **Description**: what it's for ("Phase 1: Website Build", "March Retainer")
- **Due date**: default 14 days from today unless specified

### Step 2 — Create the record
- Add the row to `finances/invoices.md`
- Create/update a payment follow-up task in <TASK SYSTEM> with the due date
- Link the invoice document path in the task notes

### Step 3 — Generate the invoice document (optional)

If the operator wants a formal invoice to send:

```
INVOICE
Invoice #: <PREFIX>-<YYYY>-<###>
Date: [Today]        Due: [Due Date]

From:  <YOUR BUSINESS> · <YOUR NAME> · <CITY, STATE> · <EMAIL>
To:    <CLIENT> · [Contact] · [Client email]

Description                          Amount
--------------------------------------------
[Service description]                $[Amount]
                              Total: $[Amount]

Payment: [methods you accept — bank transfer, card link, etc.]

Thank you for your business.
```

Save to `clients/<slug>/deliverables/invoices/<PREFIX>-<YYYY>-<###>.html` (`mkdir -p` if missing).

---

## Recording a Payment

"<CLIENT> paid" / "got payment from [name]":
- Update the ledger row to `Paid` + add the date paid
- Mark the related follow-up task complete

## Checking Outstanding Balances

"Who owes me" / "what's outstanding": read `finances/invoices.md`, filter `Sent` and `Overdue`, cross-check open payment follow-up tasks. Present:

```
Outstanding Invoices — [Date]
==============================
OVERDUE:
  • <CLIENT> — $[Amount] — due [Date] ([X] days late)
SENT (not yet due):
  • <CLIENT> — $[Amount] — due [Date] ([X] days remaining)

TOTAL OUTSTANDING: $[Sum]    TOTAL OVERDUE: $[Sum]
```

---

## Payment Reminders

At 3+ days overdue, draft a gentle reminder for the operator to send (never send without approval):

**First reminder (3 days):**
```
Subject: Quick reminder — Invoice <PREFIX>-<###>

Hi [Name],

Just a quick note — invoice <PREFIX>-<###> for $[amount] was due on [date].
Totally possible it slipped through the cracks. Here are the payment
details again:

[Payment method]

Let me know if you have any questions.

<YOUR NAME>
<YOUR BUSINESS>
```

**Second reminder (10 days):** same shape, firmer — "Following up on invoice <PREFIX>-<###>, originally due [date]. Want to make sure everything's okay on your end. If there's an issue with the invoice or timing, just let me know and we'll figure it out."

**Third reminder (21+ days):** flag for the operator's personal attention — draft a firmer but still professional message. At this point the operator should call, not just email.

---

## Monthly Revenue Report

On "revenue report" or during the weekly/monthly review:

```markdown
# Revenue Report — [Month Year]

## Collected This Month
| Client | Invoice # | Amount | Date Paid |
**Total Collected: $[Sum]**

## Recurring Revenue (Active Retainers)
| Client | Monthly Amount | Status |
**MRR: $[Sum]**

## Outstanding
| Client | Amount | Due Date | Status |
**Total Outstanding: $[Sum]**

## Year-to-Date
- Total collected (YTD) · average monthly revenue · MRR trend [last month] → [this month]

## Current north-star tracker
- Cross-check the top-priority client's payment milestones against context/current-priorities.md before reporting
```

Save to `ventures/<your-business-slug>/deliverables/revenue-reports/[YYYY-MM]-revenue.md` (`mkdir -p` if missing).

---

## Processing Uploaded Invoice Files

When the operator shares an invoice PDF/image and says "organize this", "extract this invoice", or "log this expense", extract:

- **Vendor/From** · **Date** · **Due Date** (if present) · **Amount** (look for "Total", "Amount Due", "Balance Due") · **Invoice #** (if present) · **Description** · **Category** (Software/Tools, Advertising, Contractor, Equipment, Other)

Present the extraction, then ask: "Add to the ledger and create a follow-up task? (y/n)". On confirm, write the ledger row (Status `Received` for expenses) and create/update the task.

---

## Hard rules
- This is a visibility tool, not an accounting system — the operator still needs an accountant for taxes.
- Never invent an amount, payment status, or date. Rows backfilled from disk without confirmed status carry `TODO: confirm with operator` — resolve by asking, never by guessing.
- All reminder drafts need the operator's approval before sending.
- When a payment processor (e.g. Stripe) is connected, tracking can partially automate — a webhook updates the ledger and/or task on payment. (You build this — the skill works manually without it.)
