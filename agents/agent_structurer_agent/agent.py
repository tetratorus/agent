from lib.base import Agent
from lib.tools.list_tools import list_tools
from lib.tools.read_file_in_agents_folder import read_file_in_agents_folder
from lib.tools.list_files_in_agents_folder import list_files_in_agents_folder
from lib.tools.write_file_in_agents_folder import write_file_in_agents_folder

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'LIST_TOOLS': list_tools,
            'READ_FILE_IN_AGENTS_FOLDER': read_file_in_agents_folder,
            'LIST_FILES_IN_AGENTS_FOLDER': list_files_in_agents_folder,
            'WRITE_FILE_IN_AGENTS_FOLDER': write_file_in_agents_folder,
        },
        name="AgentStructurerAgent",
    )
