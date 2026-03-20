"""
PagerDuty competitor definitions with source URLs for each intelligence category.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Competitor:
    name: str
    slug: str  # used for filtering / filenames
    website: str
    news_sources: List[str] = field(default_factory=list)     # press / news pages
    blog_urls: List[str] = field(default_factory=list)         # engineering / product blogs
    docs_urls: List[str] = field(default_factory=list)         # public docs / changelog pages
    api_changelog_urls: List[str] = field(default_factory=list) # API changelogs / release notes
    search_keywords: List[str] = field(default_factory=list)   # extra keywords for web search
    threat_notes: Optional[str] = None


COMPETITORS: List[Competitor] = [
    Competitor(
        name="Opsgenie (Atlassian)",
        slug="opsgenie",
        website="https://www.atlassian.com/software/opsgenie",
        news_sources=[
            "https://www.atlassian.com/company/news",
            "https://community.atlassian.com/t5/Opsgenie-articles/bg-p/opsgenie-articles",
        ],
        blog_urls=[
            "https://www.atlassian.com/blog/opsgenie",
            "https://www.atlassian.com/blog/software-teams/incident-management",
        ],
        docs_urls=[
            "https://support.atlassian.com/opsgenie/resources/",
            "https://docs.opsgenie.com/docs/release-notes",
        ],
        api_changelog_urls=[
            "https://docs.opsgenie.com/docs/release-notes",
        ],
        search_keywords=["Opsgenie update", "Opsgenie new feature", "Atlassian incident management"],
        threat_notes="Bundled with Atlassian suite; strong Jira integration.",
    ),
    Competitor(
        name="Splunk On-Call (VictorOps)",
        slug="splunk-oncall",
        website="https://www.splunk.com/en_us/products/on-call.html",
        news_sources=[
            "https://www.splunk.com/en_us/newsroom.html",
        ],
        blog_urls=[
            "https://www.splunk.com/en_us/blog/learn/victorops.html",
            "https://www.splunk.com/en_us/blog/category/product.html",
        ],
        docs_urls=[
            "https://help.victorops.com/knowledge-base/",
            "https://docs.splunk.com/Documentation/OnCall",
        ],
        api_changelog_urls=[
            "https://portal.victorops.com/api-info/#!/Incidents",
        ],
        search_keywords=["VictorOps update", "Splunk On-Call release", "Splunk incident response"],
        threat_notes="Backed by Cisco/Splunk; strong observability integration.",
    ),
    Competitor(
        name="Datadog Incident Management",
        slug="datadog",
        website="https://www.datadoghq.com/product/incident-management/",
        news_sources=[
            "https://www.datadoghq.com/about/newsroom/",
        ],
        blog_urls=[
            "https://www.datadoghq.com/blog/engineering/",
            "https://www.datadoghq.com/blog/",
        ],
        docs_urls=[
            "https://docs.datadoghq.com/service_management/incident_management/",
            "https://docs.datadoghq.com/release_notes/",
        ],
        api_changelog_urls=[
            "https://docs.datadoghq.com/api/latest/",
            "https://docs.datadoghq.com/release_notes/",
        ],
        search_keywords=["Datadog incident management update", "Datadog new feature", "Datadog API change"],
        threat_notes="Dominant in observability; bundling incident mgmt at scale.",
    ),
    Competitor(
        name="ServiceNow ITOM",
        slug="servicenow",
        website="https://www.servicenow.com/products/it-operations-management.html",
        news_sources=[
            "https://www.servicenow.com/company/newsroom.html",
        ],
        blog_urls=[
            "https://www.servicenow.com/blogs/",
        ],
        docs_urls=[
            "https://docs.servicenow.com/bundle/washingtondc-it-operations-management/",
            "https://www.servicenow.com/release-notes.html",
        ],
        api_changelog_urls=[
            "https://developer.servicenow.com/blog.do",
        ],
        search_keywords=["ServiceNow AIOps update", "ServiceNow ITOM release", "ServiceNow incident management"],
        threat_notes="Enterprise focus; strong ITSM moat.",
    ),
    Competitor(
        name="BigPanda",
        slug="bigpanda",
        website="https://www.bigpanda.io",
        news_sources=[
            "https://www.bigpanda.io/press/",
        ],
        blog_urls=[
            "https://www.bigpanda.io/blog/",
        ],
        docs_urls=[
            "https://docs.bigpanda.io/",
        ],
        api_changelog_urls=[
            "https://docs.bigpanda.io/reference/",
        ],
        search_keywords=["BigPanda update", "BigPanda AIOps", "BigPanda release notes"],
        threat_notes="AI-driven event correlation; targets NOC teams.",
    ),
    Competitor(
        name="xMatters (Everbridge)",
        slug="xmatters",
        website="https://www.xmatters.com",
        news_sources=[
            "https://www.xmatters.com/company/press-releases/",
            "https://www.everbridge.com/news/",
        ],
        blog_urls=[
            "https://www.xmatters.com/blog/",
        ],
        docs_urls=[
            "https://help.xmatters.com/",
        ],
        api_changelog_urls=[
            "https://help.xmatters.com/xmAPI/",
        ],
        search_keywords=["xMatters update", "xMatters new feature", "Everbridge xMatters"],
        threat_notes="Strong in critical event management; merged with Everbridge.",
    ),
    Competitor(
        name="Moogsoft",
        slug="moogsoft",
        website="https://www.moogsoft.com",
        news_sources=[
            "https://www.moogsoft.com/press-releases/",
        ],
        blog_urls=[
            "https://www.moogsoft.com/blog/",
        ],
        docs_urls=[
            "https://docs.moogsoft.com/",
        ],
        api_changelog_urls=[
            "https://docs.moogsoft.com/reference/",
        ],
        search_keywords=["Moogsoft AIOps update", "Moogsoft release", "Moogsoft new feature"],
        threat_notes="AIOps pioneer; being absorbed into Dell portfolio.",
    ),
    Competitor(
        name="Grafana OnCall",
        slug="grafana-oncall",
        website="https://grafana.com/products/oncall/",
        news_sources=[
            "https://grafana.com/blog/",
        ],
        blog_urls=[
            "https://grafana.com/blog/tags/oncall/",
        ],
        docs_urls=[
            "https://grafana.com/docs/oncall/latest/",
        ],
        api_changelog_urls=[
            "https://grafana.com/docs/oncall/latest/oncall-api-reference/",
            "https://github.com/grafana/oncall/releases",
        ],
        search_keywords=["Grafana OnCall update", "Grafana incident management", "Grafana OnCall release"],
        threat_notes="Open-source; rapidly growing; tight Grafana stack integration.",
    ),
    Competitor(
        name="Squadcast",
        slug="squadcast",
        website="https://www.squadcast.com",
        news_sources=[
            "https://www.squadcast.com/blog",
        ],
        blog_urls=[
            "https://www.squadcast.com/blog",
        ],
        docs_urls=[
            "https://support.squadcast.com/",
        ],
        api_changelog_urls=[
            "https://apidocs.squadcast.com/",
        ],
        search_keywords=["Squadcast update", "Squadcast new feature", "Squadcast release"],
        threat_notes="SMB-friendly pricing; growing in DevOps space.",
    ),
    Competitor(
        name="Rootly",
        slug="rootly",
        website="https://rootly.com",
        news_sources=[
            "https://rootly.com/blog",
        ],
        blog_urls=[
            "https://rootly.com/blog",
        ],
        docs_urls=[
            "https://docs.rootly.com/",
        ],
        api_changelog_urls=[
            "https://rootly.com/api",
            "https://docs.rootly.com/reference/api",
        ],
        search_keywords=["Rootly update", "Rootly incident management feature", "Rootly release"],
        threat_notes="Slack-native incident management; fast-growing startup.",
    ),
    Competitor(
        name="FireHydrant",
        slug="firehydrant",
        website="https://firehydrant.com",
        news_sources=[
            "https://firehydrant.com/blog/",
        ],
        blog_urls=[
            "https://firehydrant.com/blog/",
        ],
        docs_urls=[
            "https://docs.firehydrant.com/",
        ],
        api_changelog_urls=[
            "https://developers.firehydrant.io/",
        ],
        search_keywords=["FireHydrant update", "FireHydrant new feature", "FireHydrant release"],
        threat_notes="Strong retro / learning focus; developer-centric.",
    ),
    Competitor(
        name="Incident.io",
        slug="incident-io",
        website="https://incident.io",
        news_sources=[
            "https://incident.io/blog",
        ],
        blog_urls=[
            "https://incident.io/blog",
            "https://incident.io/changelog",
        ],
        docs_urls=[
            "https://docs.incident.io/",
        ],
        api_changelog_urls=[
            "https://api-docs.incident.io/",
            "https://incident.io/changelog",
        ],
        search_keywords=["incident.io update", "incident.io new feature", "incident.io changelog"],
        threat_notes="UK-based; strong narrative around learning from incidents.",
    ),
    Competitor(
        name="Zenduty",
        slug="zenduty",
        website="https://www.zenduty.com",
        news_sources=[
            "https://www.zenduty.com/blog/",
        ],
        blog_urls=[
            "https://www.zenduty.com/blog/",
        ],
        docs_urls=[
            "https://docs.zenduty.com/",
        ],
        api_changelog_urls=[
            "https://apidocs.zenduty.com/",
        ],
        search_keywords=["Zenduty update", "Zenduty new feature", "Zenduty release"],
        threat_notes="Cost-effective alternative; growing in Asia-Pacific.",
    ),
]

# Quick lookup by slug
COMPETITOR_MAP = {c.slug: c for c in COMPETITORS}
