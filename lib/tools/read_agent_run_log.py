from pathlib import Path

def read_agent_run_log(caller_id: str, agent_name: str, log_file_name: str) -> str:
    """Read content of a run log file for a specific agent.

    Args:
        agent_name: Name of the agent whose run log to read
        log_file_name: Name of the log file to read

    Returns:
        Content of the log file

    Raises:
        ValueError: If path tries to escape runs directory
        FileNotFoundError: If file doesn't exist
    """
    base_path = Path(__file__).parent.parent.parent / "runs" / agent_name
    full_path = (base_path / log_file_name).resolve()

    if not str(full_path).startswith(str(base_path)):
        raise ValueError(f"Path {log_file_name} attempts to escape runs/{agent_name} directory")

    if not full_path.exists():
        raise FileNotFoundError(f"Log file {log_file_name} for agent {agent_name} not found")

    with open(full_path, 'r') as f:
        return f.read()
