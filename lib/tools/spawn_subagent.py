import importlib.util
from pathlib import Path
import time
import logging
import threading

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
        chats_dir = Path(__file__).parent.parent.parent / 'chats'
        chats_dir.mkdir(exist_ok=True)

        # Create unique chat files for this agent instance
        caller_to_agent = chats_dir / f"{caller_id}_to_{agent.id}.txt"
        agent_to_caller = chats_dir / f"{agent.id}_to_{caller_id}.txt"
        caller_to_agent.touch()
        agent_to_caller.touch()

        # Configure agent's tell_user to write to agent_to_caller file
        def tell_user(agent_id: str, message: str) -> str:
            with open(agent_to_caller, 'a') as f:
                f.write(f"[{agent_id}] {message}\n")
                f.flush()
            agent.logger.info(f"[SUBAGENT_TELL_USER] {message}")
            return ""

        # Configure agent's ask_user to write to agent_to_caller and read from caller_to_agent
        def ask_user(agent_id: str, message: str) -> str:
            with open(agent_to_caller, 'a') as f:
                f.write(f"[{agent_id}] {message}\n")
                f.flush()
            agent.logger.info(f"[SUBAGENT_ASK_USER] {message}")

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

        agent.tell_user = tell_user
        agent.ask_user = ask_user

        # Run the agent in a separate thread so it doesn't block
        def run_agent_thread():
            try:
                agent.run()
            except Exception as e:
                agent.logger.error(f"Agent thread error: {str(e)}")

        agent_thread = threading.Thread(target=run_agent_thread, daemon=True)
        agent_thread.start()

        # Log that the agent has been started
        logging.info(f"Subagent {agent.id} started in background thread")

        return agent.id  # Return unique ID for this agent instance
    except Exception as e:
        raise ValueError(f"Failed to create agent instance: {str(e)}")
