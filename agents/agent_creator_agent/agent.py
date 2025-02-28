from lib.base import Agent
from lib.tools.spawn_subagent import spawn_subagent
from lib.tools.listen_to_subagent import listen_to_subagent
from lib.tools.respond_to_subagent import respond_to_subagent
from lib.tools.list_agents import list_agents

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    """Creates an Agent Creator Agent that coordinates the creation of new agents.

    This agent facilitates the creation of a new agent by:
    1. Spawning the 'Agent Manifesto Agent' to generate a manifesto based on user input
    2. Relaying messages between the user and the 'Agent Manifesto Agent' verbatim
    3. Passing the completed manifesto to the 'Agent Structurer Agent'
    4. Informing the user when the new agent is created.

    The agent follows a simple messaging plan to coordinate between the user and two specific subagents,
    ensuring the new agent is created without assuming detailed subagent behaviors.
    """
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'LIST_AGENTS': list_agents,
            'SPAWN_SUBAGENT': spawn_subagent,
            'LISTEN_TO_SUBAGENT': listen_to_subagent,
            'RESPOND_TO_SUBAGENT': respond_to_subagent,
        },
        name="AgentCreatorAgent",
    )
