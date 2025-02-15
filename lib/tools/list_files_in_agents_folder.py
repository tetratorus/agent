from pathlib import Path
from typing import List, Optional
import os

def get_agents_base_path() -> Path:
    return Path(__file__).parent.parent.parent / "agents"

def list_files_in_agents_folder(_: str) -> str:
    """List all files in the agents folder.

    Args:
        _: Unused, but required for tool format compliance

    Returns:
        String containing list of relative paths to files, joined by §
    """
    base_path = get_agents_base_path()
    result = []
    for root, _, files in os.walk(base_path):
        for file in files:
            full_path = Path(root) / file
            result.append(str(full_path.relative_to(base_path)))
    return '§'.join(result)
