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
    # Split on the first occurrence of § only
    # This ensures we correctly handle cases where the message itself contains §
    parts = input_str.split('§', 1)
    if len(parts) != 2:
        raise ValueError("Input must be in format 'agent_id§message'")

    agent_id, message = parts

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
