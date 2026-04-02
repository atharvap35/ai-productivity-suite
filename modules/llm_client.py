import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def complete_json(system_prompt, user_input):
    try:
        full_prompt = f"""{system_prompt}

Return ONLY valid JSON.

User Input:
{user_input}
"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60
        )

        text = response.json().get("response", "")

        # extract JSON safely
        import re
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            return {"ok": True, "data": data}

        return {"ok": False, "error": "No JSON found", "raw": text}

    except Exception as e:
        return {"ok": False, "error": str(e), "raw": None}