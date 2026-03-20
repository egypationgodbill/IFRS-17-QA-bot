"""
PagerDuty Competitor Intelligence Analyzer

Uses the Anthropic API with built-in web search to research competitor updates
across news, blogs, docs, and API changes, then produces a structured daily report.

Usage:
    python -m competitor_analysis.analyzer
    python -m competitor_analysis.analyzer --days 7
    python -m competitor_analysis.analyzer --competitor rootly
    python -m competitor_analysis.analyzer --category api
    python -m competitor_analysis.analyzer --output report.md
"""

import anthropic
import argparse
import json
import os
import sys
from datetime import date, timedelta
from typing import Optional

from .competitors import COMPETITORS, COMPETITOR_MAP, Competitor
from .report import build_report


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CATEGORIES = ["news", "blog", "docs", "api"]

CATEGORY_DESCRIPTIONS = {
    "news": "press releases, funding announcements, acquisitions, partnerships, executive changes",
    "blog": "engineering blog posts, product announcements, tutorials, thought leadership articles",
    "docs": "documentation updates, new feature guides, deprecated features, changed pricing pages, new integrations",
    "api": "API changelog entries, new endpoints, breaking changes, new SDKs, webhook updates, rate limit changes",
}

THREAT_PROMPT = (
    "Based solely on the updates found, rate the competitive threat level as one of: "
    "LOW (minor updates, no significant new capabilities), "
    "MEDIUM (notable improvements, potential impact on PagerDuty deals), "
    "HIGH (major new capability or pricing change that directly threatens PagerDuty's position). "
    "Return ONLY the word LOW, MEDIUM, or HIGH."
)


# ---------------------------------------------------------------------------
# Core research functions
# ---------------------------------------------------------------------------

def research_competitor_category(
    client: anthropic.Anthropic,
    competitor: Competitor,
    category: str,
    since_date: date,
    model: str = "claude-opus-4-6",
) -> dict:
    """
    Use Claude with web search to find recent updates for one competitor in one category.
    Returns a dict with keys: category, findings (list of strings), raw_text.
    """
    since_str = since_date.strftime("%B %d, %Y")
    today_str = date.today().strftime("%B %d, %Y")

    category_desc = CATEGORY_DESCRIPTIONS[category]

    # Build source hints
    source_hints = []
    if category == "news":
        source_hints = competitor.news_sources
    elif category == "blog":
        source_hints = competitor.blog_urls
    elif category == "docs":
        source_hints = competitor.docs_urls
    elif category == "api":
        source_hints = competitor.api_changelog_urls

    source_hint_text = ""
    if source_hints:
        source_hint_text = (
            f"\n\nPriority sources to check:\n" + "\n".join(f"- {u}" for u in source_hints)
        )

    keyword_text = ""
    if competitor.search_keywords:
        keyword_text = (
            "\n\nAdditional search terms: " + ", ".join(competitor.search_keywords)
        )

    prompt = f"""You are a competitive intelligence analyst tracking PagerDuty's competitors.

Research **{competitor.name}** for recent **{category_desc}** published between {since_str} and {today_str}.

Your goal:
1. Search the web for the most relevant recent updates in this category.
2. Return a concise, factual bullet-point list of findings.
3. For each finding include: what changed, when (approximate date if available), and why it matters to PagerDuty.
4. If nothing significant was found in this period, say "No significant updates found."
{source_hint_text}{keyword_text}

Format your response as a JSON object with this structure:
{{
  "findings": [
    {{
      "title": "Brief title of the update",
      "date": "YYYY-MM-DD or approximate month",
      "summary": "1-2 sentence description",
      "source_url": "URL if available or null",
      "impact": "Why this matters to PagerDuty"
    }}
  ],
  "no_updates": false
}}

If there are no updates, return: {{"findings": [], "no_updates": true}}
Return ONLY valid JSON, no markdown fences."""

    response = client.messages.create(
        model=model,
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract text content from response
    raw_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            raw_text += block.text

    # Parse JSON
    try:
        data = json.loads(raw_text.strip())
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from inside the text
        import re
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
            except json.JSONDecodeError:
                data = {"findings": [], "no_updates": True, "parse_error": raw_text[:200]}
        else:
            data = {"findings": [], "no_updates": True, "parse_error": raw_text[:200]}

    return {
        "category": category,
        "findings": data.get("findings", []),
        "no_updates": data.get("no_updates", False),
        "raw_text": raw_text,
    }


def assess_threat_level(
    client: anthropic.Anthropic,
    competitor: Competitor,
    all_findings: list,
    model: str = "claude-opus-4-6",
) -> str:
    """Ask Claude to assess the threat level based on all findings for a competitor."""
    if not any(r["findings"] for r in all_findings):
        return "LOW"

    findings_summary = []
    for result in all_findings:
        if result["findings"]:
            findings_summary.append(f"[{result['category'].upper()}]")
            for f in result["findings"]:
                findings_summary.append(f"  - {f.get('title', '')}: {f.get('summary', '')}")

    prompt = (
        f"Competitor: {competitor.name}\n\n"
        "Recent updates:\n"
        + "\n".join(findings_summary)
        + "\n\n"
        + THREAT_PROMPT
    )

    response = client.messages.create(
        model=model,
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}],
    )

    level = ""
    for block in response.content:
        if hasattr(block, "text"):
            level += block.text.strip().upper()

    if level not in ("LOW", "MEDIUM", "HIGH"):
        level = "LOW"
    return level


def generate_executive_summary(
    client: anthropic.Anthropic,
    competitor_results: list,
    since_date: date,
    model: str = "claude-opus-4-6",
) -> str:
    """Generate a 3-5 bullet executive summary across all competitors."""
    # Build a condensed overview
    overview_lines = []
    for cr in competitor_results:
        threat = cr.get("threat_level", "LOW")
        if threat in ("MEDIUM", "HIGH"):
            overview_lines.append(f"[{threat}] {cr['competitor_name']}:")
            for cat_result in cr["categories"]:
                for finding in cat_result["findings"][:2]:
                    overview_lines.append(f"  [{cat_result['category']}] {finding.get('title', '')}: {finding.get('summary', '')}")

    if not overview_lines:
        # Include all if nothing is medium/high
        for cr in competitor_results[:5]:
            overview_lines.append(f"{cr['competitor_name']}:")
            for cat_result in cr["categories"]:
                for finding in cat_result["findings"][:1]:
                    overview_lines.append(f"  [{cat_result['category']}] {finding.get('title', '')}")

    prompt = f"""You are a VP of Product at PagerDuty reviewing a competitive intelligence report.

Based on these competitor updates from the past period (since {since_date.strftime('%B %d, %Y')}):

{chr(10).join(overview_lines) if overview_lines else 'No significant updates found across competitors.'}

Write a concise executive summary of 3-5 bullet points highlighting:
- The most important competitive developments
- Any emerging trends across multiple competitors
- Key areas where PagerDuty should consider responding

Keep each bullet to 1-2 sentences. Be direct and action-oriented.
Return plain text bullets starting with "• "."""

    response = client.messages.create(
        model=model,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )

    summary = ""
    for block in response.content:
        if hasattr(block, "text"):
            summary += block.text
    return summary.strip()


def generate_strategic_insights(
    client: anthropic.Anthropic,
    competitor_results: list,
    model: str = "claude-opus-4-6",
) -> str:
    """Generate cross-competitor strategic insights and trends."""
    all_findings = []
    for cr in competitor_results:
        for cat_result in cr["categories"]:
            for finding in cat_result["findings"]:
                all_findings.append(
                    f"[{cr['competitor_name']} / {cat_result['category']}] "
                    f"{finding.get('title', '')}: {finding.get('summary', '')}"
                )

    if not all_findings:
        return "No significant cross-competitor trends identified in this period."

    prompt = f"""You are a competitive strategy analyst at PagerDuty.

Review these competitor updates and identify strategic patterns:

{chr(10).join(all_findings[:40])}

Provide 3-5 strategic insights covering:
1. Common themes or trends across multiple competitors
2. Technology directions the industry is moving toward
3. Market segments being targeted
4. Potential threats to PagerDuty's core business
5. Opportunities PagerDuty could exploit

Return as numbered points. Be specific and actionable. Keep it concise."""

    response = client.messages.create(
        model=model,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    insights = ""
    for block in response.content:
        if hasattr(block, "text"):
            insights += block.text
    return insights.strip()


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run_analysis(
    days: int = 1,
    competitor_slug: Optional[str] = None,
    categories: Optional[list] = None,
    output_file: Optional[str] = None,
    model: str = "claude-opus-4-6",
    verbose: bool = False,
) -> str:
    """
    Main entry point. Returns the full report as a string.
    Also writes to output_file if provided.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.Anthropic(api_key=api_key)

    since_date = date.today() - timedelta(days=days)
    active_categories = categories or CATEGORIES

    # Filter competitors
    if competitor_slug:
        if competitor_slug not in COMPETITOR_MAP:
            sys.exit(f"Unknown competitor slug: {competitor_slug}. "
                     f"Valid options: {', '.join(COMPETITOR_MAP.keys())}")
        active_competitors = [COMPETITOR_MAP[competitor_slug]]
    else:
        active_competitors = COMPETITORS

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"PagerDuty Competitor Intelligence Analysis", file=sys.stderr)
    print(f"Period: {since_date} → {date.today()} ({days} day(s))", file=sys.stderr)
    print(f"Competitors: {len(active_competitors)} | Categories: {active_categories}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)

    competitor_results = []

    for competitor in active_competitors:
        if verbose:
            print(f"Researching: {competitor.name}", file=sys.stderr)

        category_results = []
        for cat in active_categories:
            if verbose:
                print(f"  [{cat}] searching...", file=sys.stderr)
            result = research_competitor_category(client, competitor, cat, since_date, model)
            category_results.append(result)
            count = len(result["findings"])
            if verbose:
                print(f"  [{cat}] → {count} finding(s)", file=sys.stderr)

        # Assess threat level
        threat_level = assess_threat_level(client, competitor, category_results, model)
        if verbose:
            print(f"  Threat level: {threat_level}\n", file=sys.stderr)

        competitor_results.append({
            "competitor_name": competitor.name,
            "competitor_slug": competitor.slug,
            "threat_level": threat_level,
            "threat_notes": competitor.threat_notes,
            "categories": category_results,
        })

    # Executive summary
    print("Generating executive summary...", file=sys.stderr)
    executive_summary = generate_executive_summary(client, competitor_results, since_date, model)

    # Strategic insights
    print("Generating strategic insights...", file=sys.stderr)
    strategic_insights = generate_strategic_insights(client, competitor_results, model)

    # Build final report
    report_text = build_report(
        competitor_results=competitor_results,
        executive_summary=executive_summary,
        strategic_insights=strategic_insights,
        since_date=since_date,
        today=date.today(),
        days=days,
        categories=active_categories,
    )

    if output_file:
        with open(output_file, "w", encoding="utf-8") as fh:
            fh.write(report_text)
        print(f"\nReport written to: {output_file}", file=sys.stderr)

    return report_text


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a PagerDuty competitor intelligence report."
    )
    parser.add_argument(
        "--days", type=int, default=1,
        help="Number of days to look back (default: 1 = today only)",
    )
    parser.add_argument(
        "--competitor", type=str, default=None,
        help="Focus on a single competitor by slug (e.g. rootly, opsgenie)",
    )
    parser.add_argument(
        "--category", type=str, default=None,
        choices=CATEGORIES,
        help="Only report on one category: news, blog, docs, api",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Write report to this file path (e.g. report.md)",
    )
    parser.add_argument(
        "--model", type=str, default="claude-opus-4-6",
        help="Anthropic model to use (default: claude-opus-4-6)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print progress details to stderr",
    )
    parser.add_argument(
        "--list-competitors", action="store_true",
        help="List available competitor slugs and exit",
    )

    args = parser.parse_args()

    if args.list_competitors:
        print("Available competitor slugs:")
        for c in COMPETITORS:
            print(f"  {c.slug:20s}  {c.name}")
        sys.exit(0)

    categories = [args.category] if args.category else None

    report = run_analysis(
        days=args.days,
        competitor_slug=args.competitor,
        categories=categories,
        output_file=args.output,
        model=args.model,
        verbose=args.verbose,
    )

    print(report)


if __name__ == "__main__":
    main()
