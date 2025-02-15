from pathlib import Path
from typing import List

def get_agents_path() -> Path:
    return Path(__file__).parent.parent.parent / "agents"

def list_agents(_: str = '') -> str:
    """List all available agents in the agents directory."""
    agents_path = get_agents_path()
    agents = [d.name for d in agents_path.iterdir() if d.is_dir()]
    return '§'.join(agents)
