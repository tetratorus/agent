import time
import secrets
from pathlib import Path


def create_chat(caller_id: str, _: str) -> str:
    """Create a new chat file in the /chats directory with a unique filename.

    Returns:
        str: The path to the created chat file
    """
    timestamp = str(int(time.time() * 1000000))
    random_hex = secrets.token_hex(4)
    chatfile = f"{timestamp}_{random_hex}"

    chats_dir = Path(__file__).parent / 'chats'
    chats_dir.mkdir(exist_ok=True)

    chat_path = chats_dir / chatfile
    chat_path.touch()

    return str(chatfile)
