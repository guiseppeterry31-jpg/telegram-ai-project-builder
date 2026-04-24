from ai.openrouter import call_openrouter

# Models to try in order for auto rotation (all via OpenRouter)
# Using free models that work on OpenRouter
AUTO_ROTATION_MODELS = [
    "openrouter/free",  # Free model router
    "google/gemini-pro",  # Free tier available
    "meta-llama/llama-3.1-8b-instruct",  # Free open source
    "microsoft/phi-2"  # Small free model
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
