from lib.base import Agent
from lib.tools.list_tools import list_tools
from lib.tools.read_file_in_agents_superfolder import read_file_in_agents_superfolder
from lib.tools.list_files_in_agents_superfolder import list_files_in_agents_superfolder
from lib.tools.write_file_in_agents_superfolder import write_file_in_agents_superfolder

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'LIST_TOOLS': list_tools,
            'READ_FILE_IN_AGENTS_SUPERFOLDER': read_file_in_agents_superfolder,
            'LIST_FILES_IN_AGENTS_SUPERFOLDER': list_files_in_agents_superfolder,
            'WRITE_FILE_IN_AGENTS_SUPERFOLDER': write_file_in_agents_superfolder,
        },
        name="AgentStructurerAgent",
    )
