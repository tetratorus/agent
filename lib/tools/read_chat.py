from pathlib import Path
import time
import hashlib

# Store last content hash per caller_id
_last_content_hash = {}

def read_chat(caller_id: str, chatfile: str) -> str:
    """Read the content of a chat file from the /chats directory.
    If the caller_id has read this file before, blocks until new content is available.

    Args:
        caller_id (str): The ID of the caller
        chatfile (str): The name of the chat file to read

    Returns:
        str: The content of the chat file
    """
    chats_dir = Path(__file__).parent / 'chats'
    chat_path = chats_dir / chatfile

    if not chat_path.exists():
        raise FileNotFoundError(f"Chat file {chatfile} not found")

    caller_key = f"{caller_id}:{chatfile}"
    last_content = _last_read_content.get(caller_key)

    # Keep checking for new content if we've seen this content before
    start_time = time.time()
    while True:
        current_content = chat_path.read_text()
        current_hash = hashlib.sha256(current_content.encode()).hexdigest()
        if last_content is None or current_hash != last_content:
            _last_content_hash[caller_key] = current_hash
            return current_content

        if time.time() - start_time > 60:  # 1 minute timeout
            raise TimeoutError("No new messages found, feel free to call this function again to await new messages")

        time.sleep(5)  # Sleep for 5 seconds between checks
