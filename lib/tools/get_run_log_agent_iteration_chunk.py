import os
import re
from typing import Dict, List, Tuple
from pathlib import Path

def get_run_log_agent_iteration_chunk(caller_id: str, input_str: str, banner_index: int = -1) -> str:
    def filter_content_by_agent_id(content: str, agent_id: str) -> str:
        """Filter content to only include lines related to the specified agent ID.

        If a line doesn't have a prefix, look at previous lines until a prefix is found.
        If no prefix is found in previous lines, assign 'NO_PREFIX'.
        """
        lines = content.split('\n')
        # Debug prints removed

        filtered_lines = []

        # Dictionary to keep track of line prefixes
        line_prefixes = {}
        current_prefix = "NO_PREFIX"

        # First pass: assign prefixes to each line
        for i, line in enumerate(lines):
            # Check if line has a prefix using the agent ID pattern
            prefix_match = re.search(r'\[([A-Z][a-z0-9]*(?:[A-Z][a-z0-9]*)*Agent_\d{6}-[0-9a-f]{8}-)', line)

            if prefix_match:
                # Line has a prefix, use it
                current_prefix = prefix_match.group(1)

            # Store the prefix for this line
            line_prefixes[i] = current_prefix

        # Second pass: filter lines by the specified agent ID
        for i, line in enumerate(lines):
            # Keep the line only if its prefix matches the agent ID
            if agent_id in line_prefixes[i]:
                filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    # input str is agent_name§run_log_name§agent_Id§iteration_number
    parts = input_str.split('§')
    if len(parts) != 4:
        return "Error: Input should be in format 'agent_name§run_log_name§agent_Id§iteration_number'"

    agent_name, run_log_name, agent_id, iteration_str = parts

    try:
        iteration = int(iteration_str)
    except ValueError:
        return "Error: Iteration number must be an integer"

    # Default to last banner if banner_index is negative
    use_last_banner = banner_index < 0

    # Get project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))

    # Construct path to run log
    run_log_path = os.path.join(project_root, 'runs', agent_name, run_log_name + '.txt')

    # Check if run log exists
    if not os.path.isfile(run_log_path):
        return f"Error: Run log not found at {run_log_path}"

    try:
        # Read run log content
        with open(run_log_path, 'r', encoding='utf-8') as f:
            run_log_content = f.read()

        # Pattern to match iteration banners for the specific agent
        # The format is [AgentID - LLM Response - Agent Iterations X]
        pattern = rf'\[{agent_id} - LLM Response - Agent Iterations (\d+)\]'

        # Find all matches
        matches = list(re.finditer(pattern, run_log_content))

        # Group matches by iteration number
        iteration_matches: Dict[int, List[Tuple[int, int]]] = {}
        for match in matches:
            match_iteration = int(match.group(1))
            match_position = match.start()

            if match_iteration not in iteration_matches:
                iteration_matches[match_iteration] = []

            iteration_matches[match_iteration].append((match_position, len(match.group(0))))

        current_iteration = iteration
        previous_iteration = current_iteration - 1

        if current_iteration not in iteration_matches:
            return f"Error: Could not find iteration {current_iteration} banners for agent {agent_id}"

        # Sort positions for each iteration
        for iter_num in iteration_matches:
            iteration_matches[iter_num].sort()

        # Determine which banner to use
        if iteration == 1:
            # For iteration 1, we start from the first banner and go to the last banner (or specified banner)
            if len(iteration_matches[1]) < 1:
                return f"Error: Could not find any banners for iteration 1"

            # Start from the first banner
            start_pos = iteration_matches[1][0][0]

            # If use_last_banner is True, use the last banner, otherwise use the specified index
            banner_to_use = len(iteration_matches[1]) - 1 if use_last_banner else min(banner_index, len(iteration_matches[1]) - 1)

            if banner_to_use < 0 or banner_to_use >= len(iteration_matches[1]):
                return f"Error: Banner index {banner_to_use} is out of range for iteration 1 (has {len(iteration_matches[1])} banners)"

            end_banner_pos, end_banner_len = iteration_matches[1][banner_to_use]
            end_pos = end_banner_pos + end_banner_len
        else:
            # For other iterations, we need both the previous and current iterations
            if previous_iteration not in iteration_matches:
                return f"Error: Could not find iteration {previous_iteration} banners for agent {agent_id}"

            # Check if both iterations have banners
            if not iteration_matches[current_iteration] or not iteration_matches[previous_iteration]:
                return f"Error: One of the iterations has no banners"

            # If use_last_banner is True, use the last banner, otherwise use the specified index
            prev_banner_to_use = len(iteration_matches[previous_iteration]) - 1 if use_last_banner else min(banner_index, len(iteration_matches[previous_iteration]) - 1)
            curr_banner_to_use = len(iteration_matches[current_iteration]) - 1 if use_last_banner else min(banner_index, len(iteration_matches[current_iteration]) - 1)

            if prev_banner_to_use < 0 or prev_banner_to_use >= len(iteration_matches[previous_iteration]):
                return f"Error: Banner index {prev_banner_to_use} is out of range for iteration {previous_iteration} (has {len(iteration_matches[previous_iteration])} banners)"

            if curr_banner_to_use < 0 or curr_banner_to_use >= len(iteration_matches[current_iteration]):
                return f"Error: Banner index {curr_banner_to_use} is out of range for iteration {current_iteration} (has {len(iteration_matches[current_iteration])} banners)"

            # Get positions of the banners
            prev_banner_pos, prev_banner_len = iteration_matches[previous_iteration][prev_banner_to_use]
            curr_banner_pos, curr_banner_len = iteration_matches[current_iteration][curr_banner_to_use]

            # Extract content between the banners
            # Include both banners in the output
            start_pos = prev_banner_pos  # Start from the previous banner
            end_pos = curr_banner_pos + curr_banner_len

        # print("WHAT IS THE START POS AND END POS LINE NUMBERS")
        # # Calculate line numbers for start and end positions
        # start_line = run_log_content[:start_pos].count('\n') + 1
        # end_line = run_log_content[:end_pos].count('\n') + 1
        # print(f"Start position line number: {start_line}")
        # print(f"End position line number: {end_line}")

        content = run_log_content[start_pos:end_pos]
        return filter_content_by_agent_id(content, agent_id)

    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        return f"Error processing run log: {str(e)}\n\nStack trace:\n{stack_trace}"



