from lib.base import Agent
from lib.tools.spawn_subagent import spawn_subagent
from lib.tools.listen_to_subagent import listen_to_subagent
from lib.tools.respond_to_subagent import respond_to_subagent
from lib.tools.list_agents import list_agents
from lib.tools.list_files_in_scenarios_folder import list_files_in_scenarios_folder
from lib.tools.list_files_in_agents_superfolder import list_files_in_agents_superfolder


def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    """Creates a Messenger Agent that coordinates tasks between users and subagents.

    This agent facilitates communication between the user and other agents by:
    1. Listing available agents to understand their capabilities
    2. Spawning appropriate subagents based on the user's goal
    3. Passing messages between subagents to accomplish tasks
    4. Relaying final information back to the user

    The agent develops a plan leveraging the capabilities of multiple subagents
    and manages the communication flow between them.
    """
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'LIST_AGENTS': list_agents,
            'SPAWN_SUBAGENT': spawn_subagent,
            'LIST_FILES_IN_SCENARIOS_FOLDER': list_files_in_scenarios_folder,
            'LIST_FILES_IN_AGENTS_SUPERFOLDER': list_files_in_agents_superfolder,
            'LISTEN_TO_SUBAGENT': listen_to_subagent,
            'RESPOND_TO_SUBAGENT': respond_to_subagent,
        },
        name="ScenarioRunnerAgent",
    )
