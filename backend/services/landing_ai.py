import os, json, requests

API_KEY = os.getenv("LANDINGAI_API_KEY")
BASE_URL = "https://api.va.landing.ai/v1/ade"

def parse_pdf(file_path: str, model: str = "dpt-2-latest"):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    with open(file_path, "rb") as f:
        files = {"document": f}
        data = {"model": model}
        resp = requests.post(f"{BASE_URL}/parse", headers=headers, files=files, data=data)
    resp.raise_for_status()
    return resp.json()

def extract_from_markdown(markdown: str, schema: dict):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "schema": json.dumps(schema),
        "markdown": markdown
    }
    resp = requests.post(f"{BASE_URL}/extract", headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()
