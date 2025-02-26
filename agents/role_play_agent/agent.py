from lib.base import Agent
from lib.tools.search import search

def create_agent(manifesto: str, memory: str) -> Agent:
    """Creates an agent that role plays as a person specified by the user.
    The agent uses the SEARCH tool to gather information and role play as that person in an engaging way.
    """
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'SEARCH': search,
        },
        name="RolePlayAgent",
    )
