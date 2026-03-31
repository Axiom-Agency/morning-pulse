"""Write briefing data to JSON files in /data and /frontend/public/data."""

import json
import os
import shutil
from datetime import datetime

from dateutil import tz

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
DATA_DIR = os.path.join(BASE_DIR, "data")
FRONTEND_DATA_DIR = os.path.join(BASE_DIR, "frontend", "public", "data")
HISTORY_DIR = os.path.join(DATA_DIR, "history")
MELB_TZ = tz.gettz("Australia/Melbourne")


def publish(briefing_data: dict, briefing_type: str) -> str:
    """Write briefing JSON to data directories. Returns the filename."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FRONTEND_DATA_DIR, exist_ok=True)
    os.makedirs(HISTORY_DIR, exist_ok=True)

    now = datetime.now(MELB_TZ)
    briefing_data["meta"] = {
        "briefing_type": briefing_type,
        "generated_at": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "display_date": now.strftime("%A %d %B %Y"),
        "display_time": now.strftime("%I:%M %p AEST"),
    }

    # Write latest file
    latest_filename = f"latest-{briefing_type}.json"
    latest_path = os.path.join(DATA_DIR, latest_filename)
    with open(latest_path, "w") as f:
        json.dump(briefing_data, f, indent=2, default=str)

    # Copy to frontend public
    frontend_path = os.path.join(FRONTEND_DATA_DIR, latest_filename)
    shutil.copy2(latest_path, frontend_path)

    # Write to history
    history_filename = f"{now.strftime('%Y-%m-%d')}-{briefing_type}.json"
    history_path = os.path.join(HISTORY_DIR, history_filename)
    with open(history_path, "w") as f:
        json.dump(briefing_data, f, indent=2, default=str)

    print(f"[json_publisher] Published {latest_filename} and archived to history/{history_filename}")
    return latest_filename
