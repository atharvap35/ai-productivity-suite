"""OpenAI-compatible LLM client: prompt + user input → structured JSON."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from openai import APIError, APITimeoutError, OpenAI, RateLimitError

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.2


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    except ImportError:
        pass


_load_dotenv()


def _env(key: str, default: str | None = None) -> str | None:
    val = os.environ.get(key)
    if val is None or val.strip() == "":
        return default
    return val.strip()


def _openai_api_key() -> str | None:
    key = _env("OPENAI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
            v = st.secrets["OPENAI_API_KEY"]
            if v is not None and str(v).strip():
                return str(v).strip()
    except Exception:
        pass
    return None


def is_llm_configured() -> bool:
    """True if an API key is available (env, ``.env``, or Streamlit secrets)."""
    return bool(_openai_api_key())


def _get_client() -> OpenAI | None:
    api_key = _openai_api_key()
    if not api_key:
        return None
    base_url = _env("OPENAI_BASE_URL")
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _extract_json_text(raw: str) -> str:
    raw = raw.strip()
    fence = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", raw, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return raw


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = _extract_json_text(text)
    return json.loads(cleaned)


def complete_json(
    system_prompt: str,
    user_input: str,
    *,
    model: str | None = None,
    temperature: float = DEFAULT_TEMPERATURE,
) -> dict[str, Any]:
    """
    Call the chat API and return a single JSON object.

    On success: ``{"ok": True, "data": <dict>}``
    On failure: ``{"ok": False, "error": <str>, "raw": <str | None>}``
    """
    client = _get_client()
    if client is None:
        return {
            "ok": False,
            "error": (
                "Missing OPENAI_API_KEY. Add it to a `.env` file in the project root, "
                "your environment, or `.streamlit/secrets.toml` (key: OPENAI_API_KEY)."
            ),
            "raw": None,
        }

    use_model = model or _env("OPENAI_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]

    try:
        completion = client.chat.completions.create(
            model=use_model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
    except RateLimitError as e:
        return {"ok": False, "error": f"Rate limited: {e}", "raw": None}
    except APITimeoutError as e:
        return {"ok": False, "error": f"Request timed out: {e}", "raw": None}
    except APIError as e:
        return {"ok": False, "error": f"API error: {e}", "raw": None}
    except Exception as e:
        return {"ok": False, "error": f"Request failed: {e}", "raw": None}

    choice = completion.choices[0] if completion.choices else None
    if not choice or not choice.message or choice.message.content is None:
        return {"ok": False, "error": "Empty response from model.", "raw": None}

    text = choice.message.content
    try:
        data = _parse_json_object(text)
        if not isinstance(data, dict):
            return {
                "ok": False,
                "error": "Model returned JSON that is not an object.",
                "raw": text,
            }
        return {"ok": True, "data": data}
    except json.JSONDecodeError as e:
        return {
            "ok": False,
            "error": f"Invalid JSON from model: {e}",
            "raw": text,
        }
import os

def is_llm_configured():
    return os.getenv("OPENAI_API_KEY") is not None

   