from lib.base import Agent
import os

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
                 memory: str):

        if manifesto is None:
            raise ValueError("Manifesto must be provided")

        model_name = "openai/gpt-4o"

        super().__init__(
            model_name=model_name,
            manifesto=manifesto,
            memory=memory,
            tools={
                "GET_AGENT_DESCRIPTION": self.get_agent_description,
                "READ_README": self._read_readme,
                "READ_BASE_AGENT": self._read_base_agent,
                "READ_META": self._read_meta,
            },
        )

    def get_agent_description(self, _: str) -> str:
        """ use ASK_USER tool to get the agent description from the user """
        return self.ask_user("What is the agent description?")

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

    def _read_meta(self, _: str) -> str:
        """Read the meta implementation file."""
        meta_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "lib", "meta.py")
        with open(meta_path, 'r') as f:
            return f.read()
