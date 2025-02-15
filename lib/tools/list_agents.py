from pathlib import Path
from typing import List

def get_agents_path() -> Path:
    return Path(__file__).parent.parent.parent / "agents"

def list_agents(input_str: str = '') -> str:
    """List all available agents in the agents directory.
    
    Args:
        input_str: Unused, but required for tool format compliance
    
    Returns:
        String containing list of agent names (directory names in the agents folder)
    """
    agents_path = get_agents_path()
    agents = [d.name for d in agents_path.iterdir() if d.is_dir()]
    return '§'.join(agents)
