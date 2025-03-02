from pathlib import Path
import time

# Store last content per caller_id
_last_content = {}

def listen_to_subagent(caller_id: str, agent_id: str) -> str:
    """Listen to incoming messages from an agent's chat file
    If the caller_id has read this file before, blocks until new content is available.

    Args:
        caller_id (str): The ID of the caller
        agent_id (str): The ID of the agent to read messages from

    Returns:
        str: The new content of the chat file (only the diff since last call)
    """

    chats_dir = Path(__file__).parent.parent.parent / 'chats'
    chat_path = chats_dir / f"{agent_id}_to_{caller_id}.txt"

    if not chat_path.exists():
        raise FileNotFoundError(f"No messages found from agent {agent_id}")

    caller_key = f"{caller_id}:{agent_id}"
    last_content = _last_content.get(caller_key)

    # Keep checking for new content if we've seen this content before
    start_time = time.time()
    while True:
        current_content = chat_path.read_text()
        if last_content is None:
            # First time reading, return all content
            _last_content[caller_key] = current_content
            return current_content
        elif current_content != last_content:
            # Return only the new content (diff)
            new_content = current_content[len(last_content):].strip()
            _last_content[caller_key] = current_content
            return new_content

        if time.time() - start_time > 300:  # 5 minute timeout
            raise TimeoutError("No new messages found, feel free to call this function again to await new messages")

        time.sleep(5)  # Sleep for 5 seconds between checks
