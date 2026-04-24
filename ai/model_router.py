from bot.user_state import get_user_model

def route_request(user_id, prompt, openrouter_key):
    """Route request to the user's selected model"""
    model_type = get_user_model(user_id)
    if model_type == "local_mistral":
        try:
            from ai.local_mistral import run_local_mistral
            return run_local_mistral(prompt)
        except Exception as e:
            # Fallback to OpenRouter if local model fails
            print(f"Local Mistral failed: {e}. Falling back to OpenRouter.")
            from ai.openrouter import call_openrouter
            return call_openrouter(prompt, "openrouter/free", openrouter_key)
    elif model_type == "openrouter_mistral":
        from ai.openrouter import call_openrouter
        # Use the free OpenRouter model
        return call_openrouter(prompt, "openrouter/free", openrouter_key)
    elif model_type == "auto":
        from ai.auto_rotate import run_auto_rotate
        return run_auto_rotate(prompt, openrouter_key)
    else:
        # Fallback to auto mode
        from ai.auto_rotate import run_auto_rotate
        return run_auto_rotate(prompt, openrouter_key)
