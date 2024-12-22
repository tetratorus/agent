#!/usr/bin/env python3

import os
import sys
from typing import List, Tuple, Optional
import importlib.util
import subprocess
import inspect

def get_agent_class(agent_name: str) -> Optional[type]:
    """Import and return the agent class from an agent module."""
    try:
        module = importlib.import_module(f"agents.{agent_name}.agent")
        # Find the agent class (usually the only class that inherits from Agent)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and name.endswith('Agent'):
                return obj
    except ImportError:
        return None
    return None

def get_available_agents() -> List[Tuple[str, str, Optional[str]]]:
    """Get list of available agents, their runner paths, and descriptions."""
    agents_dir = os.path.join(os.path.dirname(__file__), 'agents')
    agents = []

    # Look through agents directory
    for item in os.listdir(agents_dir):
        if item.startswith('__'):
            continue

        agent_dir = os.path.join(agents_dir, item)
        if not os.path.isdir(agent_dir):
            continue

        # Check if runner exists
        runner = os.path.join(agent_dir, 'run', 'runner.py')
        if os.path.exists(runner):
            # Get agent description from class docstring
            agent_class = get_agent_class(item)
            description = inspect.getdoc(agent_class) if agent_class else None
            agents.append((item, f"agents.{item}.run.runner", description))

    return sorted(agents)

def print_agents(agents: List[Tuple[str, str, Optional[str]]]) -> None:
    """Print available agents in a nice format."""
    print("\nAvailable Agents:")
    print("----------------")
    for i, (name, _, description) in enumerate(agents, 1):
        # Convert snake_case to Title Case for display
        display_name = ' '.join(word.capitalize() for word in name.split('_'))
        print(f"{i}. {display_name}")
    print()

def show_agent_details(agent: Tuple[str, str, Optional[str]]) -> None:
    """Show detailed information about an agent."""
    name, _, description = agent
    display_name = ' '.join(word.capitalize() for word in name.split('_'))

    print(f"\n{display_name}")
    print("=" * len(display_name))
    if description:
        # Format the description nicely
        description = inspect.cleandoc(description)
        print(description)
    else:
        print("No description available")
    print()

def get_user_choice(max_choice: int) -> int:
    """Get user's choice of agent."""
    while True:
        try:
            choice = input("Select an agent (enter number): ")
            num = int(choice)
            if 1 <= num <= max_choice:
                return num
            print(f"Please enter a number between 1 and {max_choice}")
        except ValueError:
            print("Please enter a valid number")

def run_agent(module_path: str) -> None:
    """Run the selected agent's test runner using Python module import."""
    try:
        subprocess.run([sys.executable, "-m", module_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running agent: {e}")

def main():
    while True:
        # Get available agents
        agents = get_available_agents()
        if not agents:
            print("No agents found in the agents directory!")
            return

        # Print agents and get user choice
        print_agents(agents)
        choice = get_user_choice(len(agents))

        # Show agent details before running
        selected_agent = agents[choice - 1]
        show_agent_details(selected_agent)

        # Confirm run
        confirm = input("Run this agent? [Y/n]: ").lower()
        if confirm in ['', 'y', 'yes']:
            _, module_path, _ = selected_agent
            run_agent(module_path)
            break  # Exit after running
        else:
            print("\nReturning to agent selection...")
            continue  # Go back to start of loop

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
