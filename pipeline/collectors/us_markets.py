"""Collect US market index data via yfinance."""

import json
import os

import yfinance as yf

SOURCES_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")


def _load_tickers() -> list[dict]:
    with open(SOURCES_PATH) as f:
        return json.load(f)["market_tickers"]["us_indices"]


def _get_index_data(ticker_info: dict) -> dict:
    """Fetch current price + daily change for a single index."""
    try:
        tk = yf.Ticker(ticker_info["ticker"])
        hist = tk.history(period="5d")
        if hist.empty:
            return {"ticker": ticker_info["ticker"], "name": ticker_info["name"], "error": "No data"}

        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) >= 2 else hist.iloc[-1]
        price = round(float(latest["Close"]), 2)
        change = round(price - float(prev["Close"]), 2)
        change_pct = round((change / float(prev["Close"])) * 100, 2) if float(prev["Close"]) != 0 else 0

        # 5-day trend
        if len(hist) >= 5:
            first = float(hist.iloc[0]["Close"])
            last = float(hist.iloc[-1]["Close"])
            trend_pct = ((last - first) / first) * 100
            trend = "up" if trend_pct > 0.2 else "down" if trend_pct < -0.2 else "flat"
        else:
            trend = "flat"

        return {
            "ticker": ticker_info["ticker"],
            "name": ticker_info["name"],
            "price": price,
            "change": change,
            "change_pct": change_pct,
            "trend_5d": trend,
        }
    except Exception as e:
        print(f"[us_markets] Error fetching {ticker_info['ticker']}: {e}")
        return {"ticker": ticker_info["ticker"], "name": ticker_info["name"], "error": str(e)}


def collect() -> list[dict]:
    """Collect all US index data."""
    tickers = _load_tickers()
    results = [_get_index_data(t) for t in tickers]
    print(f"[us_markets] Collected {len(results)} US indices")
    return results
