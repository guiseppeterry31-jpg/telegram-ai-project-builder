import os
import shutil
from utils.json_parser import parse_project_json
from utils.file_builder import build_project_files
from utils.zip_exporter import create_zip

GENERATED_PROJECTS_DIR = "generated_projects"

def generate_project(raw_model_response):
    """Parse model response, build project files, create ZIP"""
    # Ensure generated projects directory exists
    os.makedirs(GENERATED_PROJECTS_DIR, exist_ok=True)
    try:
        # Parse and validate project JSON
        project_data = parse_project_json(raw_model_response)
        project_name = project_data["project_name"]
        description = project_data["description"]
        files = project_data["files"]

        # Create project directory (clean up existing)
        project_dir = os.path.join(GENERATED_PROJECTS_DIR, project_name)
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        
        # Build all project files
        build_project_files(project_dir, files)
        
        # Create ZIP archive
        zip_path = os.path.join(GENERATED_PROJECTS_DIR, f"{project_name}.zip")
        create_zip(project_dir, zip_path)
        
        return {
            "project_name": project_name,
            "description": description,
            "project_dir": project_dir,
            "zip_path": zip_path
        }
    except Exception as e:
        raise Exception(f"Project generation failed: {e}")
