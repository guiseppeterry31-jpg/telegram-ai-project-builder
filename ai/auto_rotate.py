from ai.openrouter import call_openrouter

# Models to try in order for auto rotation (all via OpenRouter)
AUTO_ROTATION_MODELS = [
    "mistralai/mistral-7b-instruct",
    "openchat/openchat-7b",
    "nousresearch/nous-capybara-7b",
    "microsoft/phi-2"
]

def run_auto_rotate(prompt, openrouter_key):
    """Try models in order, fallback on error or timeout"""
    last_error = None
    for model in AUTO_ROTATION_MODELS:
        try:
            print(f"Auto Mode: Trying model {model}")
            response = call_openrouter(prompt, model, openrouter_key)
            return response
        except Exception as e:
            last_error = e
            print(f"Model {model} failed: {e}. Trying next model.")
            continue
    raise Exception(f"All auto rotation models failed. Last error: {last_error}")
