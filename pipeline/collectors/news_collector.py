"""Collect world news from RSS feeds and deduplicate."""

import json
import os
from datetime import datetime, timedelta, timezone

import feedparser

SOURCES_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")


def load_sources() -> list[dict]:
    with open(SOURCES_PATH) as f:
        return json.load(f)["rss_feeds"]["world_news"]


def fetch_feed(source: dict) -> list[dict]:
    """Fetch a single RSS feed, return normalised article dicts."""
    articles = []
    try:
        feed = feedparser.parse(source["url"])
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

        for entry in feed.entries[:30]:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

            if published and published < cutoff:
                continue

            articles.append({
                "title": entry.get("title", ""),
                "description": entry.get("summary", entry.get("description", "")),
                "link": entry.get("link", ""),
                "published": published.isoformat() if published else None,
                "source": source["name"],
            })
    except Exception as e:
        print(f"[news_collector] Failed to fetch {source['name']}: {e}")
    return articles


def deduplicate(articles: list[dict]) -> list[dict]:
    """Simple dedup: if two headlines share 4+ significant words, keep the first."""
    seen_keys: list[set] = []
    unique = []
    stop_words = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "is", "are", "was", "were", "has", "have", "with", "from", "by"}

    for article in articles:
        words = set(article["title"].lower().split()) - stop_words
        is_dup = False
        for seen in seen_keys:
            if len(words & seen) >= 4:
                is_dup = True
                break
        if not is_dup:
            seen_keys.append(words)
            unique.append(article)
    return unique


def collect() -> list[dict]:
    """Main entry point: fetch all feeds, deduplicate, return articles."""
    sources = load_sources()
    all_articles = []
    for source in sources:
        all_articles.extend(fetch_feed(source))

    # Sort by publish date descending
    all_articles.sort(
        key=lambda a: a.get("published") or "1970-01-01",
        reverse=True,
    )
    deduped = deduplicate(all_articles)
    print(f"[news_collector] Collected {len(all_articles)} articles, {len(deduped)} after dedup")
    return deduped
