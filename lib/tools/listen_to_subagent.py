from pathlib import Path
import time
import hashlib

# Store last content hash per caller_id
_last_content_hash = {}

def listen_to_subagent(caller_id: str, agent_id: str) -> str:
    """Listen to incoming messages from an agent's chat file
    If the caller_id has read this file before, blocks until new content is available.

    Args:
        caller_id (str): The ID of the caller
        agent_id (str): The ID of the agent to read messages from

    Returns:
        str: The content of the chat file
    """

    chats_dir = Path(__file__).parent.parent.parent / 'chats'
    chat_path = chats_dir / f"{agent_id}_to_{caller_id}.txt"

    if not chat_path.exists():
        raise FileNotFoundError(f"No messages found from agent {agent_id}")

    caller_key = f"{caller_id}:{agent_id}"
    last_content = _last_content_hash.get(caller_key)

    # Keep checking for new content if we've seen this content before
    start_time = time.time()
    while True:
        current_content = chat_path.read_text()
        current_hash = hashlib.sha256(current_content.encode()).hexdigest()
        if last_content is None or current_hash != last_content:
            _last_content_hash[caller_key] = current_hash
            return current_content

        if time.time() - start_time > 300:  # 5 minute timeout
            raise TimeoutError("No new messages found, feel free to call this function again to await new messages")

        time.sleep(5)  # Sleep for 5 seconds between checks
