import os

def read_readme(_: str) -> str:
    """Read the README.md file from the project root directory and return its contents."""

    try:
        # Get project root directory (two levels up from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        readme_path = os.path.join(project_root, 'README.md')
        if os.path.isfile(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                return f.read()

        return f"README.md not found in project root: {project_root}"

    except Exception as e:
        return f"Error reading README: {str(e)}"
