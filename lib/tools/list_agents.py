from pathlib import Path
from typing import List


def list_agents(caller_id: str,_: str = '') -> str:
    """List all available agents in the agents directory."""

    agents_path = Path(__file__).parent.parent.parent / "agents"
    agents = [d.name for d in agents_path.iterdir() if d.is_dir()]
    return '§'.join(agents)
