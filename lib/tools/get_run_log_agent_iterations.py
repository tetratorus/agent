
import os
import re
from typing import Dict

def get_run_log_agent_iterations(caller_id: str, input_str: str) -> str:
    # input str is agent_name and run_log_name
    parts = input_str.split("§")
    if len(parts) < 2:
        return "Error: Input should be in format 'agent_name§run_log_name'"

    agent_name = parts[0]
    run_log_name = parts[1]

    # Get project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))

    # Construct path to run log
    run_log_path = os.path.join(project_root, 'runs', agent_name, run_log_name + '.txt')

    # Check if run log exists
    if not os.path.isfile(run_log_path):
        return f"Error: Run log not found at {run_log_path}. (Note: remember not to include .txt extension for the manifesto name)"

    try:
        # Read run log content
        with open(run_log_path, 'r', encoding='utf-8') as f:
            run_log_content = f.read()

        # Find all agent IDs and their max iterations
        iterations = {}
        
        # Pattern to match agent IDs in the format: PascalCaseNameAgent_HHMMSS-hextoken-
        # Example: AgentCreatorAgent_145648-560d4e50-
        # Look for "Agent Iterations N" pattern which is the standard format in logs
        pattern = r'\[([A-Z][a-z0-9]*(?:[A-Z][a-z0-9]*)*Agent_\d{6}-[0-9a-f]{8}-) - LLM Response - Agent Iterations (\d+)\]'
        
        # Find all matches and keep track of the maximum iteration for each agent
        for match in re.finditer(pattern, run_log_content):
            agent_id, iteration = match.groups()
            iterations[agent_id] = max(int(iteration), iterations.get(agent_id, 0))
        
        # Format the results
        if not iterations:
            return "No agent iterations found in the run log."
        
        result = "Agent Iterations:\n"
        for agent_id, max_iteration in sorted(iterations.items()):
            result += f"{agent_id}: Max Iteration: {max_iteration}\n"
        
        return result

    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        return f"Error reading run log: {str(e)}\n\nStack trace:\n{stack_trace}"
