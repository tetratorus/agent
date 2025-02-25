from pathlib import Path

def read_file_in_tools_folder(caller_id: str, file_path: str) -> str:
    """Read content in a file within the tools directory.

    Args:
        file_path: Path relative to the tools directory

    Returns:
        Content of the file

    Raises:
        ValueError: If path tries to escape tools directory
        FileNotFoundError: If file doesn't exist
    """
    base_path = Path(__file__).parent
    full_path = (base_path / file_path).resolve()

    if not str(full_path).startswith(str(base_path)):
        raise ValueError(f"Path {file_path} attempts to escape tools directory")

    with open(full_path, 'r') as f:
        return f.read()
