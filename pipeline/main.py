"""Main orchestrator — runs the full briefing pipeline."""

import argparse
import sys
import time

from .collectors import news_collector, us_markets, asia_markets, asx_markets, crypto_collector, fx_collector, culture_collector
from .synthesizer import news_synthesizer, asx_synthesizer, watchlist_synthesizer, culture_synthesizer, market_narrative
from .publisher import json_publisher, email_publisher


def run_7am() -> dict:
    """Pre-market preview: US recap, commodities, FX, breaking news."""
    print("=== 7am Pre-market Preview ===")
    data = {}

    print("[1/4] Collecting US markets...")
    data["us_markets"] = us_markets.collect()

    print("[2/4] Collecting Asia markets...")
    data["asia_markets"] = asia_markets.collect()

    print("[3/4] Collecting ASX + commodities...")
    asx_data = asx_markets.collect()
    data["commodities"] = asx_data.get("commodities", [])
    data["asx200"] = asx_data.get("asx200", {})

    print("[4/4] Collecting FX snapshot...")
    fx_data = fx_collector.collect()
    # For 7am, just include current rates without full history
    data["fx"] = [
        {"ticker": f["ticker"], "name": f["name"], "current_rate": f.get("current_rate", 0), "change_pct": f.get("change_pct", 0)}
        for f in fx_data
        if "error" not in f
    ]

    # Quick news check
    print("[+] Collecting breaking news...")
    raw_news = news_collector.collect()
    if raw_news:
        data["world_news"] = news_synthesizer.run(raw_news[:20])

    # Market narrative
    print("[+] Generating market narrative...")
    data["narrative"] = market_narrative.run(data["us_markets"], data["asia_markets"])

    return data


def run_8am() -> dict:
    """Full morning briefing — all 6 sections."""
    print("=== 8am Full Morning Briefing ===")
    data = {}

    # Phase 1: Collect all raw data
    print("[1/7] Collecting world news...")
    raw_news = news_collector.collect()

    print("[2/7] Collecting US markets...")
    data["us_markets"] = us_markets.collect()

    print("[3/7] Collecting Asia markets...")
    data["asia_markets"] = asia_markets.collect()

    print("[4/7] Collecting ASX data...")
    raw_asx = asx_markets.collect()

    print("[5/7] Collecting crypto...")
    data["crypto"] = crypto_collector.collect()

    print("[6/7] Collecting FX...")
    data["fx"] = fx_collector.collect()

    print("[7/7] Collecting culture events...")
    raw_culture = culture_collector.collect()

    # Phase 2: Synthesize with Gemini (5 calls, spaced)
    print("\n--- AI Synthesis Phase ---")

    print("[Synth 1/5] News synthesis...")
    data["world_news"] = news_synthesizer.run(raw_news)

    print("[Synth 2/5] Market narrative...")
    data["narrative"] = market_narrative.run(data["us_markets"], data["asia_markets"])

    print("[Synth 3/5] ASX deep dive...")
    data["asx_deep_dive"] = asx_synthesizer.run(raw_asx)

    print("[Synth 4/5] Watchlist...")
    data["watchlist"] = watchlist_synthesizer.run(raw_news)

    print("[Synth 5/5] Culture events...")
    data["culture"] = culture_synthesizer.run(raw_culture)

    return data


def run_5pm() -> dict:
    """ASX close wrap."""
    print("=== 5pm ASX Close Wrap ===")
    data = {}

    print("[1/3] Collecting ASX close data...")
    raw_asx = asx_markets.collect()

    print("[2/3] Collecting US futures/preview...")
    data["us_markets"] = us_markets.collect()

    print("[3/3] Synthesizing ASX data...")
    data["asx_deep_dive"] = asx_synthesizer.run(raw_asx)

    # Watchlist close data
    print("[+] Collecting watchlist close...")
    data["watchlist"] = watchlist_synthesizer.run()

    # FX snapshot
    fx_data = fx_collector.collect()
    data["fx"] = [
        {"ticker": f["ticker"], "name": f["name"], "current_rate": f.get("current_rate", 0), "change_pct": f.get("change_pct", 0)}
        for f in fx_data
        if "error" not in f
    ]

    return data


def main():
    parser = argparse.ArgumentParser(description="Morning Pulse briefing pipeline")
    parser.add_argument("--briefing-type", choices=["7am", "8am", "5pm"], required=True)
    parser.add_argument("--no-email", action="store_true", help="Skip email notification")
    args = parser.parse_args()

    runners = {"7am": run_7am, "8am": run_8am, "5pm": run_5pm}
    briefing_data = runners[args.briefing_type]()

    # Publish JSON
    print("\n--- Publishing ---")
    json_publisher.publish(briefing_data, args.briefing_type)

    # Send email
    if not args.no_email:
        email_publisher.publish(briefing_data, args.briefing_type)

    print(f"\n=== {args.briefing_type} briefing complete ===")


if __name__ == "__main__":
    main()
