import os
from datetime import datetime
from typing import Optional, Tuple
from lib.base import Agent
from lib.debug import debug

class ScenarioGenAgent(Agent):
    """An agent that generates test scenarios for other agents by analyzing their code.

    This agent asks the user which agent to generate a scenario for, reads that agent's code
    to understand its purpose and capabilities, then generates an appropriate test scenario.
    The scenario is saved as a text file in the target agent's scenarios/ directory.
    """

    @debug()
    def __init__(self,
                 manifesto: str,
                 memory: str = ""):

        if not manifesto:
            raise ValueError("Manifesto must be provided")

        # Initialize base agent with minimal tools
        super().__init__(
            model_name="gpt-4o",
            manifesto=manifesto,
            memory=memory,
            tools={
                'GET_TARGET_AGENT': self._get_target_agent,
                'READ_AGENT_INFO': self._read_agent_info,
                'SAVE_SCENARIO': self._save_scenario
            },
            tool_detection=self._detect_tool,
            end_detection=self._end_detection
        )

    @debug()
    def _get_target_agent(self, _: str = "") -> str:
        """Ask user for agent name and return the selected agent name."""
        # Get list of available agents
        agents_dir = os.path.dirname(os.path.dirname(__file__))
        available_agents = []
        for item in os.listdir(agents_dir):
            if os.path.isdir(os.path.join(agents_dir, item)) and not item.startswith('__'):
                if os.path.exists(os.path.join(agents_dir, item, 'agent.py')):
                    available_agents.append(item)

        # Present available agents to user
        agent_list = ', '.join(available_agents)
        agent_name = self.ask_user(f"Which agent would you like me to generate a scenario for? Available agents: {agent_list}")

        if not agent_name:
            return "ERROR: No agent name provided"

        # Construct path to agent.py
        agent_path = os.path.join(agents_dir, agent_name, "agent.py")
        if not os.path.exists(agent_path):
            return f"ERROR: Could not find agent.py at {agent_path}"

        return agent_name

    @debug()
    def _read_agent_info(self, agent_name: str) -> str:
        """read target agent code"""
        try:
            # Setup paths
            agents_dir = os.path.dirname(os.path.dirname(__file__))
            agent_path = os.path.join(agents_dir, agent_name, "agent.py")

            with open(agent_path, 'r') as f:
                content = f.read()

            # Look for a class that ends with 'Agent'
            import re
            class_match = re.search(r'class\s+(\w+Agent)', content)
            if not class_match:
                return f"ERROR: Could not find agent class in {agent_path}"

            agent_class = class_match.group(1)

            # Store these for later use when saving
            self.target_agent_path = agent_path
            self.target_agent_class = agent_class

            return content

        except Exception as e:
            return f"ERROR: Failed to read agent code: {str(e)}"

    @debug()
    def _save_scenario(self, scenario_text: str) -> str:
        """Save the generated scenario to a file."""
        try:
            # Get target agent directory
            target_dir = os.path.dirname(self.target_agent_path)
            scenarios_dir = os.path.join(target_dir, "scenarios")

            # Create scenarios directory if it doesn't exist
            os.makedirs(scenarios_dir, exist_ok=True)

            # Generate timestamp-based filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"scenario_{timestamp}"
            filepath = os.path.join(scenarios_dir, filename)

            # Save scenario
            with open(filepath, 'w') as f:
                f.write(scenario_text)

            return f"Successfully saved scenario to {filepath}"

        except Exception as e:
            return f"ERROR: Failed to save scenario: {str(e)}"

    @debug()
    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect which tool to call based on the agent's response."""
        if "<TOOL: GET_TARGET_AGENT>" in text:
            end_tag = "</TOOL>"
            end_idx = text.find(end_tag)
            if end_idx != -1:
                return "GET_TARGET_AGENT", ""
        elif "<TOOL: READ_AGENT_INFO>" in text:
            start = text.find("<TOOL: READ_AGENT_INFO>") + len("<TOOL: READ_AGENT_INFO>")
            end = text.find("</TOOL>", start)
            if start != -1 and end != -1:
                return "READ_AGENT_INFO", text[start:end].strip()
        elif "<TOOL: SAVE_SCENARIO>" in text:
            start = text.find("<TOOL: SAVE_SCENARIO>") + len("<TOOL: SAVE_SCENARIO>")
            end = text.find("</TOOL>")
            if start != -1 and end != -1:
                return "SAVE_SCENARIO", text[start:end].strip()
        return None, None

    @debug()
    def _end_detection(self, manifesto: str, memory: str) -> bool:
        """End when we see the scenario saved confirmation."""
        return "<TASK_COMPLETED>" in memory
