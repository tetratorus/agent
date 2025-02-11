#!/usr/bin/env python3

import os
import sys
import importlib.util
import inspect
from typing import Type, List, Tuple, Optional, Dict, Any, TextIO
import datetime

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

def get_agent_factory(agent_name: str, silent: bool = False) -> Optional[callable]:
    """Import and return the create_agent function from an agent module."""
    try:
        module = importlib.import_module(f"agents.{agent_name}.agent")
        if hasattr(module, 'create_agent'):
            return module.create_agent
    except ImportError:
        if not silent:
            print(f"Could not load agent for {agent_name}")
        return None
    return None

def get_available_agents() -> List[Tuple[str, Optional[str]]]:
    """Get list of available agents and their descriptions."""
    agents = []
    agents_dir = os.path.join(os.path.dirname(__file__), "agents")
    for item in os.listdir(agents_dir):
        if os.path.isdir(os.path.join(agents_dir, item)) and not item.startswith('__'):
            agent_factory = get_agent_factory(item, silent=True)
            description = agent_factory.__doc__ if agent_factory and agent_factory.__doc__ else None
            agents.append((item, description))
    return sorted(agents, key=lambda x: x[0])

def main():
    # Get available agents
    agents = get_available_agents()
    if not agents:
        print("No agents found!")
        return

    # Show agents
    print("\nAvailable Agents:")
    print("----------------")
    for i, (name, _) in enumerate(agents):
        display_name = ' '.join(word.capitalize() for word in name.split('_'))
        print(f"{i+1}. {display_name}")
    print()

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

    # Show agent details
    display_name = ' '.join(word.capitalize() for word in agent_name.split('_'))
    print(f"\n{display_name}")
    print("=" * len(display_name))
    if description:
        print(description.strip())
    print()

    # Load and run agent
    print(f"Loading agent: {agent_name}")
    agent_factory = get_agent_factory(agent_name)
    if not agent_factory:
        print(f"Could not load the agent for {agent_name}")
        return

    # Select mode
    print("\nModes:")
    print("1. Run agent")
    print("2. Run agent (verbose)")

    while True:
        try:
            mode = int(input("\nSelect mode: "))
            if mode in [1, 2]:
                break
            print("Invalid choice, try again")
        except ValueError:
            print("Please enter a number")

    # List available manifestos
    manifesto_dir = os.path.join(os.path.dirname(__file__), "agents", agent_name, "manifestos")
    manifestos = [f for f in os.listdir(manifesto_dir) if not f.startswith('.')]

    print("\nAvailable Manifestos:")
    print("-------------------")
    for i, name in enumerate(manifestos):
        print(f"{i+1}. {name}")
    print()

    # Select manifesto
    while True:
        try:
            choice = int(input("Select a manifesto (number): ")) - 1
            if 0 <= choice < len(manifestos):
                break
            print("Invalid choice, try again")
        except ValueError:
            print("Please enter a number")

    manifesto_path = os.path.join(manifesto_dir, manifestos[choice])
    try:
        with open(manifesto_path) as f:
            manifesto = f.read()
    except FileNotFoundError:
        print(f"Could not find manifesto at {manifesto_path}")
        return

    # Create runs directory if it doesn't exist
    runs_dir = os.path.join(os.path.dirname(__file__), "agents", agent_name, "runs")
    os.makedirs(runs_dir, exist_ok=True)

    # Create run log with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_log = os.path.join(runs_dir, f"run_log_{timestamp}")

    # Setup logging
    with open(run_log, "w") as log_file:
        logger = StreamingLogger(log_file)
        logger.write(f"Running Agent: {display_name}\n")
        agent = agent_factory(manifesto=manifesto, memory="")
        agent.log_handler = logger.write
        if mode == 2:
            agent.debug_verbose = True
        result = agent.run()
        logger.write(result)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
