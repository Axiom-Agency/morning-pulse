"""Filter culture events through Gemini for significance."""

from .gemini_client import synthesize

SYSTEM_PROMPT = """You are a culture editor filtering events for a busy professional in Melbourne/Sydney.

Given the following events and exhibitions currently showing in Sydney and Melbourne, select ONLY events that meet the SIGNIFICANCE THRESHOLD:

An event is significant if it meets ANY of these criteria:
- Major international exhibition (works on loan from overseas institutions)
- Once-in-a-generation cultural moment (e.g., a world-renowned artist's first Australian show)
- Large-scale landmark exhibition (100+ works, blockbuster scale)
- Historically important performance or cultural event
- Opening/closing week of a major exhibition

Examples of what IS significant: "French Impressionist masterworks on loan from Musée d'Orsay", "Yayoi Kusama Infinity Rooms comes to NGV", "Sydney Opera House 50th anniversary gala concert"

Examples of what is NOT significant: local gallery openings, regular theatre shows, comedy festivals, food markets, music gigs, small photography exhibitions, recurring events

If NOTHING meets the significance threshold today, return an empty array.

Return as JSON:
[{
  "title": "...",
  "venue": "...",
  "city": "Sydney|Melbourne",
  "dates": "Until 18 August 2026",
  "description": "2-3 sentences describing the exhibition/event and why it's significant",
  "significance_tag": "Landmark international loan exhibition",
  "url": "..."
}]

If nothing qualifies, return: []"""


def run(events: list[dict]) -> list[dict]:
    """Filter culture events through Gemini significance threshold."""
    if not events:
        print("[culture_synthesizer] No events to filter")
        return []

    formatted = []
    for i, e in enumerate(events, 1):
        formatted.append(
            f"{i}. [{e.get('source', '')}] {e['title']}\n"
            f"   City: {e.get('city', 'Unknown')}\n"
            f"   {e.get('description', '')}\n"
            f"   Link: {e.get('link', '')}"
        )

    user_content = "Here are current events/exhibitions in Sydney and Melbourne:\n\n" + "\n\n".join(formatted)

    try:
        result = synthesize(SYSTEM_PROMPT, user_content)
        if isinstance(result, list):
            print(f"[culture_synthesizer] {len(result)} events passed significance threshold")
            return result
        return []
    except Exception as e:
        print(f"[culture_synthesizer] Synthesis failed: {e}")
        return []
