from lib.base import Agent
from lib.tools.read_base_agent_implementation import read_base_agent_implementation
from lib.tools.read_readme import read_readme
from lib.tools.read_file_in_agents_folder import read_file_in_agents_folder
from lib.tools.list_files_in_agents_folder import list_files_in_agents_folder
from lib.tools.list_tools import list_tools

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'READ_BASE_AGENT_IMPLEMENTATION': read_base_agent_implementation,
            'READ_FILE_IN_AGENTS_FOLDER': read_file_in_agents_folder,
            'LIST_FILES_IN_AGENTS_FOLDER': list_files_in_agents_folder,
            'READ_README': read_readme,
            'LIST_TOOLS': list_tools
        },
        name="AgentManifestoAgent",
    )
