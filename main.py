#!/usr/bin/env python3

import os
import sys
import json
import datetime
import importlib.util
import inspect
from typing import Dict, Any, TextIO, Type, List, Tuple, Optional

class StreamingLogger:
    """Logger that writes to both file and stdout in real-time."""
    def __init__(self, log_file: TextIO):
        self.terminal = sys.stdout
        self.log_file = log_file

    def write(self, message: str):
        self.terminal.write(message)
        self.log_file.write(message)
        # Flush both to ensure real-time output
        self.terminal.flush()
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

def get_agent_class(agent_name: str) -> Optional[Type]:
    """Import and return the agent class from an agent module."""
    try:
        module = importlib.import_module(f"agents.{agent_name}.agent")
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and name.endswith('Agent') and obj.__module__ == module.__name__:
                return obj
    except ImportError:
        return None
    return None

def get_available_agents() -> List[Tuple[str, Optional[str]]]:
    """Get list of available agents and their descriptions."""
    agents = []
    agents_dir = os.path.join(os.path.dirname(__file__), "agents")
    for item in os.listdir(agents_dir):
        if os.path.isdir(os.path.join(agents_dir, item)) and not item.startswith('__'):
            agent_class = get_agent_class(item)
            description = agent_class.__doc__ if agent_class and agent_class.__doc__ else None
            agents.append((item, description))

    agents.sort(key=lambda x: x[0])  # Simple alphabetical sort
    return agents

def print_agents(agents: List[Tuple[str, Optional[str]]]) -> None:
    """Print available agents in a nice format."""
    print("\nAvailable Agents:")
    print("----------------")
    for i, (name, _) in enumerate(agents):
        display_name = ' '.join(word.capitalize() for word in name.split('_'))
        print(f"{i+1}. {display_name}")
    print()

def show_agent_details(name: str, description: Optional[str]) -> None:
    """Show detailed information about an agent."""
    display_name = ' '.join(word.capitalize() for word in name.split('_'))
    print(f"\n{display_name}")
    print("=" * len(display_name))
    if description:
        print(description.strip())
    else:
        print("No description available")
    print()

def create_run_folder(agent_dir: str) -> str:
    """Create a timestamped folder for this run."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(agent_dir, "logs", f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir

def load_variables(var_dir: str) -> Dict[str, Any]:
    """Load variables from JSON files."""
    variables = {}
    for filename in os.listdir(var_dir):
        if filename.endswith('.json'):
            var_name = filename[:-5]  # Remove .json
            with open(os.path.join(var_dir, filename)) as f:
                variables[var_name] = json.load(f)[0]  # Take first element for now
    return variables

def load_all_variations(var_dir: str) -> Tuple[List[Dict[str, str]], int]:
    """Load all variations from all JSON files.
    Returns tuple of (list of variable combinations, number of variations)"""
    variations = {}
    num_variations = None

    # Load all variations from each file
    for filename in os.listdir(var_dir):
        if filename.endswith('.json'):
            var_name = filename[:-5]
            with open(os.path.join(var_dir, filename)) as f:
                var_list = json.load(f)
                variations[var_name] = var_list

                # Check all files have same number of variations
                if num_variations is None:
                    num_variations = len(var_list)
                elif len(var_list) != num_variations:
                    raise ValueError(f"Mismatched number of variations in {filename}. Expected {num_variations}, got {len(var_list)}")

    if not num_variations:
        raise ValueError("No variations found")

    return variations, num_variations

def run_agent(agent_class: Type, variables: Dict[str, Any]) -> Any:
    """Run the agent with console output only."""
    agent = agent_class(**variables)
    return agent.run()

def run_agent_with_logging(agent_class: Type, variables: Dict[str, Any], run_dir: str) -> Any:
    """Run the agent and capture all output to file."""
    with open(os.path.join(run_dir, "debug.log"), "w") as log_file:
        sys.stdout = StreamingLogger(log_file)
        try:
            agent = agent_class(**variables)
            result = agent.run()

            with open(os.path.join(run_dir, "results"), "w") as f:
                json.dump({"result": result}, f, indent=2)

            return result
        finally:
            sys.stdout = sys.__stdout__

def optimize_agent(agent_name: str, agent_class: Type):
    """Optimize agent by trying different variables"""
    print(f"\nOptimizing {agent_name}...")

    # Setup directories
    agent_dir = os.path.join(os.path.dirname(__file__), "agents", agent_name)
    var_dir = os.path.join(agent_dir, "variables")

    # Load all variations
    variations, num_variations = load_all_variations(var_dir)
    print(f"\nFound {num_variations} variations to test")

    # Try each variation set
    for i in range(num_variations):
        print(f"\nTesting variation set {i+1}/{num_variations}:")

        # Build variables for this variation
        test_vars = {}
        for var_name, var_list in variations.items():
            test_vars[var_name] = var_list[i]
            preview = var_list[i][:200] + "..." if len(var_list[i]) > 200 else var_list[i]
            print(f"{var_name}: {preview}")

        # Run with these variables
        run_dir = create_run_folder(agent_dir)
        try:
            result = run_agent_with_logging(agent_class, test_vars, run_dir)
            print(f"Result: {result}")
            print(f"Logs saved to: {run_dir}")
        except Exception as e:
            print(f"Failed: {e}")
            print(f"Error logs in: {run_dir}")

def generate_variables(agent_name: str, agent_class: Type):
    """Generate variations of agent variables using LLM."""
    # read the README.md file
    with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
        readme = f.read()

    # read the base.py
    with open(os.path.join(os.path.dirname(__file__), "lib", "base.py")) as f:
        base_code = f.read()

    # read the agent code
    with open(os.path.join(os.path.dirname(__file__), "agents", agent_name, "agent.py")) as f:
        agent_code = f.read()

    pass

def run_variations(agent_name: str, agent_class: Type):
    # TO DO: implement run variations
    pass

def score_results(agent_name: str):
    # TO DO: implement score results
    pass

def view_results(agent_name: str):
    # TO DO: implement view results
    pass

def main():
    # Get available agents
    agents = get_available_agents()
    if not agents:
        print("No agents found!")
        return

    # Show agents
    print_agents(agents)

    # Select agent
    while True:
        try:
            choice = int(input("Select an agent (number): ")) - 1
            if 0 <= choice < len(agents):
                break
            print("Invalid choice, try again")
        except ValueError:
            print("Please enter a number")

    agent_name, description = agents[choice]
    show_agent_details(agent_name, description)

    agent_class = get_agent_class(agent_name)
    if not agent_class:
        print(f"Could not load agent class for {agent_name}")
        return

    # Select mode
    print("\nModes:")
    print("1. Run agent")
    print("2. Generate variables")
    print("3. Run variations")
    print("4. Score results")
    print("5. View results")

    while True:
        try:
            mode = int(input("\nSelect mode: "))
            if mode in [1, 2, 3, 4, 5]:
                break
            print("Invalid choice, try again")
        except ValueError:
            print("Please enter a number")

    if mode == 1:
        # Run mode - console output only
        agent_dir = os.path.join(os.path.dirname(__file__), "agents", agent_name)
        var_dir = os.path.join(agent_dir, "variables")
        variables = load_variables(var_dir)
        result = run_agent(agent_class, variables)
        print(f"\nRun completed.")
    elif mode == 2:
        generate_variables(agent_name, agent_class)
    elif mode == 3:
        run_variations(agent_name, agent_class)
    elif mode == 4:
        score_results(agent_name)
    else:
        view_results(agent_name)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
