from lib.base import Agent

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={},
        name="ScissorsPaperStoneAgent"
    )
