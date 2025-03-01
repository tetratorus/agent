import os
import json

def list_agents(caller_id: str, _: str = '') -> str:
    """Lists all available agents and their descriptions."""
    try:
        # Get project root directory (two levels up from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        agents_dir = os.path.join(project_root, 'agents')

        if not os.path.isdir(agents_dir):
            return f"Agents directory not found at: {agents_dir}"

        agents = []
        for agent_name in os.listdir(agents_dir):
            agent_dir = os.path.join(agents_dir, agent_name)
            if os.path.isdir(agent_dir):
                config_file = os.path.join(agent_dir, 'config.json')
                if os.path.isfile(config_file):
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                            description = config.get('description', 'No description available')
                            agents.append(f"\nAGENT: {agent_name}\n{'='*50}\n{description}\n{'='*50}")
                    except Exception as e:
                        agents.append(f"\n{agent_name}: Error parsing config file: {str(e)}")

        if not agents:
            return "No agents found"

        # Sort agents alphabetically by agent name
        agents.sort(key=lambda x: x.split("AGENT: ")[1].split("\n")[0] if "AGENT: " in x else x)

        return "Available agents:\n" + ''.join(agents)

    except Exception as e:
        return f"Error listing agents: {str(e)}"
