import os
import json
import re
from typing import Dict, Optional, Tuple, Any
from lib.base import Agent
from lib.debug import debug

class VariableGenerationAgent(Agent):
    """Agent that generates variations of another agent's variables.

    Given a target agent's code and variables, analyzes its purpose and generates
    variations of its variables.

    Args:
        manifesto: Custom instructions for the agent
        target_agent: Name of the agent to generate variations for
        memory: Initial memory/context for the conversation
    """

    @debug()
    def __init__(
        self,
        manifesto: str,
        target_agent: str,
        memory: str = "",
    ):
        if manifesto is None:
            raise ValueError("Manifesto must be provided")
        if target_agent is None:
            raise ValueError("Target agent must be provided")

        model_name = "gpt-4o"

        # Set agent_dir first
        self.target_agent = target_agent
        self.agent_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), target_agent)

        # Read core files after agent_dir is set
        readme_content = self._read_readme("")
        base_content = self._read_base("")
        agent_content = self._read_agent("")

        # Add file contents to initial memory
        initial_memory = f"""Target Agent: {target_agent}

Core Files Read:
1. README.md:
{readme_content}

2. base.py:
{base_content}

3. {target_agent}/agent.py:
{agent_content}
"""

        super().__init__(
            model_name=model_name,
            manifesto=manifesto,
            memory=initial_memory,
            tools={
                "list_variables": self._list_variables,
                "add_variation": self.add_variation,
                "ask_user": self.ask_user,
                "copy_last_entry": self.copy_last_entry
            },
            tool_detection=self._detect_tool,
            end_detection=self._end_detection
        )

    @debug()
    def ask_user(self, question: str) -> str:
        """Ask the user a question and get their response."""
        return input(question + "\nYour response: ")

    @debug()
    def _read_file(self, path: str) -> str:
        """Read a file's contents."""
        try:
            # Handle paths relative to variables directory
            if path.startswith('variables/'):
                path = os.path.join(self.agent_dir, path)
            else:
                path = os.path.join(self.agent_dir, "variables", path)

            if not os.path.exists(path):
                return f"Error: File not found: {path}"

            with open(path) as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @debug()
    def _list_files(self, _: str = "") -> str:
        """List all files in the target agent's directory."""
        try:
            if not os.path.exists(self.agent_dir):
                return f"Error: Agent directory not found: {self.agent_dir}"

            files = []
            for root, dirs, filenames in os.walk(self.agent_dir):
                rel_path = os.path.relpath(root, self.agent_dir)
                if rel_path == ".":
                    prefix = ""
                else:
                    prefix = rel_path + "/"

                for d in sorted(dirs):
                    files.append(prefix + d + "/")
                for f in sorted(filenames):
                    files.append(prefix + f)

            return "\n".join(files) if files else "No files found"
        except Exception as e:
            return f"Error listing files: {str(e)}"

    @debug()
    def _list_variables(self, _: str = "") -> str:
        """List all variable files in the variables directory."""
        try:
            var_dir = os.path.join(self.agent_dir, "variables")
            if not os.path.exists(var_dir):
                return f"Error: Variables directory not found: {var_dir}"

            files = []
            for f in sorted(os.listdir(var_dir)):
                if f.endswith('.json'):
                    files.append(f"variables/{f}")

            return "\n".join(files) if files else "No variable files found"
        except Exception as e:
            return f"Error listing variables: {str(e)}"

    @debug()
    def add_variation(self, variable_and_content: str) -> str:
        """Add a variation for a variable file."""
        # Split the input into variable name and content
        try:
            variable, content = variable_and_content.split("\n", 1)
        except ValueError:
            return "Error: Input must contain a newline to separate variable name and content"

        # Append .json if not already present
        if not variable.endswith(".json"):
            variable += ".json"
        target_path = os.path.join(self.agent_dir, "variables", variable)

        try:
            with open(target_path, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return "Error reading variable file"

        # Add new content to list
        data.append(content)

        # Write back to file
        with open(target_path, "w") as f:
            json.dump(data, f, indent=2)

        return "Successfully added variation"

    @debug()
    def copy_last_entry(self, variable: str) -> str:
        """Copy the last entry from a variable file."""
        # Append .json if not already present
        if not variable.endswith(".json"):
            variable += ".json"
        target_path = os.path.join(self.agent_dir, "variables", variable)

        try:
            with open(target_path, "r") as f:
                data = json.load(f)

            # Get last non-empty entry if exists
            last_entry = next((x for x in reversed(data) if x), "") if data else ""
            data.append(last_entry)

            # Write back
            with open(target_path, "w") as f:
                json.dump(data, f, indent=2)

            return "Successfully copied last entry"
        except Exception as e:
            return f"Error copying last entry: {str(e)}"

    @debug()
    def _read_readme(self, _: str = "") -> str:
        """Read the README.md file from root directory."""
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            path = os.path.join(root_dir, "README.md")
            if not os.path.exists(path):
                return f"Error: README.md not found at {path}"
            with open(path) as f:
                return f.read()
        except Exception as e:
            return f"Error reading README.md: {str(e)}"

    @debug()
    def _read_base(self, _: str = "") -> str:
        """Read the base.py file from lib directory."""
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            path = os.path.join(root_dir, "lib", "base.py")
            if not os.path.exists(path):
                return f"Error: base.py not found at {path}"
            with open(path) as f:
                return f.read()
        except Exception as e:
            return f"Error reading base.py: {str(e)}"

    @debug()
    def _read_agent(self, _: str = "") -> str:
        """Read the agent.py file from target agent's directory."""
        try:
            path = os.path.join(self.agent_dir, "agent.py")
            if not os.path.exists(path):
                return f"Error: agent.py not found at {path}"
            with open(path) as f:
                return f.read()
        except Exception as e:
            return f"Error reading agent.py: {str(e)}"

    @debug()
    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect tool calls in the agent's response."""
        pattern = r'<VAR_GEN_TOOL: ([A-Z_]+)>(.*?)</VAR_GEN_TOOL>'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            tool_name = match.group(1).lower()
            tool_input = match.group(2).strip()
            return tool_name, tool_input
        return None, None

    @debug()
    def _end_detection(self, manifesto: str, memory: str) -> bool:
        if "<VAR_GEN_COMPLETED>" in memory:
            return True
        else:
            return False
