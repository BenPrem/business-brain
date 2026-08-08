# Workspace + Task-System Source-of-Truth Architecture

All active business data lives in two places:

1. **The workspace** (`clients/` + `ventures/` folders) — durable client, prospect, project, invoice, interaction, and operating-memory records.
2. **<TASK SYSTEM>** (Asana, Linear, Trello — whatever owns your live tasks) — execution layer for tasks, stages, due dates, follow-ups, and project handoffs.

The workspace is the long-term memory. <TASK SYSTEM> is the work queue.

## Core Records

1. **Companies** — one record per business. Website, industry, city, review rating, lead score, and current opportunity context.
2. **Contacts** — one record per person. Stage, priority, service interest, deal value, next follow-up date. Connects to Companies through links and naming.
3. **Activities** — one touchpoint per email, call, meeting, or deliverable. Always has a date, type, and 1-2 sentence summary.
4. **Pain Points** — one finding or opportunity per note/bullet. Category, severity, service match, source, and recommended next step.
5. **Invoices** — one row per invoice in the workspace ledger. Amount, status, dates, client/vendor, and file path.
6. **Tasks** — <TASK SYSTEM> tasks for due dates, project work, follow-ups, content items, and payment reminders.

## Relationship Model

```
CONTACTS <---------- COMPANIES
(people)    many:1   (businesses)
    |                     |
    | 1:many              | 1:many
    v                     v
ACTIVITIES           PAIN POINTS
(timeline)           (opportunities)

INVOICES             <TASK SYSTEM> TASKS
(billing)            (execution)
    |                     |
    +---- both link ------+
       to workspace records
```

## Rules for Reading Data

- To understand a lead: read the Contact record, Company record, recent Activities, Pain Points, and the <TASK SYSTEM> task.
- To prep for a call: read Company, Pain Points, Activities sorted by date, and any meeting task in <TASK SYSTEM>.
- To write a proposal: read Company, Pain Points, Contact, service interest, deal value, and current <TASK SYSTEM> stage.
- To check the pipeline: use <TASK SYSTEM> stages and confirm details in the workspace.
- To find follow-ups: use <TASK SYSTEM> due dates and workspace `Next Follow-Up` context.

## Rules for Writing Data

- Every outreach action creates a workspace Activity note or entry.
- Every website/social/business audit finding creates a workspace Pain Point note or entry.
- Stage changes happen in <TASK SYSTEM> and are mirrored in the workspace Contact record.
- Never bury interaction history in a generic notes field; use Activities so the timeline stays readable.

## Quick Reference

| Question | Source |
|----------|--------|
| "Who needs a follow-up today?" | <TASK SYSTEM> tasks due today |
| "What do I know about [company]?" | Workspace Company + Pain Points + recent Activities |
| "What's my pipeline look like?" | <TASK SYSTEM> grouped by stage |
| "Who owes me money?" | Workspace invoice ledger + <TASK SYSTEM> payment tasks |
| "What happened with [lead]?" | Workspace Activities sorted by date |
| "What should I pitch [prospect]?" | Workspace Pain Points sorted by severity |
| "What's my revenue this month?" | Workspace invoice ledger filtered by paid date |
| "What tasks are due this week?" | <TASK SYSTEM> tasks due this week |

## Migration Rule

When older instructions refer to a previous CRM or note system, interpret them as:

- Durable records, context, activities, pain points, invoices: **the workspace**
- Tasks, stages, follow-ups, execution dates: **<TASK SYSTEM>**
