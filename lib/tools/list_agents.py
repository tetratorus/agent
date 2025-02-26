import os

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
                agent_file = os.path.join(agent_dir, 'agent.py')
                if os.path.isfile(agent_file):
                    with open(agent_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract docstring from create_agent function
                        import ast
                        try:
                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef) and node.name == 'create_agent':
                                    docstring = ast.get_docstring(node)
                                    if docstring:
                                        agents.append(f"\nAGENT: {agent_name}\n{'='*50}\n{docstring}\n{'='*50}")
                                    else:
                                        agents.append(f"\nAGENT: {agent_name}\n{'='*50}\nNo description available\n{'='*50}")
                                    break
                        except Exception as e:
                            agents.append(f"\n{agent_name}: Error parsing agent file: {str(e)}")
        
        if not agents:
            return "No agents found"
            
        return "Available agents:\n" + ''.join(agents)

    except Exception as e:
        return f"Error listing agents: {str(e)}"
