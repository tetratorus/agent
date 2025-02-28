from lib.base import Agent
from lib.tools.search import search
from lib.tools.open_url import open_url

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    """Creates a role-playing agent
    This agent is designed to role-play by gathering information related to a given character name and then acting out the role based on that information.
    It has access to the SEARCH and OPEN_URL tools to gather and process relevant data.
    """
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'SEARCH': search,
            'OPEN_URL': open_url,
        },
        name="RolePlayingAgent",
    )
