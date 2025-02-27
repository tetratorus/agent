from pathlib import Path
import os

def list_files_in_scenarios_folder(caller_id: str, agent_name: str) -> str:
    """List all files in the scenarios directory for a specific agent.

    Args:
        agent_name: Name of the agent subfolder to list files from
                   Must match an existing agent subfolder in agents/
                   If empty, lists all agent subfolders in scenarios/

    Returns:
        String containing list of relative paths to files, joined by §
        If agent_name is empty, returns list of agent subfolder names

    Raises:
        ValueError: If agent_name doesn't match an existing agent subfolder
    """
    scenarios_path = Path(__file__).parent.parent.parent / "scenarios"
    
    # If no agent name provided, list all agent subfolders in scenarios
    if not agent_name:
        # Create scenarios directory if it doesn't exist
        os.makedirs(scenarios_path, exist_ok=True)
        # List all directories in scenarios folder
        result = []
        if scenarios_path.exists():
            for item in scenarios_path.iterdir():
                if item.is_dir():
                    result.append(item.name)
        return '§'.join(result)
    
    # Check if agent exists in agents directory
    agents_dir = Path(__file__).parent.parent.parent / "agents"
    if not (agents_dir / agent_name).exists() or not (agents_dir / agent_name).is_dir():
        raise ValueError(f"Agent '{agent_name}' does not exist in agents directory")
    
    # List files in scenarios/agent_name directory
    base_path = scenarios_path / agent_name
    
    # Create the directory if it doesn't exist
    os.makedirs(base_path, exist_ok=True)
    
    result = []
    if base_path.exists():
        for root, _, files in os.walk(base_path):
            for file in files:
                full_path = Path(root) / file
                result.append(str(full_path.relative_to(base_path)))
    
    return '§'.join(result)
