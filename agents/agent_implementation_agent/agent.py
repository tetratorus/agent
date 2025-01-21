from lib.base import Agent
import os

class AgentImplementationAgent(Agent):
    """Agent that generates Python code for other AI agents based on descriptions.

    This agent takes in a description of an agent and generates the appropriate agent.py
    implementation based on the requirements.

    Args:
        manifesto: Custom instructions for the agent.
        memory: Initial memory/context for the conversation
    """

    def __init__(self,
                 manifesto: str,
                 memory: str):

        if manifesto is None:
            raise ValueError("Manifesto must be provided")

        model_name = "openai/gpt-4o"

        super().__init__(
            model_name=model_name,
            manifesto=manifesto,
            memory=memory,
            tools={
                "GET_AGENT_DEFINITION": self.get_agent_definition,
                "READ_FILE": self.read_file,
                "VIEW_DIRCTORY_TREE": self.view_directory_tree,
            },
        )

    def get_agent_definition(self, _: str) -> str:
        """ use ASK_USER tool to get the agent definition from the user """
        return self.ask_user("What is the agent definition?")

    def read_file(self, file_path: str) -> str:
        with open(file_path, 'r') as f:
            return f.read()

    def view_directory_tree(self, directory: str) -> str:
        """Display directory structure in a tree-like format.

        Args:
            directory: Path to the directory to display

        Returns:
            String representation of the directory tree
        """
        def list_files_recursively(path, prefix=""):
            output = []
            entries = sorted([e for e in os.listdir(path) if not (e.startswith('__') or e.startswith('.'))])

            for i, entry in enumerate(entries):
                is_last = i == len(entries) - 1
                entry_path = os.path.join(path, entry)

                connector = "└── " if is_last else "├── "
                output.append(prefix + connector + entry)

                if os.path.isdir(entry_path):
                    extension = "    " if is_last else "│   "
                    output.extend(list_files_recursively(entry_path, prefix + extension))

            return output

        try:
            tree = list_files_recursively(directory)
            return "\n".join(tree)
        except Exception as e:
            return f"Error displaying directory tree: {str(e)}"
