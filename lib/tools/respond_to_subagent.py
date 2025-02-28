from pathlib import Path
import re

def respond_to_subagent(caller_id: str, input_str: str) -> str:
    """Write a message to a subagent's chat file to respond to them.

    Args:
        caller_id (str): The ID of the caller
        input_str (str): String in format 'agent_id§message'

    Returns:
        str: Empty string on success

    Raises:
        ValueError: If input format is invalid
        IOError: If writing to chat file fails
    """
    # Use regex to match the format 'agent_id§message' with a non-greedy approach
    # This is more robust than splitting on '§' which can fail if the message itself contains '§'
    # or if there are formatting issues with newlines, invisible characters, etc.
    match = re.match(r'^([^§]+)§([\s\S]*)$', input_str.strip())
    if not match:
        raise ValueError("Input must be in format 'agent_id§message'")

    agent_id, message = match.groups()

    chats_dir = Path(__file__).parent.parent.parent / 'chats'
    chats_dir.mkdir(exist_ok=True)

    # Write to caller_to_agent chat file
    try:
        chat_file = chats_dir / f"{caller_id}_to_{agent_id}.txt"
        with open(chat_file, 'a') as f:
            f.write(f"[{caller_id}] {message}\n")
        return ""
    except IOError as e:
        raise IOError(f"Failed to write to chat file: {str(e)}")
