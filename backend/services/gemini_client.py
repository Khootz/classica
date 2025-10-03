import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(messages: list, model="gemini-1.5-flash"):
    """
    messages = [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    """
    resp = genai.GenerativeModel(model).generate_content(
        [m["content"] for m in messages]
    )
    return resp.text
