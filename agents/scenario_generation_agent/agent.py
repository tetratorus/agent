from lib.base import Agent

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    """Creates a Scenario Generation Agent that generates detailed test scenarios for other agents.
    
    This agent analyzes a target agent's manifesto and:
    1. Understands the target agent's purpose and functionality
    2. Generates complete, detailed scenarios to test the agent
    3. Creates all necessary artifacts for the scenario simulation
    4. Provides concrete, reproducible content rather than high-level descriptions
    
    The scenarios are designed to be used by a simulation agent that will
    override 'ask_user' calls with responses based on the generated scenario.
    """
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={},
        name="ScenarioGenerationAgent",
    )
