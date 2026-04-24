# In-memory store for user model selections
user_model_choices = {}

def get_user_model(user_id):
    """Get the selected model for a user, defaults to auto mode"""
    return user_model_choices.get(user_id, "auto")

def set_user_model(user_id, model_type):
    """Set the selected model for a user"""
    user_model_choices[user_id] = model_type
