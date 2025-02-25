from pathlib import Path
from typing import List, Optional
import os

def list_files_in_tools_folder(caller_id: str, _: str) -> str:
    """List all files in the tools directory.

    Returns:
        String containing list of relative paths to files, joined by §
    """
    base_path = Path(__file__).parent
    result = []
    for root, _, files in os.walk(base_path):
        for file in files:
            full_path = Path(root) / file
            result.append(str(full_path.relative_to(base_path)))
    return '§'.join(result)
