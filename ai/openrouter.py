import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout))
)
def call_openrouter(prompt, model, api_key):
    """Call OpenRouter API with specified model and prompt, with retry logic"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://telegram-ai-builder",
        "X-Title": "Telegram AI Project Builder"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 4096
    }
    try:
        response = requests.post(OPENROUTER_ENDPOINT, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        raise Exception("OpenRouter API request timed out")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
    except KeyError as e:
        raise Exception(f"Invalid OpenRouter response format: missing key {e}")
