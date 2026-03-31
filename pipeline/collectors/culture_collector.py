"""Collect culture events from RSS feeds and web scraping."""

import json
import os

import feedparser
import requests
from bs4 import BeautifulSoup

SOURCES_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")


def _load_config():
    with open(SOURCES_PATH) as f:
        data = json.load(f)
    return data["rss_feeds"].get("culture", []), data.get("culture_scrape_urls", [])


def _fetch_rss(source: dict) -> list[dict]:
    events = []
    try:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries[:20]:
            events.append({
                "title": entry.get("title", ""),
                "description": entry.get("summary", ""),
                "link": entry.get("link", ""),
                "source": source["name"],
                "city": "Sydney" if "sydney" in source["name"].lower() else "Melbourne",
            })
    except Exception as e:
        print(f"[culture_collector] RSS error for {source['name']}: {e}")
    return events


def _scrape_venue(venue: dict) -> list[dict]:
    """Scrape exhibition/event titles from a venue page."""
    events = []
    try:
        resp = requests.get(venue["url"], timeout=15, headers={
            "User-Agent": "MorningPulse/1.0 (personal market briefing)"
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Generic extraction: look for headings and links in main content
        for heading in soup.find_all(["h2", "h3", "h4"], limit=15):
            title = heading.get_text(strip=True)
            if len(title) < 5:
                continue
            link_tag = heading.find("a")
            link = link_tag["href"] if link_tag and link_tag.get("href") else venue["url"]
            if link.startswith("/"):
                from urllib.parse import urljoin
                link = urljoin(venue["url"], link)

            # Try to get a description from the next sibling
            desc = ""
            next_p = heading.find_next_sibling("p")
            if next_p:
                desc = next_p.get_text(strip=True)[:300]

            events.append({
                "title": title,
                "description": desc,
                "link": link,
                "source": venue["name"],
                "city": venue["city"],
            })
    except Exception as e:
        print(f"[culture_collector] Scrape error for {venue['name']}: {e}")
    return events


def collect() -> list[dict]:
    rss_sources, scrape_sources = _load_config()

    all_events = []
    for source in rss_sources:
        all_events.extend(_fetch_rss(source))
    for venue in scrape_sources:
        all_events.extend(_scrape_venue(venue))

    print(f"[culture_collector] Collected {len(all_events)} raw culture events")
    return all_events
