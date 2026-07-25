import os

import requests

def call_openrouter_api_with_messages(messages, model=None, max_tokens=None, debug=False):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise Exception("OPENROUTER_API_KEY environment variable is not set")

    if model is None:
        model = os.getenv("MODEL")
    if not model:
        raise Exception("MODEL not specified and MODEL env var is not set")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {"model": model, "messages": messages}
    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    resp = requests.post(url, headers=headers, json=data, timeout=(5, 120))
    if not resp.ok:
        raise Exception(f"OpenRouter API error: HTTP {resp.status_code}\n{resp.text[:1000]}")
    body = resp.json()
    content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content:
        raise Exception(f"Empty response from model {model}")
    return content
