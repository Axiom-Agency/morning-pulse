"""Collect ASX 200 index + sector representative stocks via yfinance."""

import json
import os

import yfinance as yf

SOURCES_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")
WATCHLIST_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "watchlist.json")


def _load_config():
    with open(SOURCES_PATH) as f:
        sources = json.load(f)
    return sources["market_tickers"]["asx_sectors"], sources["market_tickers"]["commodities"]


def _get_stock_data(ticker: str) -> dict:
    """Fetch price, change, volume data for a single ticker."""
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="1mo")
        if hist.empty:
            return {"ticker": ticker, "error": "No data"}

        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) >= 2 else hist.iloc[-1]
        price = round(float(latest["Close"]), 2)
        change_pct = round(((price - float(prev["Close"])) / float(prev["Close"])) * 100, 2) if float(prev["Close"]) != 0 else 0

        # Volume vs 20-day average
        vol = float(latest["Volume"])
        avg_vol = float(hist["Volume"].tail(20).mean()) if len(hist) >= 20 else float(hist["Volume"].mean())
        vol_vs_avg = round(vol / avg_vol, 2) if avg_vol > 0 else 1.0

        return {
            "ticker": ticker,
            "price": price,
            "change_pct": change_pct,
            "volume": int(vol),
            "volume_vs_avg": vol_vs_avg,
        }
    except Exception as e:
        print(f"[asx_markets] Error fetching {ticker}: {e}")
        return {"ticker": ticker, "error": str(e)}


def _get_asx200() -> dict:
    """Get ASX 200 index data."""
    try:
        tk = yf.Ticker("^AXJO")
        hist = tk.history(period="5d")
        if hist.empty:
            return {"error": "No data"}
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) >= 2 else hist.iloc[-1]
        level = round(float(latest["Close"]), 2)
        change_pct = round(((level - float(prev["Close"])) / float(prev["Close"])) * 100, 2)
        return {"level": level, "change_pct": change_pct}
    except Exception as e:
        print(f"[asx_markets] Error fetching ASX 200: {e}")
        return {"error": str(e)}


def _get_commodity_data(commodity: dict) -> dict:
    try:
        tk = yf.Ticker(commodity["ticker"])
        hist = tk.history(period="5d")
        if hist.empty:
            return {"ticker": commodity["ticker"], "name": commodity["name"], "error": "No data"}
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) >= 2 else hist.iloc[-1]
        price = round(float(latest["Close"]), 2)
        change_pct = round(((price - float(prev["Close"])) / float(prev["Close"])) * 100, 2)
        return {"ticker": commodity["ticker"], "name": commodity["name"], "price": price, "change_pct": change_pct}
    except Exception as e:
        return {"ticker": commodity["ticker"], "name": commodity["name"], "error": str(e)}


def collect() -> dict:
    """Collect ASX 200 + all sector stocks + commodities."""
    sectors_config, commodities_config = _load_config()

    asx200 = _get_asx200()

    sectors = {}
    for sector_name, tickers in sectors_config.items():
        stocks = [_get_stock_data(t) for t in tickers]
        valid = [s for s in stocks if "error" not in s]
        sector_change = round(sum(s["change_pct"] for s in valid) / len(valid), 2) if valid else 0
        sectors[sector_name] = {
            "stocks": stocks,
            "sector_change_pct": sector_change,
        }

    commodities = [_get_commodity_data(c) for c in commodities_config]

    print(f"[asx_markets] Collected ASX 200 + {len(sectors)} sectors + {len(commodities)} commodities")
    return {
        "asx200": asx200,
        "sectors": sectors,
        "commodities": commodities,
    }
