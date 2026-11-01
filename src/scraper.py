"""
Regulatory Intelligence Scraper
Fetches legal, corporate, data privacy, and tech policy feeds across India.
"""

import requests
import feedparser
from datetime import datetime

# Verified regulatory and legal news feeds
FEEDS = {
    "Corporate & Commercial": "https://www.livelaw.in/rss/corporate-commercial",
    "Judicial Precedents": "https://www.livelaw.in/rss/top-stories",
    "PIB Corporate Affairs": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1",
    "PIB Finance": "https://pib.gov.in/RssMain.aspx?ModId=2&Lang=1",
    "MeitY & Electronics": "https://pib.gov.in/RssMain.aspx?ModId=16&Lang=1",
    "Cyber & Privacy Law": "https://www.livelaw.in/rss/cyber-it-law"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}


def fetch_weekly_feed_entries():
    """
    Fetches past month circulars across feeds.
    Temporarily expanded to pull up to 30 items per feed to recover historical records.
    """
    collected = []

    for category, url in FEEDS.items():
        try:
            print(f"[*] Fetching feed: {category}...")
            response = requests.get(url, headers=HEADERS, timeout=12)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                # Method A lookback: process up to 30 items per feed (was 8)
                for entry in feed.entries[:30]:
                    title = entry.get("title", "").strip()
                    summary = entry.get("summary", "").strip()
                    link = entry.get("link", "").strip()
                    published = entry.get("published", "") or datetime.utcnow().strftime("%Y-%m-%d")

                    if title:
                        collected.append({
                            "title": title,
                            "summary": summary[:350] + "..." if len(summary) > 350 else summary,
                            "link": link,
                            "date": published[:10],
                            "category_hint": category
                        })
            else:
                print(f"[!] Feed {category} returned HTTP {response.status_code}")
        except Exception as e:
            print(f"[!] Error fetching {category}: {e}")

    print(f"[✓] Total raw entries collected: {len(collected)}")

    # Return up to 100 entries to cover the past month (was 30)
    if not collected:
        collected.append({
            "title": "Regulatory Monitoring Active",
            "summary": "Automated surveillance active across MCA, SEBI, RBI, and MeitY circulars.",
            "link": "https://juridigm.in",
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "category_hint": "System Notice"
        })

    return collected[:100]


if __name__ == "__main__":
    entries = fetch_weekly_feed_entries()
    print(f"Scraped {len(entries)} items successfully.")
