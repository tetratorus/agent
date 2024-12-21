import sys
from typing import Optional

def ask_user(prompt: str, default: Optional[str] = None) -> str:
    """
    Get user input from the terminal.

    Args:
        prompt (str): The prompt to display to the user.
        default (Optional[str]): The default value if the user inputs nothing.

    Returns:
        str: The user's input or the default value if provided.

    Raises:
        EOFError: If the user closes the input stream (e.g., by pressing Ctrl+D).
    """
    try:
        if default is not None:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "

        user_input = input(full_prompt).strip()
        if not user_input and default is not None:
            return default
        return user_input
    except EOFError:
        print("\nInput stream closed. Exiting.", file=sys.stderr)
        raise