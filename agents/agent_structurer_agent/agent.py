from lib.base import Agent
from lib.tools.list_tools import list_tools
from lib.tools.read_file_in_agents_superfolder import read_file_in_agents_superfolder
from lib.tools.list_files_in_agents_superfolder import list_files_in_agents_superfolder
from lib.tools.write_file_in_agents_superfolder import write_file_in_agents_superfolder

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    """Creates an agent that takes a manifesto as input and sets up the necessary folder and file structure for new agents.

    This agent takes a manifesto as input and:
    1. Parses the manifesto to understand required files and structure
    2. Creates the necessary folders and files for the new agent
    3. Ensures the agent.py file follows the correct structure
    4. Places the manifesto in the correct location


    The agent only uses existing tools and doesn't redefine default tools.
    It verifies its work by checking the created files before completion.
    """
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
