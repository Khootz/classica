import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

def ask_gemini(messages: list, model="google/gemini-2.0-flash-exp:free"):
    """
    messages = [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    Uses OpenRouter API for chat completions
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages
    }
    
    resp = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
    resp.raise_for_status()
    
    return resp.json()["choices"][0]["message"]["content"]
