import os
import sys
from datetime import datetime
from typing import Optional, Tuple, Dict, Callable
from lib.base import Agent
import inspect
import re
import json

class SimulateScenarioAgent(Agent):
    """An agent that simulates responses for other target agents based on a scenario by providing human-like responses.

    This agent asks the user which target agent, and also which scenario to simulate, reads the target agent and scenario file.

    This agent will then ask the user for what the target agent's next question is, and then provide a response to that question.

    This agent will then repeat this process until the user indicates that the target agent has completed its task.

    """

    def __init__(self,
                 manifesto: str,
                 memory: str = ""):

        if not manifesto:
            raise ValueError("Manifesto must be provided")

        super().__init__(
            model_name="gpt-4o",
            manifesto=manifesto,
            memory=memory,
            tools={
                'GET_TARGET_AGENT': self._get_target_agent,
                'GET_SCENARIO': self._get_scenario,
                'GET_VARIABLES': self._get_variables,
                'GET_QUESTION': self._get_question,
                'ANSWER_QUESTION': self._answer_question
            },
            tool_detection=self._detect_tool,
            end_detection=self._end_detection
        )

        self.scenario_text = None
        self.target_agent_name = None
        self.target_agent_manifesto = None

        self.target_agent_context_loaded_in_memory = False

    def _get_target_agent(self, _: str = "") -> str:
        """Ask user for agent name and return the selected agent."""
        # Get list of available agents
        agents_dir = os.path.dirname(os.path.dirname(__file__))
        available_agents = []
        for item in os.listdir(agents_dir):
            if os.path.isdir(os.path.join(agents_dir, item)) and not item.startswith('__'):
                if os.path.exists(os.path.join(agents_dir, item, 'agent.py')):
                    available_agents.append(item)

        # Present available agents to user
        agent_list = ', '.join(available_agents)
        agent_name = self.ask_user(f"Which agent would you like me to simulate? Available agents: {agent_list}")

        if not agent_name:
            return "ERROR: No agent name provided"

        # Import the agent class
        try:
            import importlib.util
            agent_path = os.path.join(agents_dir, agent_name, "agent.py")
            spec = importlib.util.spec_from_file_location("agent_module", agent_path)
            if not spec or not spec.loader:
                return f"ERROR: Could not load agent module from {agent_path}"

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find the agent class (specific to this agent, not the base class)
            agent_class = None
            for attr in dir(module):
                if attr.endswith('Agent') and attr != 'Agent':
                    obj = getattr(module, attr)
                    if inspect.isclass(obj) and issubclass(obj, Agent):
                        agent_class = obj
                        break

            if not agent_class:
                return f"ERROR: Could not find agent class in {agent_path}"

            self.target_agent_name = agent_name
            return f"Successfully loaded {agent_name}"

        except Exception as e:
            return f"ERROR: Failed to load agent: {str(e)}"

    def _get_scenario(self, _: str = "") -> str:
        """Get the scenario file to simulate."""
        if not self.target_agent_name:
            return "ERROR: Must get target agent first"

        # Get scenarios directory
        agents_dir = os.path.dirname(os.path.dirname(__file__))
        scenarios_dir = os.path.join(agents_dir, self.target_agent_name, "scenarios")

        if not os.path.exists(scenarios_dir):
            return f"ERROR: No scenarios directory found at {scenarios_dir}"

        # List available scenarios
        scenarios = [f for f in os.listdir(scenarios_dir)]
        if not scenarios:
            return f"ERROR: No scenario files found in {scenarios_dir}"

        # Let user pick scenario
        scenario_list = ', '.join(scenarios)
        scenario_name = self.ask_user(f"Which scenario would you like to simulate? Available scenarios: {scenario_list}")

        if not scenario_name:
            return "ERROR: No scenario name provided"

        scenario_path = os.path.join(scenarios_dir, scenario_name)
        if not os.path.exists(scenario_path):
            return f"ERROR: Could not find scenario file at {scenario_path}"

        # Read scenario
        try:
            with open(scenario_path, 'r') as f:
                self.scenario_text = f.read()
            return f"Successfully loaded scenario from {scenario_path}, \n scenario text: {self.scenario_text}"
        except Exception as e:
            return f"ERROR: Failed to read scenario: {str(e)}"

    def _get_variables(self, _: str) -> str:
        """ look through the variables folder of the target agent for a file called manifesto.json
        (which is a json array) and return the length of that array. User then gets to pick which index.
        """
        # TODO: only selecting manifesto right now, might need to add other variables later on

        if not self.target_agent_name:
            return "ERROR: Must get target agent first"

        # Get variables directory
        agents_dir = os.path.dirname(os.path.dirname(__file__))
        variables_dir = os.path.join(agents_dir, self.target_agent_name, "variables")

        if not os.path.exists(variables_dir):
            return f"ERROR: No variables directory found at {variables_dir}"

        # Each variable in variables folder is a json file which is always a json array of strings
        # List available indexs (0 to [length of array])
        # Use manifesto.json
        manifesto_path = os.path.join(variables_dir, "manifesto.json")
        if not os.path.exists(manifesto_path):
            return f"ERROR: Could not find manifesto file at {manifesto_path}"

        # Read manifesto
        try:
            with open(manifesto_path, 'r') as f:
                manifesto = json.load(f)
        except Exception as e:
            return f"ERROR: Failed to read manifesto: {str(e)}"

        manifesto_length = len(manifesto)
        if manifesto_length == 0:
            return f"ERROR: Manifesto at {manifesto_path} is empty"

        # Let user pick index, (0 to [length of array - 1])
        selected_index = self.ask_user(f"Which index would you like to use? Available indexs: 0 to {manifesto_length - 1}")

        # Get selected index
        if not selected_index:
            return "ERROR: No index provided"
        selected_index = int(selected_index)
        selected_manifesto = manifesto[selected_index]
        self.target_agent_manifesto = selected_manifesto

        return f"Successfully loaded variables from {manifesto_path}, \n selected index: {selected_index}, \n selected manifesto: {selected_manifesto}"

    def _get_question(self, _: str = "") -> str:
        """Get the next question from the target agent. Assume that it is passed in by the user."""
        if not self.target_agent_name:
            return "ERROR: Must get target agent first"

        question = self.ask_user(f"Please provide the next question for {self.target_agent_name}")
        return question

    def _answer_question(self, answer: str) -> str:
        """Answer the question using the target agent."""
        if not self.target_agent_name:
            return "ERROR: Must get target agent first"

        self.tell_user(f"Answering question for {self.target_agent_name}: {answer}")
        return ""


    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect which tool to call based on the agent's response."""
        pattern = r'<TOOL: (GET_TARGET_AGENT|GET_SCENARIO|GET_VARIABLES|GET_QUESTION|ANSWER_QUESTION)>([^<]*)</TOOL>'
        if match := re.search(pattern, text):
            return match.group(1), match.group(2)
        return None, None

    def _end_detection(self, manifesto: str, memory: str) -> bool:
        """End when simulation is complete."""
        return "<SIMULATION_COMPLETED>" in memory
