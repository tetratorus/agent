import os
import sys
from typing import Dict, Optional, Callable, Tuple
from lib.base import Agent

class ToolGenerationAgent(Agent):
    """An agent that generates tool implementations in a standardized directory structure.
    
    Creates new tools in tools/<tool_name>/ directories with:
    - <tool_name>.py for implementation
    - test/test_<tool_name>.py for unit tests
    """

    def __init__(self, manifesto: str = "", memory: str = ""):
        if not manifesto:
            with open(os.path.join(os.path.dirname(__file__), "variables", "manifesto.json")) as f:
                manifesto = f.read()

        super().__init__(
            model_name="claude-3-5-sonnet-20240620",
            manifesto=manifesto,
            memory=memory,
            tools={
                "CREATE_DIRECTORY": self._create_directory,
                "WRITE_FILE": self._write_file,
                "CHECK_PATH_EXISTS": self._check_path_exists,
                "GET_USER_INPUT": self._get_user_input
            },
            tool_detection=self._detect_tool
        )

    def _create_directory(self, path: str) -> str:
        """Create a directory and its parents if they don't exist."""
        try:
            os.makedirs(path, exist_ok=True)
            return f"Created directory: {path}"
        except Exception as e:
            return f"Error creating directory {path}: {str(e)}"

    def _write_file(self, args: str) -> str:
        """Write content to a file, creating parent directories if needed."""
        try:
            path, content = args.split("|||", 1)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return f"Wrote file: {path}"
        except Exception as e:
            return f"Error writing file {path}: {str(e)}"

    def _check_path_exists(self, path: str) -> str:
        """Check if a path exists."""
        return str(os.path.exists(path))

    def _get_user_input(self, prompt: str) -> str:
        """Get input from the user with a prompt."""
        try:
            print(prompt, end=" ")
            sys.stdout.flush()
            return input().strip()
        except Exception as e:
            return f"Error getting user input: {str(e)}"

    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect tool calls in the LLM's response."""
        lines = text.split("\n")
        for line in lines:
            if line.startswith("CREATE_DIRECTORY:"):
                return "CREATE_DIRECTORY", line.split(":", 1)[1].strip()
            elif line.startswith("WRITE_FILE:"):
                return "WRITE_FILE", line.split(":", 1)[1].strip()
            elif line.startswith("CHECK_PATH_EXISTS:"):
                return "CHECK_PATH_EXISTS", line.split(":", 1)[1].strip()
            elif line.startswith("GET_USER_INPUT:"):
                return "GET_USER_INPUT", line.split(":", 1)[1].strip()
        return None, None
