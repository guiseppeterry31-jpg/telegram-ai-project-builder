import json
import re

def parse_project_json(raw_response):
    """Safely parse and validate project JSON from model response"""
    # Extract JSON from response (handle extra text around JSON)
    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON found in model response")
    json_str = json_match.group(0)
    try:
        project_data = json.loads(json_str)
        # Validate required fields
        required_fields = ["project_name", "description", "files"]
        for field in required_fields:
            if field not in project_data:
                raise ValueError(f"Missing required field: {field}")
        if not isinstance(project_data["files"], list):
            raise ValueError("'files' must be a list")
        for file in project_data["files"]:
            if "path" not in file or "content" not in file:
                raise ValueError("Each file must have 'path' and 'content'")
        return project_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
