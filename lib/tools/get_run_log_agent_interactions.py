import os
import re
from typing import List, Dict, Any

def get_run_log_agent_interactions(caller_id: str, input_str: str) -> str:
    """Extract agent interactions from a run log file.
    
    This function extracts communication events between agents and users:
    - ASK_USER tool calls
    - TELL_USER tool calls
    - LISTEN_TO_SUBAGENT tool calls
    - RESPOND_TO_SUBAGENT tool calls
    
    Args:
        caller_id: ID of the calling agent
        input_str: String in format 'agent_name§log_file_name'
                   agent_name must match an existing agent
                   log_file_name is the name of the log file to analyze
    
    Returns:
        Formatted string with chronological list of all agent interactions
    """
    try:
        parts = input_str.split('§')
        if len(parts) != 2:
            return "Error: Input must be in format 'agent_name§log_file_name'"

        agent_name, log_file_name = parts
        
        # Get project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Construct path to run log
        log_file_path = os.path.join(project_root, 'runs', agent_name, log_file_name)
        
        # Add .txt extension if not provided
        if not log_file_path.endswith('.txt'):
            log_file_path += '.txt'
        
        # Check if run log exists
        if not os.path.isfile(log_file_path):
            return f"Error: Run log not found at {log_file_path}"
        
        # Extract events from the log file
        events = extract_agent_events(log_file_path)
        
        # Format the events as a string
        return format_agent_events(events)
        
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        return f"Error analyzing run log: {str(e)}\n\nStack trace:\n{stack_trace}"

def extract_agent_events(log_file_path: str) -> List[Dict[str, Any]]:
    """Extract specific agent tool calls from logs.
    
    This function extracts:
    - ASK_USER tool calls
    - TELL_USER tool calls
    - LISTEN_TO_SUBAGENT tool calls
    - RESPOND_TO_SUBAGENT tool calls
    
    Args:
        log_file_path: Path to the log file
        
    Returns:
        list: Chronological list of all tool calls
    """
    # Event list to store all tool calls
    events = []
    
    # Track current agent iterations
    agent_iterations = {}
    
    # Regular expressions for extracting information
    tool_pattern = re.compile(r'agent\.(\w+).*\[Tool: (ASK_USER|TELL_USER|LISTEN_TO_SUBAGENT|RESPOND_TO_SUBAGENT)\]')
    iteration_pattern = re.compile(r'\[(\w+).*? - LLM Response - Agent Iterations (\d+)\]')
    
    with open(log_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for iteration markers
            iteration_match = iteration_pattern.search(line)
            if iteration_match:
                agent_id = iteration_match.group(1)
                iteration_num = iteration_match.group(2)
                agent_iterations[agent_id] = iteration_num
            
            # Skip summary lines that only have length information
            if "Input Length:" in line and "Result Length:" in line:
                i += 1
                continue
                
            # Check if line contains a tool call with content
            tool_match = tool_pattern.search(line)
            if tool_match and "Input:" in line:
                agent_id = tool_match.group(1)
                tool_name = tool_match.group(2)
                
                # Get the line number
                line_num = i + 1
                
                # Get current iteration for this agent if available
                current_iteration = agent_iterations.get(agent_id)
                
                # Extract input and result parts
                parts = line.split("Input:", 1)[1]
                
                # Handle multiline inputs
                input_text = ""
                if " | Result:" in parts:
                    input_parts = parts.split(" | Result:", 1)
                    input_text = input_parts[0].strip()
                    result = input_parts[1].strip() if len(input_parts) > 1 else None
                else:
                    # This is a multiline input, collect until we find " | Result:"
                    input_text = parts.strip()
                    j = i + 1
                    while j < len(lines) and " | Result:" not in lines[j]:
                        input_text += "\n" + lines[j].strip()
                        j += 1
                    
                    # Now get the result if we found it
                    if j < len(lines) and " | Result:" in lines[j]:
                        result = lines[j].split(" | Result:", 1)[1].strip()
                        i = j  # Update our position
                    else:
                        result = None
                
                # Create event based on tool type
                if tool_name == "ASK_USER":
                    events.append({
                        'line_num': line_num,
                        'line': line,
                        'agent_id': agent_id,
                        'tool': 'ASK_USER',
                        'input': input_text,
                        'result': result,
                        'iteration': current_iteration
                    })
                elif tool_name == "TELL_USER":
                    events.append({
                        'line_num': line_num,
                        'line': line,
                        'agent_id': agent_id,
                        'tool': 'TELL_USER',
                        'input': input_text,
                        'iteration': current_iteration
                    })
                elif tool_name == "RESPOND_TO_SUBAGENT":
                    # Extract receiver and content
                    receiver_id = None
                    content = None
                    
                    if "§" in input_text:
                        parts = input_text.split("§", 1)
                        receiver_id = parts[0].strip()
                        content = parts[1] if len(parts) > 1 else None
                    
                    events.append({
                        'line_num': line_num,
                        'line': line,
                        'agent_id': agent_id,
                        'tool': 'RESPOND_TO_SUBAGENT',
                        'receiver_id': receiver_id,
                        'content': content,
                        'iteration': current_iteration
                    })
                elif tool_name == "LISTEN_TO_SUBAGENT":
                    events.append({
                        'line_num': line_num,
                        'line': line,
                        'agent_id': agent_id,
                        'tool': 'LISTEN_TO_SUBAGENT',
                        'target_id': input_text,
                        'result': result,
                        'iteration': current_iteration
                    })
            
            i += 1
    
    # Sort events by line number
    events.sort(key=lambda x: x['line_num'])
    
    return events

def format_agent_events(events: List[Dict[str, Any]]) -> str:
    """Format agent events into a chronological text report.
    
    Args:
        events: Events extracted with extract_agent_events
        
    Returns:
        str: Formatted chronological list of all agent interactions
    """
    if not events:
        return "No agent interactions found in the log."
    
    output = "=== AGENT COMMUNICATION (CHRONOLOGICAL) ===\n\n"
    
    for i, event in enumerate(events, 1):
        agent_id = event['agent_id']
        agent_short_id = agent_id.split('-')[0] if '-' in agent_id else agent_id
        
        # Format agent with iteration if available
        iteration_info = f" [Agent Iterations {event['iteration']}]" if event.get('iteration') else ""
        agent_display = f"{agent_short_id}{iteration_info}"
        
        if event['tool'] == 'ASK_USER':
            output += f"{i}. [Line {event['line_num']}] {agent_display} → User (ASK_USER)\n"
            output += f"   Question: {event['input']}\n"
            if event.get('result'):
                output += f"   Response: {event['result']}\n"
        
        elif event['tool'] == 'TELL_USER':
            output += f"{i}. [Line {event['line_num']}] {agent_display} → User (TELL_USER)\n"
            output += f"   Message: {event['input']}\n"
        
        elif event['tool'] == 'RESPOND_TO_SUBAGENT':
            receiver_id = event.get('receiver_id') or 'unknown'
            receiver_short_id = receiver_id.split('-')[0] if '-' in receiver_id else receiver_id
            output += f"{i}. [Line {event['line_num']}] {agent_display} → {receiver_short_id} (RESPOND_TO_SUBAGENT)\n"
            if event.get('content'):
                output += f"   Content: {event['content']}\n"
            else:
                output += f"   Content: [Empty or Multiline Content]\n"
        
        elif event['tool'] == 'LISTEN_TO_SUBAGENT':
            target_id = event.get('target_id') or 'unknown'
            target_short_id = target_id.split('-')[0] if '-' in target_id else target_id
            output += f"{i}. [Line {event['line_num']}] {agent_display} ← {target_short_id} (LISTEN_TO_SUBAGENT)\n"
            if event.get('result') and event['result'].strip():
                output += f"   Result: {event['result']}\n"
            else:
                output += f"   Result: No message received\n"
        
        output += "\n"
    
    return output