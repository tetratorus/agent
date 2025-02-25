from lib.base import Agent
from lib.tools import list_agents, spawn_subagent, tell_subagent, read_chat

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
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