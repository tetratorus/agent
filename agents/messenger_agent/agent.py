from lib.base import Agent
from lib.tools.spawn_subagent import spawn_subagent
from lib.tools.tell_subagent import tell_subagent
from lib.tools.read_chat import read_chat
from lib.tools.list import list_agents

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
            'TELL_SUBAGENT': tell_subagent,
            'READ_CHAT': read_chat,
        },
        name="MessengerAgent",
    )
