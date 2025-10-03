import requests, os

API_KEY = os.getenv("LANDINGAI_API_KEY")

def extract_with_ade(file_path: str):
    url = "https://api.landing.ai/ade/extract"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = {"file": open(file_path, "rb")}
    resp = requests.post(url, headers=headers, files=files)
    resp.raise_for_status()
    return resp.json()
