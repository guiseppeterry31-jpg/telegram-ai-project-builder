import shutil
import os

def create_zip(project_dir, output_zip_path):
    """Compress project directory into a ZIP file"""
    if not output_zip_path.endswith(".zip"):
        output_zip_path += ".zip"
    base_name = output_zip_path[:-4]  # Remove .zip extension
    # Remove existing zip if it exists
    if os.path.exists(output_zip_path):
        os.remove(output_zip_path)
    shutil.make_archive(base_name, "zip", project_dir)
    return output_zip_path
