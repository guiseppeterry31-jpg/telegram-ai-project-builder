from bot.user_state import get_user_model

def route_request(user_id, prompt, openrouter_key):
    """Route request to the user's selected model"""
    model_type = get_user_model(user_id)
    if model_type == "local_mistral":
        from ai.local_mistral import run_local_mistral
        return run_local_mistral(prompt)
    elif model_type == "openrouter_mistral":
        from ai.openrouter import call_openrouter
        return call_openrouter(prompt, "mistralai/mistral-7b-instruct", openrouter_key)
    elif model_type == "auto":
        from ai.auto_rotate import run_auto_rotate
        return run_auto_rotate(prompt, openrouter_key)
    else:
        # Fallback to auto mode
        from ai.auto_rotate import run_auto_rotate
        return run_auto_rotate(prompt, openrouter_key)
