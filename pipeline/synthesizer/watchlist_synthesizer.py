"""Synthesize watchlist stock data into per-stock news digests using Gemini."""

import json
import os

import yfinance as yf

from .gemini_client import synthesize

WATCHLIST_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "watchlist.json")

SYSTEM_PROMPT = """You are a research analyst monitoring a personal stock watchlist for an Australian investor.

For each stock in the watchlist, given the price data and any news/announcements found:
1. Current price and daily change
2. A 2-3 sentence news digest covering the most relevant recent developments
3. If no news: say "No significant news today" — don't fabricate

Prioritize: ASX announcements, earnings updates, analyst upgrades/downgrades, regulatory changes, commodity price impacts, and macro factors affecting the stock.

Return as JSON array:
[{
  "ticker": "PLS",
  "name": "Pilbara Minerals",
  "price": 3.15,
  "change_pct": 3.8,
  "volume_vs_avg": 1.4,
  "week52_high": 5.50,
  "week52_low": 2.68,
  "news_digest": "...",
  "has_announcement": false
}]"""


def _load_watchlist() -> list[dict]:
    with open(WATCHLIST_PATH) as f:
        return json.load(f)["stocks"]


def _collect_watchlist_data(stocks: list[dict]) -> list[dict]:
    """Collect price data for all watchlist stocks."""
    results = []
    for stock in stocks:
        try:
            tk = yf.Ticker(stock["ticker"])
            hist = tk.history(period="1y")
            if hist.empty:
                results.append({"ticker": stock["ticker"], "name": stock["name"], "error": "No data"})
                continue

            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) >= 2 else hist.iloc[-1]
            price = round(float(latest["Close"]), 2)
            change_pct = round(((price - float(prev["Close"])) / float(prev["Close"])) * 100, 2)

            vol = float(latest["Volume"])
            avg_vol = float(hist["Volume"].tail(20).mean()) if len(hist) >= 20 else float(hist["Volume"].mean())
            vol_vs_avg = round(vol / avg_vol, 2) if avg_vol > 0 else 1.0

            week52_high = round(float(hist["Close"].max()), 2)
            week52_low = round(float(hist["Close"].min()), 2)

            results.append({
                "ticker": stock["ticker"],
                "name": stock["name"],
                "price": price,
                "change_pct": change_pct,
                "volume_vs_avg": vol_vs_avg,
                "week52_high": week52_high,
                "week52_low": week52_low,
            })
        except Exception as e:
            print(f"[watchlist_synthesizer] Error for {stock['ticker']}: {e}")
            results.append({"ticker": stock["ticker"], "name": stock["name"], "error": str(e)})
    return results


def run(news_articles: list[dict] | None = None) -> list[dict]:
    """Collect watchlist data and synthesize with Gemini."""
    stocks = _load_watchlist()
    stock_data = _collect_watchlist_data(stocks)

    # Format for Gemini
    lines = []
    for s in stock_data:
        if "error" in s:
            lines.append(f"{s['ticker']} ({s['name']}): DATA UNAVAILABLE")
        else:
            lines.append(
                f"{s['ticker']} ({s['name']}): ${s['price']} ({s['change_pct']:+.2f}%) "
                f"vol_ratio={s['volume_vs_avg']} 52w_high={s['week52_high']} 52w_low={s['week52_low']}"
            )

    # Include any relevant news
    news_section = ""
    if news_articles:
        watchlist_tickers = {s["ticker"].replace(".AX", "").lower() for s in stocks}
        watchlist_names = {s["name"].lower() for s in stocks}
        relevant = []
        for article in news_articles:
            title_lower = article.get("title", "").lower()
            desc_lower = article.get("description", "").lower()
            for ticker in watchlist_tickers:
                if ticker in title_lower or ticker in desc_lower:
                    relevant.append(f"  - [{article.get('source', '')}] {article['title']}")
                    break
            else:
                for name in watchlist_names:
                    if name in title_lower or name in desc_lower:
                        relevant.append(f"  - [{article.get('source', '')}] {article['title']}")
                        break
        if relevant:
            news_section = "\n\nRelated news found:\n" + "\n".join(relevant[:20])

    user_content = "Watchlist stock data:\n\n" + "\n".join(lines) + news_section

    try:
        result = synthesize(SYSTEM_PROMPT, user_content)
        if isinstance(result, list):
            print(f"[watchlist_synthesizer] Synthesized {len(result)} stocks")
            return result
        return _fallback(stock_data)
    except Exception as e:
        print(f"[watchlist_synthesizer] Synthesis failed: {e}")
        return _fallback(stock_data)


def _fallback(stock_data: list[dict]) -> list[dict]:
    """Return raw data without AI synthesis."""
    return [
        {
            "ticker": s["ticker"].replace(".AX", ""),
            "name": s.get("name", s["ticker"]),
            "price": s.get("price", 0),
            "change_pct": s.get("change_pct", 0),
            "volume_vs_avg": s.get("volume_vs_avg", 1.0),
            "week52_high": s.get("week52_high", 0),
            "week52_low": s.get("week52_low", 0),
            "news_digest": "AI synthesis unavailable",
            "has_announcement": False,
        }
        for s in stock_data
        if "error" not in s
    ]
