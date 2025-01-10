from typing import Dict, Optional, Tuple, Callable
import os
from lib.base import Agent
import re

class AgentDefinitionAgent(Agent):
    """Agent that gathers requirements for new agents by reading framework docs and asking targeted questions."""

    def __init__(self,
                 manifesto: str,
                 memory: str):
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
