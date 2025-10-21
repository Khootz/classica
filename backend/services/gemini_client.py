import os
import requests
import time

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

def ask_gemini(messages: list, model="google/gemini-2.0-flash-exp:free", max_retries=3):
    """
    messages = [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    Uses OpenRouter API for chat completions with retry logic for rate limits
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages
    }
    
    for attempt in range(max_retries):
        try:
            resp = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:  # Rate limit
                if attempt < max_retries - 1:
                    # Exponential backoff: 2s, 4s, 8s
                    wait_time = 2 ** (attempt + 1)
                    print(f"⚠️ Rate limit hit, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Rate limit exceeded after {max_retries} retries. Please wait a moment and try again.")
            elif resp.status_code == 401:
                raise Exception("Invalid or missing OpenRouter API key. Check OPENROUTER_API_KEY environment variable.")
            else:
                raise Exception(f"OpenRouter API error: {resp.status_code} - {resp.text}")
        except requests.exceptions.Timeout:
            raise Exception("OpenRouter API request timed out. Please try again.")
        except Exception as e:
            raise Exception(f"Unexpected error calling OpenRouter: {str(e)}")
    
    raise Exception("Failed to get response from OpenRouter after multiple retries.")
