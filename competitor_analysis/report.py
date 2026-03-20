"""
Report builder: turns structured competitor data into a formatted Markdown report.
"""

from datetime import date
from typing import List, Optional


THREAT_EMOJI = {
    "LOW": "🟢",
    "MEDIUM": "🟡",
    "HIGH": "🔴",
}

CATEGORY_HEADERS = {
    "news": "📰 News & Press Releases",
    "blog": "✍️  Blog Posts",
    "docs": "📚 Documentation Changes",
    "api": "⚙️  API Changes",
}


def _finding_to_md(finding: dict, indent: int = 0) -> str:
    prefix = " " * indent
    lines = []
    title = finding.get("title", "Update")
    summary = finding.get("summary", "")
    impact = finding.get("impact", "")
    source_url = finding.get("source_url")
    pub_date = finding.get("date", "")

    date_str = f" *({pub_date})*" if pub_date else ""
    if source_url:
        lines.append(f"{prefix}- **[{title}]({source_url})**{date_str}")
    else:
        lines.append(f"{prefix}- **{title}**{date_str}")

    if summary:
        lines.append(f"{prefix}  {summary}")
    if impact:
        lines.append(f"{prefix}  > *PagerDuty impact: {impact}*")

    return "\n".join(lines)


def build_report(
    competitor_results: List[dict],
    executive_summary: str,
    strategic_insights: str,
    since_date: date,
    today: date,
    days: int,
    categories: List[str],
) -> str:
    """Build the full Markdown report string."""
    lines = []

    # -----------------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------------
    lines.append("# PagerDuty Competitor Intelligence Report")
    lines.append("")
    lines.append(f"**Date:** {today.strftime('%A, %B %d, %Y')}")
    period_label = "Today" if days == 1 else f"Last {days} days"
    lines.append(f"**Period:** {period_label} ({since_date} → {today})")
    lines.append(f"**Categories:** {', '.join(c.upper() for c in categories)}")
    lines.append(f"**Competitors tracked:** {len(competitor_results)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # -----------------------------------------------------------------------
    # Executive Summary
    # -----------------------------------------------------------------------
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(executive_summary)
    lines.append("")
    lines.append("---")
    lines.append("")

    # -----------------------------------------------------------------------
    # Threat dashboard
    # -----------------------------------------------------------------------
    lines.append("## Threat Dashboard")
    lines.append("")
    lines.append("| Competitor | Threat Level | Key Update |")
    lines.append("|------------|:------------:|------------|")
    for cr in competitor_results:
        name = cr["competitor_name"]
        level = cr.get("threat_level", "LOW")
        emoji = THREAT_EMOJI.get(level, "")
        # Pick first finding as key update
        key_update = "No significant updates"
        for cat_result in cr["categories"]:
            if cat_result["findings"]:
                key_update = cat_result["findings"][0].get("title", "See details below")
                break
        lines.append(f"| {name} | {emoji} {level} | {key_update} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # -----------------------------------------------------------------------
    # Per-competitor sections
    # -----------------------------------------------------------------------
    lines.append("## Competitor Details")
    lines.append("")

    for cr in competitor_results:
        name = cr["competitor_name"]
        level = cr.get("threat_level", "LOW")
        emoji = THREAT_EMOJI.get(level, "")
        threat_notes = cr.get("threat_notes", "")

        lines.append(f"### {name} &nbsp; {emoji} {level}")
        if threat_notes:
            lines.append(f"*{threat_notes}*")
        lines.append("")

        has_any_findings = any(cat["findings"] for cat in cr["categories"])

        if not has_any_findings:
            lines.append("No significant updates found in this period.")
            lines.append("")
            continue

        for cat_result in cr["categories"]:
            cat = cat_result["category"]
            findings = cat_result["findings"]
            header = CATEGORY_HEADERS.get(cat, cat.upper())

            lines.append(f"#### {header}")
            lines.append("")

            if not findings:
                lines.append("*No updates found.*")
            else:
                for finding in findings:
                    lines.append(_finding_to_md(finding))
                    lines.append("")

        lines.append("---")
        lines.append("")

    # -----------------------------------------------------------------------
    # Strategic Insights
    # -----------------------------------------------------------------------
    lines.append("## Strategic Insights & Trends")
    lines.append("")
    lines.append(strategic_insights)
    lines.append("")
    lines.append("---")
    lines.append("")

    # -----------------------------------------------------------------------
    # Footer
    # -----------------------------------------------------------------------
    lines.append("## Report Metadata")
    lines.append("")
    lines.append(f"- Generated: {today.isoformat()}")
    lines.append(f"- Research window: {since_date.isoformat()} to {today.isoformat()}")
    lines.append("- Data sources: Web search (news sites, official blogs, docs, GitHub)")
    lines.append("- Analysis: Anthropic Claude (claude-opus-4-6)")
    lines.append("")
    lines.append("> *This report is AI-generated from publicly available sources.*")
    lines.append("> *Always verify critical findings before acting on them.*")

    return "\n".join(lines)
