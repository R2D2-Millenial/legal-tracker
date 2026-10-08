import feedparser
from datetime import datetime, timedelta

FEEDS = {
    "Corporate & Tech": "https://www.livelaw.in/rss/corporate-laws",
    "Judicial Precedents": "https://www.barandbench.com/feed",
    "PIB Corporate Affairs": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1",
    "PIB Finance": "https://pib.gov.in/RssMain.aspx?ModId=2&Lang=1",
    # Add RSS feeds of tier-1 law firm advisory pages
}

def fetch_weekly_feed_entries():
    one_week_ago = datetime.now() - timedelta(days=7)
    collected = []

    for category, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Parse published date if present, otherwise default to recent
            collected.append({
                "source_category": category,
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", "")
            })
    return collected[:35]  # Ingest top 35 candidates for weekly synthesis
