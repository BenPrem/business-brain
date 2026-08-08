# Phase 2: Competitor Analysis

**Status: Handled by tools**

Phase 2 competitor analysis is executed by `tools/competitor_analyzer.py`.

## Process
The competitor_analyzer.py script:
1. Identifies 3-5 direct competitors in the same niche and geography
2. Analyzes each competitor's website for design quality, messaging, services, pricing visibility, and call-to-action effectiveness
3. Builds a comparison matrix (prospect vs. each competitor)
4. Identifies 3-5 specific gaps where the prospect is losing market share

## Output
Generates `competitor-analysis.md` containing:
- Competitor overview (name, niche positioning, estimated revenue tier if visible)
- Design/UX quality score
- Messaging effectiveness
- Service breadth
- Online presence strength (reviews, social media activity)
- CTA strategy
- Gap analysis (where the prospect is weaker)

## For Integration
The orchestrator passes:
- Input: {business_name}, {niche}, {location}, {scraped_content}
- Output file: competitor-analysis.md

Do not modify or replace this phase — refer to tools/competitor_analyzer.py for implementation details.
