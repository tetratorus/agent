import os
from pathlib import Path

def display_directory_tree(_: str) -> str:
    """Display the directory tree of the project."""
    project_root = Path(__file__).parent.parent.parent
    result = []
    
    def add_directory(directory: Path, prefix: str = ""):
        files = sorted(directory.iterdir())
        for i, path in enumerate(files):
            is_last = i == len(files) - 1
            result.append(f"{prefix}{'└── ' if is_last else '├── '}{path.name}")
            if path.is_dir() and path.name != "__pycache__":
                add_directory(path, prefix + ("    " if is_last else "│   "))
    
    result.append(project_root.name)
    add_directory(project_root)
    return "\n".join(result)
