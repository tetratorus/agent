from pathlib import Path
import time
import hashlib

# Store last content hash per caller_id:agent_id pair
_last_content_hash = {}

def listen_to_all_subagents(caller_id: str) -> str:
    global _last_content_hash
    """Listen to incoming messages from subagents, blocks until new content is available.

    Gets all agents by looking at the chats folder and filtering for _to_{caller_id}.txt files.

    Returns:
        str: String with format "agent_id§content"

    Raises:
        FileNotFoundError: If no messages found from specified agent(s)
        TimeoutError: If no new messages after 5 minutes
    """
    chats_dir = Path(__file__).parent.parent.parent / 'chats'

    # Keep checking for new content from any agent
    start_time = time.time()
    while True:
        # Check all chat files in each iteration
        chat_files = list(chats_dir.glob(f'*_to_{caller_id}.txt'))

        if not chat_files:
            raise FileNotFoundError(f"No subagents found for caller {caller_id}")

        for chat_file in chat_files:
            # Extract agent_id from filename
            agent_id = chat_file.name.split(f'_to_{caller_id}.txt')[0]

            # Check if content has changed
            current_content = chat_file.read_text()
            current_hash = hashlib.sha256(current_content.encode()).hexdigest()
            caller_key = f"{caller_id}:{agent_id}"
            last_hash = _last_content_hash.get(caller_key)

            if last_hash is None or current_hash != last_hash:
                # Update the hash for this agent
                _last_content_hash[caller_key] = current_hash

                # Return immediately when a new message is found
                return f"{agent_id}§{current_content}"

        if time.time() - start_time > 300:  # 5 minute timeout
            raise TimeoutError("No new messages found from any agent, feel free to call this function again to await new messages")

        time.sleep(5)  # Sleep for 5 seconds between checks
