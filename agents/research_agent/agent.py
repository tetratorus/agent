from lib.base import Agent
from lib.tools.search import search
from lib.tools.open_url import open_url

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    """Creates a Research Agent that conducts comprehensive research on any topic.
    
    This agent uses internet search capabilities to:
    1. Ask the user for a research topic
    2. Search the internet for relevant information
    3. Open and read URLs to gather detailed content
    4. Iteratively search and explore until sufficient information is gathered
    5. Provide the user with a comprehensive research output
    
    The agent uses SEARCH and OPEN_URL tools extensively to gather information
    from multiple sources before presenting findings.
    """
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'SEARCH': search,
            'OPEN_URL': open_url
        },
        name="ResearchAgent",
    )
