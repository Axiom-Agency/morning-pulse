"""Synthesize ASX market data into sector analysis using Gemini."""

import json

from .gemini_client import synthesize

SYSTEM_PROMPT = """You are an Australian equities analyst preparing a daily ASX market report.

Given the following market data and recent announcements, provide:

1. A 2-3 sentence ASX overview (what drove the market today, key themes)
2. For each of the 6 sectors, provide:
   - Sector performance summary (1 sentence)
   - For the top 3 notable movers in each sector: ticker, price, change %, and a 1-sentence explanation of WHY it moved (link to news, announcements, macro factors, commodity prices, or analyst actions)

Focus on causation — don't just say "BHP rose 2.3%", say "BHP rose 2.3% as iron ore prices rallied on renewed China stimulus hopes."

Return as JSON:
{
  "overview": "...",
  "asx200": { "level": 8142.5, "change_pct": 0.4 },
  "sectors": [{
    "name": "Mining & Resources",
    "change_pct": 1.8,
    "summary": "...",
    "movers": [{
      "ticker": "BHP",
      "name": "BHP Group",
      "price": 45.92,
      "change_pct": 2.3,
      "explanation": "..."
    }]
  }]
}"""


def run(asx_data: dict) -> dict:
    """Take raw ASX data, return synthesized sector analysis."""
    if not asx_data or "error" in asx_data.get("asx200", {}):
        print("[asx_synthesizer] No valid ASX data to synthesize")
        return _fallback(asx_data)

    # Format for Gemini
    lines = []
    lines.append(f"ASX 200: {asx_data['asx200'].get('level', 'N/A')} ({asx_data['asx200'].get('change_pct', 0):+.2f}%)")
    lines.append("")

    if asx_data.get("commodities"):
        lines.append("Commodities:")
        for c in asx_data["commodities"]:
            if "error" not in c:
                lines.append(f"  {c['name']}: ${c['price']} ({c['change_pct']:+.2f}%)")
        lines.append("")

    for sector_name, sector_data in asx_data.get("sectors", {}).items():
        lines.append(f"Sector: {sector_name} (avg change: {sector_data['sector_change_pct']:+.2f}%)")
        for stock in sector_data["stocks"]:
            if "error" not in stock:
                lines.append(f"  {stock['ticker']}: ${stock['price']} ({stock['change_pct']:+.2f}%) vol_ratio={stock.get('volume_vs_avg', 'N/A')}")
        lines.append("")

    user_content = "Here is today's ASX market data:\n\n" + "\n".join(lines)

    try:
        result = synthesize(SYSTEM_PROMPT, user_content)
        if isinstance(result, dict):
            print("[asx_synthesizer] Synthesis complete")
            return result
        return _fallback(asx_data)
    except Exception as e:
        print(f"[asx_synthesizer] Synthesis failed: {e}")
        return _fallback(asx_data)


def _fallback(asx_data: dict) -> dict:
    """Return raw data in expected format without AI synthesis."""
    sectors = []
    for name, data in asx_data.get("sectors", {}).items():
        movers = []
        for s in sorted(data["stocks"], key=lambda x: abs(x.get("change_pct", 0)), reverse=True)[:3]:
            if "error" not in s:
                movers.append({
                    "ticker": s["ticker"].replace(".AX", ""),
                    "name": s["ticker"],
                    "price": s["price"],
                    "change_pct": s["change_pct"],
                    "explanation": "No AI analysis available",
                })
        sectors.append({
            "name": name,
            "change_pct": data["sector_change_pct"],
            "summary": "AI synthesis unavailable",
            "movers": movers,
        })
    return {
        "overview": "AI synthesis unavailable. Showing raw data.",
        "asx200": asx_data.get("asx200", {}),
        "sectors": sectors,
    }
