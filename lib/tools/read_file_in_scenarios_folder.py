from pathlib import Path

def read_file_in_scenarios_folder(caller_id: str, file_path: str) -> str:
    """Read content in a file within the scenarios directory.

    Args:
        file_path: Path relative to the scenarios directory

    Returns:
        Content of the file

    Raises:
        ValueError: If path tries to escape scenarios directory
        FileNotFoundError: If file doesn't exist
    """
    base_path = Path(__file__).parent.parent.parent / "scenarios"
    full_path = (base_path / file_path).resolve()

    if not str(full_path).startswith(str(base_path)):
        raise ValueError(f"Path {file_path} attempts to escape scenarios directory")

    with open(full_path, 'r') as f:
        return f.read()
