# Phase 3: Website Audit

**Status: Handled by tools**

Phase 3 website audit is executed by `tools/website_auditor.py`.

## Process
The website_auditor.py script analyzes the prospect's website against a 15-point digital marketing checklist:

- Mobile responsiveness
- Page load speed
- SEO basics (title tags, meta descriptions, headers)
- Call-to-action visibility and clarity
- Trust signals (testimonials, credentials, reviews)
- Content clarity (does it match customer language?)
- Navigation structure
- Contact information accessibility
- Service descriptions specificity
- Visual design quality
- Brand consistency
- Social proof integration
- Forms and lead capture
- Analytics/tracking setup
- Accessibility (alt text, contrast)

## Output
Generates `website-audit.md` containing:
- Overall audit score (out of 100)
- Category breakdown with scores
- Top 5 gaps (what's hurting their online visibility most)
- Quick-win fixes (improvements with high impact/low effort)
- Long-term improvements
- Competitive positioning (how they rank vs. typical competitors in their niche)

## For Integration
The orchestrator passes:
- Input: {business_name}, {scraped_content}
- Output file: website-audit.md

Do not modify or replace this phase — refer to tools/website_auditor.py for implementation details.
