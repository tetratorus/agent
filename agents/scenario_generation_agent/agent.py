from lib.base import Agent
from lib.tools.read_readme import read_readme
from lib.tools.list_agents import list_agents
from lib.tools.list_files_in_agents_superfolder import list_files_in_agents_superfolder
from lib.tools.read_file_in_agents_superfolder import read_file_in_agents_superfolder
from lib.tools.list_files_in_scenarios_folder import list_files_in_scenarios_folder
from lib.tools.read_file_in_scenarios_folder import read_file_in_scenarios_folder
from lib.tools.write_file_in_scenarios_folder import write_file_in_scenarios_folder

def create_agent(manifesto: str, memory: str) -> Agent:
    """Creates a Scenario Generation Agent
    This agent is designed to generate detailed scenario texts for target agents.
    """
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            LIST_AGENTS: list_agents,
            LIST_FILES_IN_AGENTS_SUPERFOLDER: list_files_in_agents_superfolder,
            READ_FILE_IN_AGENTS_SUPERFOLDER: read_file_in_agents_superfolder,
            LIST_FILES_IN_SCENARIOS_FOLDER: list_files_in_scenarios_folder,
            READ_FILE_IN_SCENARIOS_FOLDER: read_file_in_scenarios_folder,
            WRITE_FILE_IN_SCENARIOS_FOLDER: write_file_in_scenarios_folder,
        },
        name="ScenarioGenerationAgent",
    )
