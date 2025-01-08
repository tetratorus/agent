import os
import sys
import importlib.util
import inspect
import shutil
from typing import Type, List, Tuple, Optional

def get_agent_class(agent_name: str) -> Optional[Type]:
    """Import and return the agent class from an agent module."""
    try:
        module = importlib.import_module(f"agents.{agent_name}.agent")
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and name.endswith('Agent') and obj.__module__ == module.__name__:
                return obj
    except ImportError:
        print(f"Could not load agent class for {agent_name}")
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
    return sorted(agents, key=lambda x: x[0])

def clean_agent_runs(agent_name: str) -> int:
    """Clean runs directory for a specific agent. Returns number of files removed."""
    runs_dir = os.path.join(os.path.dirname(__file__), "agents", agent_name, "runs")
    if not os.path.exists(runs_dir):
        return 0

    count = 0
    for item in os.listdir(runs_dir):
        if item.startswith('run_log_'):
            os.remove(os.path.join(runs_dir, item))
            count += 1
    return count

def clean_agent_simulations(agent_name: str) -> int:
    """Clean simulations directory for a specific agent. Returns number of files removed."""
    sims_dir = os.path.join(os.path.dirname(__file__), "agents", agent_name, "simulations")
    if not os.path.exists(sims_dir):
        return 0

    count = 0
    for item in os.listdir(sims_dir):
        if item.startswith('sim_'):
            os.remove(os.path.join(sims_dir, item))
            count += 1
    return count

def main():
    # Get available agents
    agents = get_available_agents()
    if not agents:
        print("No agents found!")
        return

    # Show agents
    print("\nAvailable Agents:")
    print("----------------")
    print("1. All Agents")
    for i, (name, _) in enumerate(agents, 2):
        display_name = ' '.join(word.capitalize() for word in name.split('_'))
        print(f"{i}. {display_name}")
    print()

    # Select agent
    while True:
        try:
            choice = int(input("Select an agent (number): "))
            if 1 <= choice <= len(agents) + 1:
                break
            print("Invalid choice, try again")
        except ValueError:
            print("Please enter a number")

    # Show cleaning options
    print("\nWhat would you like to clean?")
    print("1. Runs")
    print("2. Simulations")
    print("3. Both")
    print()

    while True:
        try:
            clean_choice = int(input("Select what to clean (number): "))
            if 1 <= clean_choice <= 3:
                break
            print("Invalid choice, try again")
        except ValueError:
            print("Please enter a number")

    # Clean based on selections
    total_runs = 0
    total_sims = 0

    if choice == 1:  # All agents
        print("\nCleaning all agents...")
        for agent_name, _ in agents:
            if clean_choice in [1, 3]:
                runs = clean_agent_runs(agent_name)
                if runs > 0:
                    print(f"Removed {runs} run logs from {agent_name}")
                total_runs += runs

            if clean_choice in [2, 3]:
                sims = clean_agent_simulations(agent_name)
                if sims > 0:
                    print(f"Removed {sims} simulations from {agent_name}")
                total_sims += sims
    else:
        agent_name = agents[choice - 2][0]
        print(f"\nCleaning {agent_name}...")
        if clean_choice in [1, 3]:
            total_runs = clean_agent_runs(agent_name)
            if total_runs > 0:
                print(f"Removed {total_runs} run logs")

        if clean_choice in [2, 3]:
            total_sims = clean_agent_simulations(agent_name)
            if total_sims > 0:
                print(f"Removed {total_sims} simulations")

    print(f"\nTotal cleaned: {total_runs} run logs, {total_sims} simulations")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
