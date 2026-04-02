"""LLM client: Ollama (default) + OpenAI fallback → structured JSON"""

from __future__ import annotations

import json
import os
import re
import requests
from pathlib import Path
from typing import Any

from openai import OpenAI, APIError, APITimeoutError, RateLimitError

# -------------------------
# CONFIG
# -------------------------

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.2

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"  # 🔥 fast + reliable


# -------------------------
# ENV SETUP
# -------------------------

def _load_dotenv():
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    except:
        pass


_load_dotenv()


def _env(key: str, default=None):
    val = os.environ.get(key)
    return val.strip() if val else default


def _openai_api_key():
    key = _env("OPENAI_API_KEY")
    if key:
        return key

    try:
        import streamlit as st
        if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except:
        pass

    return None


def is_llm_configured():
    """Check if either OpenAI or Ollama is available"""
    if _openai_api_key():
        return True

    try:
        requests.get("http://localhost:11434", timeout=2)
        return True
    except:
        return False


# -------------------------
# JSON CLEANER
# -------------------------

def _extract_json(text: str):
    text = text.strip()

    # remove markdown
    text = re.sub(r"```json|```", "", text).strip()

    # extract first json object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return text


def _parse_json(text: str):
    cleaned = _extract_json(text)
    return json.loads(cleaned)


# -------------------------
# OLLAMA (PRIMARY)
# -------------------------

def _call_ollama(system_prompt: str, user_input: str):
    try:
        full_prompt = f"""{system_prompt}

IMPORTANT:
Return ONLY valid JSON.
Do NOT include explanation.

User Input:
{user_input}
"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=120  # 🔥 increased timeout
        )

        text = response.json().get("response", "")

        try:
            data = _parse_json(text)
            return {"ok": True, "data": data}
        except:
            return {"ok": False, "error": "Invalid JSON from Ollama", "raw": text}

    except Exception as e:
        return {"ok": False, "error": str(e), "raw": None}


# -------------------------
# OPENAI (FALLBACK)
# -------------------------

def _get_client():
    key = _openai_api_key()
    if not key:
        return None
    return OpenAI(api_key=key)


# -------------------------
# MAIN FUNCTION
# -------------------------

def complete_json(system_prompt: str, user_input: str, *, model=None, temperature=DEFAULT_TEMPERATURE):
    """
    Returns:
    {"ok": True, "data": dict}
    OR
    {"ok": False, "error": str, "raw": str}
    """

    # 🔥 TRY OLLAMA FIRST
    ollama_result = _call_ollama(system_prompt, user_input)

    if ollama_result["ok"]:
        return ollama_result

    # fallback to OpenAI if available
    client = _get_client()
    if client is None:
        return ollama_result

    try:
        completion = client.chat.completions.create(
            model=model or DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        text = completion.choices[0].message.content

        try:
            data = _parse_json(text)
            return {"ok": True, "data": data}
        except:
            return {"ok": False, "error": "Invalid JSON from OpenAI", "raw": text}

    except Exception as e:
        return {"ok": False, "error": str(e), "raw": None}