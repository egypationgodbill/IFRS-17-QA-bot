# PagerDuty Competitor Daily Intelligence Report

Generate a comprehensive daily intelligence report on PagerDuty's competitors by researching their latest updates across news releases, blogs, documentation, and API changes.

## Instructions

Run the competitor analysis script to produce today's report:

```bash
cd /home/user/IFRS-17-QA-bot && python -m competitor_analysis.analyzer $ARGUMENTS
```

## What This Report Covers

For each major PagerDuty competitor the report surfaces:

1. **News & Press Releases** — funding rounds, acquisitions, partnerships, executive changes, product launches
2. **Blog Posts** — engineering blogs, product announcements, tutorials, and thought leadership
3. **Documentation Changes** — new features documented, deprecated APIs, new integrations, changed pricing pages
4. **API Changes** — new endpoints, breaking changes, new SDKs, webhook updates, changelog entries

## Competitors Tracked

- Opsgenie (Atlassian)
- VictorOps / Splunk On-Call
- Datadog Incident Management
- ServiceNow IT Operations Management
- BigPanda
- xMatters (Everbridge)
- Moogsoft
- Grafana OnCall / AlertManager
- Squadcast
- Rootly
- FireHydrant
- Incident.io
- Zenduty

## Usage

```
/competitor-report                    # Full report for today
/competitor-report --days 7           # Last 7 days of changes
/competitor-report --competitor rootly # Focus on one competitor
/competitor-report --category api     # Only API changes
/competitor-report --output markdown  # Save as markdown file
```

## Output Format

The report is structured as:

```
PAGERDUTY COMPETITOR INTELLIGENCE REPORT
Date: YYYY-MM-DD
Period: Last N days

EXECUTIVE SUMMARY
- 3-5 bullet highlights of most important changes

PER-COMPETITOR SECTIONS
  [Competitor Name]
  - News/Press: ...
  - Blog Updates: ...
  - Docs Changes: ...
  - API Changes: ...
  - Threat Level: LOW / MEDIUM / HIGH

STRATEGIC INSIGHTS
- Trends across competitors
- Areas where PagerDuty may need to respond
```
