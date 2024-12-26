import os
from datetime import datetime
from typing import Optional, Tuple, Dict, Callable
from lib.base import Agent
from lib.debug import debug

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
                'RUN_SIMULATION': self._run_simulation
            },
            tool_detection=self._detect_tool,
            end_detection=self._end_detection
        )

        self.target_agent = None
        self.scenario_text = None

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

            # Find the agent class (ends with 'Agent')
            agent_class = None
            for attr in dir(module):
                if attr.endswith('Agent'):
                    agent_class = getattr(module, attr)
                    break

            if not agent_class:
                return f"ERROR: Could not find agent class in {agent_path}"

            self.target_agent = agent_class
            return f"Successfully loaded {agent_name}"

        except Exception as e:
            return f"ERROR: Failed to load agent: {str(e)}"

    @debug()
    def _get_scenario(self, _: str = "") -> str:
        """Get the scenario file to simulate."""
        if not self.target_agent:
            return "ERROR: Must get target agent first"

        # Get scenarios directory
        agent_dir = os.path.dirname(self.target_agent.__file__)
        scenarios_dir = os.path.join(agent_dir, "scenarios")

        if not os.path.exists(scenarios_dir):
            return f"ERROR: No scenarios directory found at {scenarios_dir}"

        # List available scenarios
        scenarios = [f for f in os.listdir(scenarios_dir) if f.endswith('.txt')]
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
            return f"Successfully loaded scenario from {scenario_path}"
        except Exception as e:
            return f"ERROR: Failed to read scenario: {str(e)}"

    @debug()
    def _run_simulation(self, _: str = "") -> str:
        """Run the simulation with the selected agent and scenario."""
        if not self.target_agent or not self.scenario_text:
            return "ERROR: Must get target agent and scenario first"

        try:
            # Create agent instance
            agent = self.target_agent(manifesto=self.scenario_text)

            # Override ask_user to use LLM
            def simulated_ask_user(question: str) -> str:
                # Update memory with question
                self.update_memory(self.memory + "\nTarget Agent Question: " + question)

                # Generate response using LLM
                prompt = self.compose_request() + "\nBased on the above context and scenario, how should I respond to this question?"
                response = self.llm_call(prompt)

                # Update memory with response
                self.update_memory(self.memory + "\nSimulated Response: " + response)
                return response

            agent.override_ask_user(simulated_ask_user)

            # Run the agent
            result = agent.run()
            return f"Simulation completed. Agent output:\n{result}"

        except Exception as e:
            return f"ERROR: Simulation failed: {str(e)}"

    @debug()
    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect which tool to call based on the agent's response."""
        if "<TOOL: GET_TARGET_AGENT>" in text:
            return "GET_TARGET_AGENT", ""
        elif "<TOOL: GET_SCENARIO>" in text:
            return "GET_SCENARIO", ""
        elif "<TOOL: RUN_SIMULATION>" in text:
            return "RUN_SIMULATION", ""
        return None, None

    @debug()
    def _end_detection(self, manifesto: str, memory: str) -> bool:
        """End when simulation is complete."""
        return "<TASK_COMPLETED>" in memory
