"""Collect FX rates (AUD/USD, NZD/USD, AUD/NZD) with 1yr history via yfinance."""

import json
import os

import yfinance as yf

SOURCES_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")


def _load_pairs() -> list[dict]:
    with open(SOURCES_PATH) as f:
        return json.load(f)["market_tickers"]["fx_pairs"]


def _fetch_pair(pair_info: dict) -> dict:
    """Fetch current rate + 1yr daily history for an FX pair."""
    try:
        tk = yf.Ticker(pair_info["ticker"])
        hist = tk.history(period="1y")
        if hist.empty:
            return {"ticker": pair_info["ticker"], "name": pair_info["name"], "error": "No data"}

        latest = float(hist.iloc[-1]["Close"])
        prev = float(hist.iloc[-2]["Close"]) if len(hist) >= 2 else latest
        change_pct = round(((latest - prev) / prev) * 100, 4) if prev else 0

        first_price = float(hist.iloc[0]["Close"])
        yoy_change = round(((latest - first_price) / first_price) * 100, 2) if first_price else 0

        # Build daily history
        history = []
        for date, row in hist.iterrows():
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "rate": round(float(row["Close"]), 4),
            })

        return {
            "ticker": pair_info["ticker"],
            "name": pair_info["name"],
            "current_rate": round(latest, 4),
            "change_pct": change_pct,
            "yoy_change_pct": yoy_change,
            "history": history,
        }
    except Exception as e:
        print(f"[fx_collector] Error fetching {pair_info['ticker']}: {e}")
        return {"ticker": pair_info["ticker"], "name": pair_info["name"], "error": str(e)}


def collect() -> list[dict]:
    pairs = _load_pairs()
    results = [_fetch_pair(p) for p in pairs]
    print(f"[fx_collector] Collected {len(results)} FX pairs")
    return results
