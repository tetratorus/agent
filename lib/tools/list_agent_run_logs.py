from pathlib import Path
from typing import List, Optional
import os

def list_agent_run_logs(caller_id: str, agent_name: str) -> str:
    """List all run log files for a specific agent.

    Args:
        agent_name: Name of the agent whose run logs to list

    Returns:
        String containing list of log file names, joined by §
    """
    base_path = Path(__file__).parent.parent.parent / "runs" / agent_name
    
    if not base_path.exists():
        return ""
    
    result = []
    for root, _, files in os.walk(base_path):
        for file in files:
            full_path = Path(root) / file
            result.append(str(full_path.relative_to(base_path)))
    
    result.sort()
    return '§'.join(result)
