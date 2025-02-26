import importlib.util
from pathlib import Path
import time
import logging

def spawn_subagent(caller_id: str, input_str: str) -> str:
    """Spawn a new instance of a subagent that communicates via a chat file.

    Args:
        caller_id (str): The ID of the caller
        input_str (str): String in format 'agent_name§chat_id'

    Returns:
        str: The agent instance ID

    Raises:
        ValueError: If input format is invalid or agent not found
        ImportError: If agent module cannot be imported
    """
    agent_name = input_str

    agents_dir = Path(__file__).parent.parent.parent / "agents"
    agent_dir = agents_dir / agent_name
    agent_file = agent_dir / "agent.py"

    if not agent_file.exists():
        raise ValueError(f"Agent {agent_name} not found")

    # Import the agent module
    spec = importlib.util.spec_from_file_location("agent", str(agent_file))
    if not spec or not spec.loader:
        raise ImportError(f"Could not load agent module for {agent_name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Create the agent instance
    try:
        # Load default manifesto
        manifesto_file = agent_dir / "manifestos" / "default_manifesto.txt"
        if not manifesto_file.exists():
            raise ValueError(f"No default_manifesto.txt found for agent {agent_name}")

        manifesto = manifesto_file.read_text()

        agent = module.create_agent(
            manifesto=manifesto,
            memory=""
        )

        # Create chat files for bidirectional communication
        chats_dir = Path(__file__).parent / 'chats'
        chats_dir.mkdir(exist_ok=True)

        # Create unique chat files for this agent instance
        caller_to_agent = chats_dir / f"{caller_id}_to_{agent.id}.txt"
        agent_to_caller = chats_dir / f"{agent.id}_to_{caller_id}.txt"
        caller_to_agent.touch()
        agent_to_caller.touch()

        # Configure agent's tell_user to write to agent_to_caller file
        def tell_user(agent_id: str, message: str) -> str:
            try:
                with open(agent_to_caller, 'a') as f:
                    f.write(f"[{agent_id}] {message}\n")
                agent.logger.info(f"[TELL_USER] {message}")
                return ""
            except IOError as e:
                error_message = f"Failed to write to chat file: {str(e)}"
                agent.logger.info(error_message)
                agent.logger.error(error_message)
                raise IOError(error_message)

        # Configure agent's ask_user to write to agent_to_caller and read from caller_to_agent
        def ask_user(agent_id: str, message: str) -> str:
            print("DID THIS EVEN GET FUCKING CALLED??????")
            try:
                # First write the question
                agent.logger.info(f"[ASK_USER] {message}")
                tell_user(agent_id, message)

                # Then wait for new content
                start_time = time.time()
                with open(caller_to_agent, 'r') as f:
                    last_content = f.read()

                while True:
                    with open(caller_to_agent, 'r') as f:
                        current_content = f.read()
                    if current_content != last_content:
                        # Return just the new content
                        new_content = current_content[len(last_content):].strip()
                        agent.logger.info(f"[USER_RESPONSE] Content: {new_content}")
                        return new_content

                    if time.time() - start_time > 60:  # 1 minute timeout
                        timeout_message = "ASK_USER timed out waiting for response"
                        agent.logger.info(timeout_message)
                        raise TimeoutError("No new messages found, feel free to call this function again to await new messages")

                    time.sleep(5)  # Sleep for 5 seconds between checks
            except IOError as e:
                error_message = f"Failed to read from chat file: {str(e)}"
                agent.logger.info(error_message)
                agent.logger.error(error_message)
                raise IOError(error_message)

        agent.tell_user = tell_user
        agent.ask_user = ask_user

        return agent.id  # Return unique ID for this agent instance
    except Exception as e:
        raise ValueError(f"Failed to create agent instance: {str(e)}")
