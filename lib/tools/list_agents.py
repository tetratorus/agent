from pathlib import Path
import importlib.util
import inspect


def list_agents(caller_id: str, _: str = '') -> str:
    """List all available agents in the agents directory with their descriptions."""

    agents_path = Path(__file__).parent.parent.parent / "agents"
    result = []
    
    for agent_dir in agents_path.iterdir():
        if not agent_dir.is_dir():
            continue
            
        agent_name = agent_dir.name
        agent_file = agent_dir / "agent.py"
        
        if not agent_file.exists():
            result.append(f"{agent_name}: [No agent.py file found]")
            continue
            
        # Import the agent module
        try:
            spec = importlib.util.spec_from_file_location("agent", str(agent_file))
            if not spec or not spec.loader:
                result.append(f"{agent_name}: [Could not load agent module]")
                continue
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get docstring of create_agent function
            if hasattr(module, 'create_agent'):
                docstring = inspect.getdoc(module.create_agent) or "[No docstring]"
                result.append(f"{agent_name}: {docstring}")
            else:
                result.append(f"{agent_name}: [No create_agent function found]")
        except Exception as e:
            result.append(f"{agent_name}: [Error loading agent: {str(e)}]")
    
    return '\n'.join(result)
