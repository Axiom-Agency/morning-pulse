"""Generate brief market narrative for US + Asia markets using Gemini."""

from .gemini_client import synthesize

SYSTEM_PROMPT = """You are a markets analyst writing a 1-2 sentence overview of overnight US and Asian market performance for an Australian investor reading this at 8am AEST.

Be concise, specific, and focus on what drove the moves. Mention specific catalysts (earnings, data releases, policy decisions).

Return as JSON:
{
  "us_narrative": "1-2 sentences about US session",
  "asia_narrative": "1-2 sentences about Asian session"
}"""


def run(us_data: list[dict], asia_data: list[dict]) -> dict:
    """Generate market narrative from US + Asia data."""
    lines = ["US Markets:"]
    for idx in us_data:
        if "error" not in idx:
            lines.append(f"  {idx['name']}: {idx['price']} ({idx['change_pct']:+.2f}%)")
    lines.append("\nAsian Markets:")
    for idx in asia_data:
        if "error" not in idx:
            lines.append(f"  {idx['name']}: {idx['price']} ({idx['change_pct']:+.2f}%)")

    user_content = "\n".join(lines)

    try:
        result = synthesize(SYSTEM_PROMPT, user_content)
        if isinstance(result, dict):
            return result
        return {"us_narrative": "", "asia_narrative": ""}
    except Exception as e:
        print(f"[market_narrative] Synthesis failed: {e}")
        return {"us_narrative": "Market narrative unavailable.", "asia_narrative": "Market narrative unavailable."}
