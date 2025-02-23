from lib.base import Agent
from lib.tools.read_readme import read_readme
from lib.tools.list_tools import list_tools
from lib.tools.read_file_in_agents_folder import read_file_in_agents_folder
from lib.tools.list_files_in_agents_folder import list_files_in_agents_folder
from lib.tools.write_file_in_agents_folder import write_file_in_agents_folder
from lib.tools.ask_user import ask_user
from lib.tools.tell_user import tell_user
from lib.tools.end_run import end_run

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'READ_README': read_readme,
            'LIST_TOOLS': list_tools,
            'READ_FILE_IN_AGENTS_FOLDER': read_file_in_agents_folder,
            'LIST_FILES_IN_AGENTS_FOLDER': list_files_in_agents_folder,
            'WRITE_FILE_IN_AGENTS_FOLDER': write_file_in_agents_folder,
            'ASK_USER': ask_user,
            'TELL_USER': tell_user,
            'END_RUN': end_run
        },
        name="AgentStructurerAgent",
    )