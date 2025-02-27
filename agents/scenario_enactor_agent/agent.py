from lib.base import Agent
from lib.tools.list_agents import list_agents
from lib.tools.list_files_in_scenarios_folder import list_files_in_scenarios_folder
from lib.tools.read_file_in_scenarios_folder import read_file_in_scenarios_folder

def create_agent(manifesto: str, memory: str) -> Agent:
    """Creates a Scenario Enactor Agent
    This agent enacts scenarios by listing, selecting, and roleplaying through available scenarios, facilitating automatic testing of agents by simulating realistic situations.
    """
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'LIST_AGENTS': list_agents,
            'LIST_FILES_IN_SCENARIOS_FOLDER': list_files_in_scenarios_folder,
            'READ_FILE_IN_SCENARIOS_FOLDER': read_file_in_scenarios_folder,
        },
        name="Scenario Enactor Agent",
    )
