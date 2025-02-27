from pathlib import Path

def read_file_in_scenarios_folder(caller_id: str, input_str: str) -> str:
    """Read content in a file within the scenarios directory.

    Args:
        input_str: String in format 'agent_name§file_path'
                   agent_name must match an existing agent subfolder in agents/
                   file_path is relative to the scenarios/agent_name directory

    Returns:
        Content of the file

    Raises:
        ValueError: If path tries to escape scenarios directory, input format is invalid,
                   or agent_name doesn't match an existing agent subfolder
        FileNotFoundError: If file doesn't exist
    """
    parts = input_str.split('§')
    if len(parts) != 2:
        raise ValueError("Input must be in format 'agent_name§file_path'")

    agent_name, file_path = parts

    # Check if agent exists in agents directory
    agents_dir = Path(__file__).parent.parent.parent / "agents"
    if not (agents_dir / agent_name).exists() or not (agents_dir / agent_name).is_dir():
        raise ValueError(f"Agent '{agent_name}' does not exist in agents directory")

    # Set up scenarios/agent_name directory
    base_path = Path(__file__).parent.parent.parent / "scenarios" / agent_name
    full_path = (base_path / file_path).resolve()

    if not str(full_path).startswith(str(base_path)):
        raise ValueError(f"Path {file_path} attempts to escape scenarios/{agent_name} directory")

    with open(full_path, 'r') as f:
        return f.read()
