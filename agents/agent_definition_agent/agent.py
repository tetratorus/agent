from typing import Dict, Optional, Tuple, Callable
import os
from lib.base import Agent
import re

class AgentDefinitionAgent(Agent):
    """Agent that gathers requirements for new agents by reading framework docs and asking targeted questions."""

    def __init__(self,
                 manifesto: str,
                 memory: str = "",
    ):
        if manifesto is None:
            raise ValueError("Manifesto must be provided")

        # Initialize tools
        tools = {
            'READ_README': self._read_readme,
            'READ_BASE_AGENT': self._read_base_agent,
        }

        super().__init__(
            model_name="openai/gpt-4o",
            tools=tools,
            tool_detection=self._detect_tool,
            manifesto=manifesto,
            memory=memory
        )

    def _read_readme(self, _: str) -> str:
        """Read the framework README file."""
        readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "README.md")
        with open(readme_path, 'r') as f:
            return f.read()

    def _read_base_agent(self, _: str) -> str:
        """Read the base agent implementation file."""
        base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "lib", "base.py")
        with open(base_path, 'r') as f:
            return f.read()

    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect tool calls in the agent's response using regex pattern matching."""
        pattern = r'<TOOL: ([A-Z_]+)>([\s\S]*?)</TOOL>'
        match = re.search(pattern, text)
        if match:
            return match.group(1), match.group(2).strip()
        return None, None
