from lib.base import Agent
from lib.tools.search import search
from lib.tools.open_url import open_url

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'SEARCH': search,
            'OPEN_URL': open_url
        },
        name="ResearchAgent",
    )
