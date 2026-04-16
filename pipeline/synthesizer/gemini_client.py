"""AI synthesis client — MiniMax API with rate limiting and retry logic."""

import json
import os
import time
from typing import Union

import requests

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1/chat/completions"
MODEL = "MiniMax-Text-01"

# Track last call time for rate limiting
_last_call_time = 0.0
_MIN_INTERVAL = 2  # seconds between calls (MiniMax is much faster)


def synthesize(system_prompt: str, user_content: str, max_retries: int = 3, temperature: float = 0.3) -> Union[dict, list]:
    """
    Call MiniMax with a system prompt and user content.
    Returns parsed JSON. Handles rate limiting with exponential backoff.
    """
    global _last_call_time

    api_key = os.environ.get("MINIMAX_API_KEY", MINIMAX_API_KEY)

    # Enforce minimum interval between calls
    elapsed = time.time() - _last_call_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "max_tokens": 4096,
    }

    for attempt in range(max_retries):
        try:
            _last_call_time = time.time()
            response = requests.post(MINIMAX_BASE_URL, headers=headers, json=payload, timeout=60)

            if response.status_code == 429:
                wait = 2 ** attempt * 5
                print(f"[ai_client] Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue

            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]

            # Strip markdown code fences if present
            if text.strip().startswith("```"):
                text = text.strip().split("\n", 1)[1].rsplit("```", 1)[0]

            return json.loads(text)

        except json.JSONDecodeError as e:
            print(f"[ai_client] JSON parse error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
        except Exception as e:
            print(f"[ai_client] Error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(5)

    raise Exception(f"MiniMax API failed after {max_retries} retries")
