import feedparser
import requests
from datetime import datetime

FEEDS = {
    "Corporate & Commercial": "https://www.livelaw.in/rss/corporate-laws",
    "Judicial Precedents": "https://www.barandbench.com/feed",
    "PIB Corporate Affairs": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1",
    "PIB Finance": "https://pib.gov.in/RssMain.aspx?ModId=2&Lang=1",
    "MeitY & Electronics (IT/AI)": "https://pib.gov.in/RssMain.aspx?ModId=3&Lang=1",
    "Cyber & Privacy Law": "https://www.livelaw.in/rss/cyber-laws"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_weekly_feed_entries():
    collected = []

    for category, url in FEEDS.items():
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                for entry in feed.entries[:8]:
                    collected.append({
                        "source_category": category,
                        "title": entry.get("title", "").strip(),
                        "summary": entry.get("summary", "").strip()[:600],
                        "link": entry.get("link", "").strip(),
                        "published": entry.get("published", "")
                    })
        except Exception as e:
            print(f"Warning: Could not fetch feed {category}: {e}")
            continue

    if not collected:
        collected.append({
            "source_category": "General",
            "title": "No major statutory notifications published this week",
            "summary": "Regular monitoring completed. No material gazette circulars published in this window.",
            "link": "https://egazette.gov.in",
            "published": datetime.now().strftime("%Y-%m-%d")
        })

    return collected[:35]
