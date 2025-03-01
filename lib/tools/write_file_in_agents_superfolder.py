from pathlib import Path
import os

def write_file_in_agents_superfolder(caller_id: str, input_str: str) -> str:
    """Write content in a file within the agents superfolder.

    Args:
        input_str: String in format 'file_path§content'

    Returns:
        Empty string on success

    Raises:
        ValueError: If path tries to escape agents directory or input format is invalid
    """
    # Split on the first occurrence of § only
    # This ensures we correctly handle cases where the content itself contains §
    parts = input_str.split('§', 1)
    if len(parts) != 2:
        raise ValueError("Input must be in format 'file_path§content'")

    file_path, content = parts

    base_path = Path(__file__).parent.parent.parent / "agents"
    full_path = (base_path / file_path).resolve()

    if not str(full_path).startswith(str(base_path)):
        raise ValueError(f"Path {file_path} attempts to escape agents directory")

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)

    return ''
