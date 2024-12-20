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

    def _write_file(self, args: Tuple[str, str]) -> str:
        """Write content to a file, creating parent directories if needed."""
        try:
            path, content = args
            if not path or not content:
                return "Error: Both path and content must be provided"

            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding='utf-8') as f:
                f.write(content)
            
            # Verify the file was written correctly
            if not os.path.exists(path):
                return f"Error: File {path} was not created"
                
            with open(path, 'r', encoding='utf-8') as f:
                written_content = f.read()
                if written_content.strip() != content.strip():
                    return f"Error: File {path} content verification failed"
                    
            return f"Wrote file: {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

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
        current_tool = None
        current_path = None
        current_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Handle single-line tool calls
            if line.startswith(("CREATE_DIRECTORY:", "CHECK_PATH_EXISTS:", "GET_USER_INPUT:")):
                if current_tool == "WRITE_FILE" and current_path and current_content:
                    # Found a new tool call, return the previous WRITE_FILE
                    return "WRITE_FILE", (current_path, "\n".join(current_content))
                    
                tool, args = line.split(":", 1)
                return tool, args.strip()
                
            # Start of a WRITE_FILE block
            elif line.startswith("WRITE_FILE:"):
                if current_tool == "WRITE_FILE" and current_path and current_content:
                    # Found a new WRITE_FILE, return the previous one
                    return "WRITE_FILE", (current_path, "\n".join(current_content))
                    
                current_tool = "WRITE_FILE"
                current_path = line.split(":", 1)[1].strip()
                current_content = []
                
            # Content lines for WRITE_FILE
            elif current_tool == "WRITE_FILE" and current_path:
                current_content.append(line)
        
        # Return final WRITE_FILE if we were building one
        if current_tool == "WRITE_FILE" and current_path and current_content:
            return "WRITE_FILE", (current_path, "\n".join(current_content))
            
        return None, None
