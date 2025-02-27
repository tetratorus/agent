from pathlib import Path
import os

def write_scenario_in_scenarios_folder(caller_id: str, input_str: str) -> str:
    """Write content in a file within the scenarios directory.

    Args:
        input_str: String in format 'agent_name§file_path§content'
                   agent_name must match an existing agent subfolder in agents/
                   file_path is relative to the scenarios/agent_name directory

    Returns:
        Empty string on success

    Raises:
        ValueError: If path tries to escape scenarios directory, input format is invalid,
                   or agent_name doesn't match an existing agent subfolder
    """
    parts = input_str.split('§')
    if len(parts) != 3:
        raise ValueError("Input must be in format 'agent_name§file_path§content'")

    agent_name, file_path, content = parts

    # Check if agent exists in agents directory
    agents_dir = Path(__file__).parent.parent.parent / "agents"
    if not (agents_dir / agent_name).exists() or not (agents_dir / agent_name).is_dir():
        raise ValueError(f"Agent '{agent_name}' does not exist in agents directory")

    # Set up scenarios/agent_name directory
    base_path = Path(__file__).parent.parent.parent / "scenarios" / agent_name
    full_path = (base_path / file_path).resolve()

    if not str(full_path).startswith(str(base_path)):
        raise ValueError(f"Path {file_path} attempts to escape scenarios/{agent_name} directory")

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)

    return ''
