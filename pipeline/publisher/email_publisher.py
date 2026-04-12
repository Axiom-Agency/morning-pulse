"""Send briefing notification emails via Resend."""

import os
from datetime import datetime

from dateutil import tz

MELB_TZ = tz.gettz("Australia/Melbourne")


def _severity_emoji(severity: str) -> str:
    return {"high": "\U0001f534", "medium": "\U0001f7e1", "low": "\U0001f7e2"}.get(severity, "\u26aa")


def _change_arrow(change: float) -> str:
    return "\u2b06" if change >= 0 else "\u2b07"


def _build_html(briefing_data: dict, briefing_type: str, dashboard_url: str) -> str:
    now = datetime.now(MELB_TZ)
    date_str = now.strftime("%A %d %B %Y")
    time_str = {"7am": "7:00 AM", "8am": "8:00 AM", "5pm": "5:00 PM"}.get(briefing_type, briefing_type)

    # Extract key metrics
    asx = briefing_data.get("asx_deep_dive", {}).get("asx200", {})
    asx_level = asx.get("level", "N/A")
    asx_change = asx.get("change_pct", 0)

    us = briefing_data.get("us_markets", [])
    sp500 = next((i for i in us if "GSPC" in i.get("ticker", "") or "S&P" in i.get("name", "")), {})
    sp_price = sp500.get("price", "N/A")
    sp_change = sp500.get("change_pct", 0)

    fx = briefing_data.get("fx", [])
    audusd = next((f for f in fx if "AUDUSD" in f.get("ticker", "") or "AUD/USD" in f.get("name", "")), {})
    aud_rate = audusd.get("current_rate", "N/A")

    crypto = briefing_data.get("crypto", [])
    btc = next((c for c in crypto if c.get("symbol") == "BTC"), {})
    btc_price = btc.get("current_price", "N/A")

    # Top stories
    stories = briefing_data.get("world_news", [])[:5]
    stories_html = ""
    for s in stories:
        emoji = _severity_emoji(s.get("severity", "low"))
        stories_html += f'<tr><td style="padding:4px 0;font-size:14px;color:#333;">{emoji} {s["headline"]}</td></tr>\n'
    remaining = len(briefing_data.get("world_news", [])) - len(stories)
    if remaining > 0:
        stories_html += f'<tr><td style="padding:4px 0;font-size:13px;color:#888;">\u2192 {remaining} more stories</td></tr>\n'

    # Watchlist highlights
    watchlist = briefing_data.get("watchlist", [])
    top_movers = sorted(watchlist, key=lambda w: abs(w.get("change_pct", 0)), reverse=True)[:3]
    watchlist_html = ""
    for w in top_movers:
        arrow = _change_arrow(w.get("change_pct", 0))
        color = "#1D9E75" if w.get("change_pct", 0) >= 0 else "#E24B4A"
        digest = w.get("news_digest", "")
        short_digest = (digest[:60] + "...") if len(digest) > 60 else digest
        watchlist_html += (
            f'<tr><td style="padding:4px 0;font-size:14px;color:#333;">'
            f'{arrow} <strong>{w.get("ticker", "")}</strong> '
            f'<span style="color:{color}">{w.get("change_pct", 0):+.1f}%</span>'
            f' \u2014 {short_digest}</td></tr>\n'
        )

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;padding:0;background:#f5f5f0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f0;padding:20px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden;">

<tr><td style="padding:32px 32px 16px;border-bottom:2px solid #1a1a1a;">
  <h1 style="margin:0;font-size:20px;font-weight:700;letter-spacing:1px;color:#1a1a1a;">MORNING PULSE</h1>
  <p style="margin:4px 0 0;font-size:13px;color:#666;">{date_str}, {time_str} AEST</p>
</td></tr>

<tr><td style="padding:24px 32px 16px;">
  <p style="margin:0 0 12px;font-size:11px;font-weight:600;letter-spacing:1px;color:#888;text-transform:uppercase;">Markets at a glance</p>
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td style="padding:8px 12px;background:#f8f8f5;border-radius:6px;width:25%;vertical-align:top;">
        <p style="margin:0;font-size:11px;color:#888;">ASX 200</p>
        <p style="margin:2px 0 0;font-size:16px;font-weight:600;color:#1a1a1a;">{asx_level}</p>
        <p style="margin:2px 0 0;font-size:12px;color:{'#1D9E75' if asx_change >= 0 else '#E24B4A'};">{asx_change:+.2f}%</p>
      </td>
      <td width="8"></td>
      <td style="padding:8px 12px;background:#f8f8f5;border-radius:6px;width:25%;vertical-align:top;">
        <p style="margin:0;font-size:11px;color:#888;">S&P 500</p>
        <p style="margin:2px 0 0;font-size:16px;font-weight:600;color:#1a1a1a;">{sp_price}</p>
        <p style="margin:2px 0 0;font-size:12px;color:{'#1D9E75' if sp_change >= 0 else '#E24B4A'};">{sp_change:+.2f}%</p>
      </td>
      <td width="8"></td>
      <td style="padding:8px 12px;background:#f8f8f5;border-radius:6px;width:25%;vertical-align:top;">
        <p style="margin:0;font-size:11px;color:#888;">AUD/USD</p>
        <p style="margin:2px 0 0;font-size:16px;font-weight:600;color:#1a1a1a;">{aud_rate}</p>
      </td>
      <td width="8"></td>
      <td style="padding:8px 12px;background:#f8f8f5;border-radius:6px;width:25%;vertical-align:top;">
        <p style="margin:0;font-size:11px;color:#888;">BTC/AUD</p>
        <p style="margin:2px 0 0;font-size:16px;font-weight:600;color:#1a1a1a;">${btc_price:,.0f}</p>
      </td>
    </tr>
  </table>
</td></tr>

<tr><td style="padding:24px 32px 16px;">
  <p style="margin:0 0 8px;font-size:11px;font-weight:600;letter-spacing:1px;color:#888;text-transform:uppercase;">Top stories</p>
  <table width="100%" cellpadding="0" cellspacing="0">
    {stories_html}
  </table>
</td></tr>

<tr><td style="padding:16px 32px 24px;">
  <p style="margin:0 0 8px;font-size:11px;font-weight:600;letter-spacing:1px;color:#888;text-transform:uppercase;">Watchlist highlights</p>
  <table width="100%" cellpadding="0" cellspacing="0">
    {watchlist_html}
  </table>
</td></tr>

<tr><td style="padding:24px 32px;text-align:center;border-top:1px solid #eee;">
  <a href="{dashboard_url}" style="display:inline-block;padding:12px 32px;background:#1a1a1a;color:#fff;text-decoration:none;border-radius:6px;font-size:14px;font-weight:600;">VIEW FULL BRIEFING \u2192</a>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""


def _build_subject(briefing_data: dict, briefing_type: str) -> str:
    now = datetime.now(MELB_TZ)
    date_part = now.strftime("%a %d %b")

    asx = briefing_data.get("asx_deep_dive", {}).get("asx200", {})
    asx_str = f"ASX {asx.get('change_pct', 0):+.1f}%" if asx.get("change_pct") is not None else ""

    us = briefing_data.get("us_markets", [])
    sp500 = next((i for i in us if "GSPC" in i.get("ticker", "")), {})
    sp_str = f"S&P {sp500.get('change_pct', 0):+.1f}%" if sp500.get("change_pct") is not None else ""

    stories_count = len(briefing_data.get("world_news", []))
    stories_str = f"{stories_count} stories" if stories_count else ""

    parts = ["Morning Pulse", date_part]
    if asx_str:
        parts.append(asx_str)
    if sp_str:
        parts.append(sp_str)
    if stories_str:
        parts.append(stories_str)
    return " \u00b7 ".join(parts)


def publish(briefing_data: dict, briefing_type: str) -> bool:
    """Send email notification via Resend."""
    api_key = os.environ.get("RESEND_API_KEY")
    email_to = os.environ.get("EMAIL_TO")
    dashboard_url = os.environ.get("DASHBOARD_URL", "https://morning-pulse.vercel.app")

    if not api_key or not email_to:
        print("[email_publisher] RESEND_API_KEY or EMAIL_TO not set, skipping email")
        return False

    try:
        import resend
        resend.api_key = api_key

        subject = _build_subject(briefing_data, briefing_type)
        html = _build_html(briefing_data, briefing_type, dashboard_url)

        params = {
            "from": "Morning Pulse <onboarding@resend.dev>",
            "to": [email_to],
            "subject": subject,
            "html": html,
        }
        result = resend.Emails.send(params)
        print(f"[email_publisher] Email sent: {result}")
        return True
    except Exception as e:
        print(f"[email_publisher] Failed to send email: {e}")
        return False
