import os
import sys
from datetime import datetime
from typing import Optional, Tuple, Dict, Callable
from lib.base import Agent
from lib.debug import debug
import inspect
import re
import json

class SimulateScenarioAgent(Agent):
    """An agent that simulates scenarios for other agents.

    This agent asks the user which target agent, and also which scenario to simulate, reads the target agent and scenario file.
    This agent then runs the target agent, overriding ask_user where necessary and responding to the target agent based on the scenario.
    """

    @debug()
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
                'RUN_SIMULATION': self._run_simulation,
            },
            tool_detection=self._detect_tool,
            end_detection=self._end_detection
        )

        self.scenario_text = None
        self.target_agent = None
        self.target_agent_name = None
        self.target_agent_manifesto = None

    @debug()
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

            self.target_agent = agent_class
            self.target_agent_name = agent_name
            return f"Successfully loaded {agent_name}"

        except Exception as e:
            return f"ERROR: Failed to load agent: {str(e)}"

    @debug()
    def _get_scenario(self, _: str = "") -> str:
        """Get the scenario file to simulate."""
        if not self.target_agent:
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
    @debug()
    def _get_variables(self, _: str) -> str:
        """ look through the variables folder of the target agent for a file called manifesto.json
        (which is a json array) and return the length of that array. User then gets to pick which index.
        """
        # TODO: only selecting manifesto right now, might need to add other variables later on

        if not self.target_agent:
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

        # Let user pick index, (1 to [length of array])
        selected_index = self.ask_user(f"Which index would you like to use? Available indexs: 1 to {manifesto_length}")

        # Get selected index
        if not selected_index:
            return "ERROR: No index provided"
        selected_index = int(selected_index)
        selected_manifesto = manifesto[selected_index - 1]
        self.target_agent_manifesto = selected_manifesto

        return f"Successfully loaded variables from {manifesto_path}, \n selected index: {selected_index}, \n selected manifesto: {selected_manifesto}"

    @debug()
    def _run_simulation(self, _: str = "") -> str:
        """Run the simulation with the selected agent and scenario."""
        if not self.target_agent:
            return "ERROR: Must get target agent first"
        if not self.scenario_text:
            return "ERROR: Must get scenario first"
        if not self.target_agent_manifesto:
            return "ERROR: Must get variables first"

        try:
            # Create agent instance
            agent = self.target_agent(manifesto=self.target_agent_manifesto)

            # Override ask_user to use LLM
            @debug()
            def simulated_ask_user(question: str) -> str:
                # Update memory with question
                self.update_memory(self.memory + "\nQuestion: " + question)

                # Generate response using LLM based only on scenario
                prompt = f"You are simulating what a user might respond to the target agent, {self.target_agent_name}, according to this scenario:\n{self.scenario_text}\n\nThe user is asked: {question}\n\nRespond as this user would:"
                response = self.llm_call(prompt)

                # Update memory with response
                self.update_memory(self.memory + "\n Response: " + response)
                return response

            agent.override_ask_user(simulated_ask_user)

            # Run the agent
            result = agent.run()
            return f"<SIMULATION_COMPLETED>. Agent output:\n{result}"

        except Exception as e:
            return f"ERROR: Simulation failed: {str(e)}"

    @debug()
    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect which tool to call based on the agent's response."""
        pattern = r'<TOOL: (GET_TARGET_AGENT|GET_SCENARIO|GET_VARIABLES|RUN_SIMULATION)>([^<]*)</TOOL>'
        if match := re.search(pattern, text):
            return match.group(1), match.group(2)
        return None, None

    @debug()
    def _end_detection(self, manifesto: str, memory: str) -> bool:
        """End when simulation is complete."""
        return "<SIMULATION_COMPLETED>" in memory
