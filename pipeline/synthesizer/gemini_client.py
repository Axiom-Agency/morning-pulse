"""Base Gemini API client with rate limiting and retry logic."""

import json
import os
import time

import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

MODEL = "gemini-2.5-pro"

# Track last call time for rate limiting
_last_call_time = 0.0
_MIN_INTERVAL = 13  # seconds between calls (safe for 5 RPM)


def synthesize(system_prompt: str, user_content: str, max_retries: int = 3, temperature: float = 0.3) -> dict | list:
    """
    Call Gemini 2.5 Pro with a system prompt and user content.
    Returns parsed JSON. Handles rate limiting with exponential backoff.
    """
    global _last_call_time

    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=temperature,
        ),
    )

    # Enforce minimum interval between calls
    elapsed = time.time() - _last_call_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)

    for attempt in range(max_retries):
        try:
            _last_call_time = time.time()
            response = model.generate_content(user_content)
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            # Try to extract JSON from response
            text = response.text if response else ""
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    pass
            print(f"[gemini_client] JSON parse error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait = 2 ** attempt * 10
                print(f"[gemini_client] Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"[gemini_client] Error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(5)

    raise Exception(f"Gemini API failed after {max_retries} retries")
