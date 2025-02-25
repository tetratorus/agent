from pathlib import Path

def read_file_in_agents_superfolder(caller_id: str, file_path: str) -> str:
    """Read content in a file within the agents superfolder.

    Args:
        file_path: Path relative to the agents directory

    Returns:
        Content of the file

    Raises:
        ValueError: If path tries to escape agents directory
        FileNotFoundError: If file doesn't exist
    """
    base_path = Path(__file__).parent.parent.parent / "agents"
    full_path = (base_path / file_path).resolve()

    if not str(full_path).startswith(str(base_path)):
        raise ValueError(f"Path {file_path} attempts to escape agents directory")

    with open(full_path, 'r') as f:
        return f.read()
