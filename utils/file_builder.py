import os

def build_project_files(base_dir, files):
    """Create project folders and write all files dynamically"""
    os.makedirs(base_dir, exist_ok=True)
    created_paths = []
    for file in files:
        file_path = os.path.join(base_dir, file["path"])
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Write file content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file["content"])
        created_paths.append(file_path)
    return created_paths
