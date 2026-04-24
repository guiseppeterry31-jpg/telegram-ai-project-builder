import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_error(error_msg):
    """Log error messages"""
    logger.error(error_msg)

def handle_api_error(e):
    """Handle API-related errors"""
    log_error(f"API Error: {e}")
    return f"Failed to call API: {e}"

def handle_json_error(e):
    """Handle JSON parsing errors"""
    log_error(f"JSON Error: {e}")
    return f"Failed to parse project JSON: {e}"
