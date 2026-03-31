"""Synthesize raw news articles into ranked, prioritised summaries using Gemini."""

import json

from .gemini_client import synthesize

SYSTEM_PROMPT = """You are a geopolitical analyst preparing a daily briefing for a sophisticated investor in Melbourne, Australia.

Given the following raw news articles from the last 24 hours, select the 5-10 most important stories by global significance. Rank by importance.

For each story:
1. Write a clear headline (rewritten, not copied from source)
2. Write a 2-3 sentence synthesis that explains what happened, why it matters, and any market/investment implications
3. Assign a severity: "high" (major geopolitical shift, direct market impact), "medium" (significant but contained), "low" (worth noting)
4. Assign a region tag: "Europe", "Asia-Pacific", "Middle East", "Americas", "Africa", "South Asia", "Global"
5. Note if this story has direct implications for Australian markets or the AUD

Return as JSON array:
[{
  "headline": "...",
  "summary": "...",
  "severity": "high|medium|low",
  "region": "...",
  "aus_impact": true/false,
  "aus_impact_note": "...",
  "sources": ["Reuters", "BBC"]
}]

Prioritize: conflicts/tensions that affect trade or commodities, central bank decisions, elections/political instability in major economies, trade policy changes, sanctions, anything affecting China-Australia or US-Australia relations."""


def run(articles: list[dict]) -> list[dict]:
    """Take raw news articles, return synthesized ranked summaries."""
    if not articles:
        print("[news_synthesizer] No articles to synthesize")
        return []

    # Format articles for the prompt
    formatted = []
    for i, a in enumerate(articles[:50], 1):
        formatted.append(
            f"{i}. [{a['source']}] {a['title']}\n   {a.get('description', '')}\n   Published: {a.get('published', 'Unknown')}"
        )

    user_content = "Here are the raw news articles from the last 24 hours:\n\n" + "\n\n".join(formatted)

    try:
        result = synthesize(SYSTEM_PROMPT, user_content)
        if isinstance(result, list):
            print(f"[news_synthesizer] Synthesized {len(result)} stories")
            return result
        return []
    except Exception as e:
        print(f"[news_synthesizer] Synthesis failed: {e}")
        # Fallback: return raw articles in expected format
        return [
            {
                "headline": a["title"],
                "summary": a.get("description", ""),
                "severity": "medium",
                "region": "Global",
                "aus_impact": False,
                "aus_impact_note": "",
                "sources": [a["source"]],
            }
            for a in articles[:10]
        ]
