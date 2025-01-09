from lib.base import Agent
import re
from typing import Dict, Optional, Callable, Tuple

class AgentImplementationAgent(Agent):
    """Agent that generates Python code for other AI agents based on descriptions.

    This agent takes in a description of an agent and generates the appropriate agent.py
    implementation based on the requirements.

    Args:
        manifesto: Custom instructions for the agent.
        memory: Initial memory/context for the conversation
    """

    def __init__(self,
                 manifesto: str,
                 memory: str = ""):

        if manifesto is None:
            raise ValueError("Manifesto must be provided")

        model_name = "openai/gpt-4o"

        super().__init__(
            model_name=model_name,
            manifesto=manifesto,
            memory=memory,
            tools={
                GET_AGENT_DESCRIPTION: lambda: self.get_agent_description(),
            },
            tool_detection=self._detect_tool,
        )

    def get_agent_description(self, _: str) -> str:
        """ use ASK_USER tool to get the agent description from the user """
        return self.ask_user("What is the agent description?")

    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect if there is a tool call in the text and return the tool name and input."""
        pattern = r'<TOOL: ([A-Z_]+)>([\s\S]*?)</TOOL>'
        match = re.search(pattern, text)
        if match:
            return match.group(1), match.group(2)
        return None, None
