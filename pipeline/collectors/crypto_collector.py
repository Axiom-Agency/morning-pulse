"""Collect BTC and ETH prices + 1yr history from CoinGecko API."""

import json
import os
import time

import requests

SOURCES_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sources.json")
COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def _load_config() -> dict:
    with open(SOURCES_PATH) as f:
        return json.load(f)["crypto"]


def _fetch_coin(coin_id: str, vs_currency: str) -> dict:
    """Fetch current price + 365-day history for a coin."""
    headers = {}
    api_key = os.environ.get("COINGECKO_API_KEY")
    if api_key:
        headers["x-cg-demo-api-key"] = api_key

    try:
        # Current price
        price_resp = requests.get(
            f"{COINGECKO_BASE}/simple/price",
            params={"ids": coin_id, "vs_currencies": vs_currency, "include_24hr_change": "true"},
            headers=headers,
            timeout=15,
        )
        price_resp.raise_for_status()
        price_data = price_resp.json()[coin_id]
        current_price = price_data[vs_currency]
        change_24h = price_data.get(f"{vs_currency}_24h_change", 0)

        time.sleep(2)  # Rate limit buffer

        # Historical prices (365 days)
        chart_resp = requests.get(
            f"{COINGECKO_BASE}/coins/{coin_id}/market_chart",
            params={"vs_currency": vs_currency, "days": 365, "interval": "daily"},
            headers=headers,
            timeout=30,
        )
        chart_resp.raise_for_status()
        prices = chart_resp.json().get("prices", [])

        # Convert [[timestamp_ms, price], ...] to [{date, price}, ...]
        history = [
            {"date": time.strftime("%Y-%m-%d", time.gmtime(p[0] / 1000)), "price": round(p[1], 2)}
            for p in prices
        ]

        yoy_change = 0
        if len(history) >= 2:
            first_price = history[0]["price"]
            last_price = history[-1]["price"]
            yoy_change = round(((last_price - first_price) / first_price) * 100, 2) if first_price else 0

        return {
            "coin_id": coin_id,
            "name": "Bitcoin" if coin_id == "bitcoin" else "Ethereum",
            "symbol": "BTC" if coin_id == "bitcoin" else "ETH",
            "current_price": round(current_price, 2),
            "change_24h_pct": round(change_24h, 2),
            "yoy_change_pct": yoy_change,
            "history": history,
        }
    except Exception as e:
        print(f"[crypto_collector] Error fetching {coin_id}: {e}")
        return {"coin_id": coin_id, "error": str(e)}


def collect() -> list[dict]:
    config = _load_config()
    results = []
    for coin in config["coins"]:
        results.append(_fetch_coin(coin, config["vs_currency"]))
        time.sleep(3)  # CoinGecko rate limit
    print(f"[crypto_collector] Collected {len(results)} coins")
    return results
