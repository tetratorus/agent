#!/usr/bin/env python3

import os
import sys
import importlib.util
import secrets
from typing import Type, List, Tuple, Optional, Dict, Any, TextIO
import datetime
import logging

_first_agent_id = None
GREY_TEXT_COLOR = "\033[90m"
WHITE_TEXT_COLOR = "\033[97m"

class StreamingLogger(logging.Handler):
    """Logger that writes to both file and stdout in real-time."""
    def __init__(self, log_file: TextIO):
        super().__init__()
        self.terminal = sys.stdout
        self.log_file = log_file
        self.setFormatter(logging.Formatter('%(name)s - %(message)s'))
        # Cache for agent colors
        self.agent_colors = {}
        # ANSI colors (text only, no background)
        self.text_colors = [
            "\033[91m",  # Bright Red
            "\033[92m",  # Bright Green
            "\033[93m",  # Bright Yellow
            "\033[94m",  # Bright Blue
            "\033[95m",  # Bright Magenta
            "\033[96m",  # Bright Cyan
            "\033[31m",  # Red
            "\033[32m",  # Green
            "\033[33m",  # Yellow
            "\033[34m",  # Blue
            "\033[35m",  # Magenta
            "\033[36m",  # Cyan
        ]
        # Store the terminal log level (will be set when adding handler)
        self.terminal_level = logging.INFO

    def get_color_for_agent(self, agent_id):
        """Select a ANSI color based on the hash of the agent ID."""
        if agent_id in self.agent_colors:
            return self.agent_colors[agent_id]

        # Generate a simple hash number from the agent ID
        hash_val = sum(ord(c) for c in agent_id) % len(self.text_colors)
        color = self.text_colors[hash_val]

        # Cache the color for this agent
        self.agent_colors[agent_id] = color
        return color

    def emit(self, record):
        global _first_agent_id
        # Get the original message
        original_msg = record.getMessage()

        # For terminal output with colored agent prefix - only if at or above terminal level
        if record.levelno >= self.terminal_level:
            if hasattr(record, 'name') and record.name.startswith('agent.'):
                # Extract agent ID
                agent_id = record.name[6:]  # Remove 'agent.' prefix
                if _first_agent_id is None:
                    _first_agent_id = agent_id
                color_code = self.get_color_for_agent(agent_id)
                reset_code = "\033[0m"

                # Color only the agent prefix, not the whole message
                colored_prefix = f"{color_code}{record.name}{reset_code}"

                if _first_agent_id == agent_id:
                    colored_msg = f"{WHITE_TEXT_COLOR}{original_msg}\033[0m"
                else:
                    colored_msg = f"{GREY_TEXT_COLOR}{original_msg}\033[0m"

                # Write to terminal with colored prefix
                self.terminal.write(f"{colored_prefix} - {colored_msg}\n")
            else:
                # Standard output for non-agent messages
                self.terminal.write(f"{record.name} - {original_msg}\n")

            # Flush terminal to ensure real-time output
            self.terminal.flush()

        # Always write to log file regardless of level
        self.log_file.write(f"{record.name} - {original_msg}\n")
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def set_terminal_level(self, level):
        """Set the log level for terminal output only."""
        self.terminal_level = level

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
    print("1. Run agent (INFO level)")
    print("2. Run agent (DEBUG level - verbose)")

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
    runs_dir = os.path.join(os.path.dirname(__file__), "runs", agent_name)
    os.makedirs(runs_dir, exist_ok=True)

    # Create run log with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_log = os.path.join(runs_dir, f"run_log_{timestamp}_{secrets.token_hex(4)}")

    # Setup logging
    with open(run_log, "w") as log_file:
        # Set up logging
        logger = StreamingLogger(log_file)

        # Create a specific logger for agents instead of using root logger
        agent_logger = logging.getLogger('agent')

        # Always set the logger to DEBUG level to capture all logs
        agent_logger.setLevel(logging.DEBUG)

        # Set terminal log level based on selected mode
        if mode == 2:  # Verbose/DEBUG mode
            logger.set_terminal_level(logging.DEBUG)
        else:  # Normal/INFO mode
            logger.set_terminal_level(logging.INFO)

        agent_logger.addHandler(logger)
        # Prevent propagation to root logger
        agent_logger.propagate = False

        agent_logger.info(f"Running Agent: {display_name}")
        agent = agent_factory(manifesto=manifesto, memory="")
        agent.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
