from lib.base import Agent
from lib.tools.read_base_agent_implementation import read_base_agent_implementation
from lib.tools.read_readme import read_readme
from lib.tools.read_file_in_agents_superfolder import read_file_in_agents_superfolder
from lib.tools.list_files_in_agents_superfolder import list_files_in_agents_superfolder
from lib.tools.list_tools import list_tools
from lib.tools.list_agents import list_agents

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    """Creates an agent that helps users generate manifestos for new AI agents.

    This agent guides users through the process of creating manifestos for new agents by:
    1. Providing information about the agent framework and structure
    2. Asking intent-based questions to understand the user's needs
    3. Drafting a manifesto that follows the required format
    4. Including appropriate tools based on the agent's purpose

    The agent focuses on understanding user intent rather than implementation details,
    and ensures all manifestos include the four default tools.
    """
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'READ_BASE_AGENT_IMPLEMENTATION': read_base_agent_implementation,
            'READ_FILE_IN_AGENTS_SUPERFOLDER': read_file_in_agents_superfolder,
            'LIST_FILES_IN_AGENTS_SUPERFOLDER': list_files_in_agents_superfolder,
            'READ_README': read_readme,
            'LIST_AGENTS': list_agents,
            'LIST_TOOLS': list_tools
        },
        name="AgentManifestoAgent",
    )
