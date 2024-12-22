from typing import Dict, Optional, Callable, Tuple, List
import os
from lib.base import Agent
import json

class AgentCreatorAgent(Agent):
    """An agent that creates other agents by analyzing the codebase and gathering requirements.
    
    This agent follows a strict process:
    1. Keeps README as constant context for framework philosophy and guidelines
    2. Explores codebase structure using tree
    3. Analyzes implementation patterns from existing agents
    4. Gathers requirements through user interaction
    5. Generates agent implementation in order:
       - agent.py
       - test/test_runner.py 
       - variables/*.json files
    """
    
    def __init__(self, manifesto: str, memory: str = ""):
        # Initialize with tools needed for codebase analysis and file operations
        tools = {
            'VIEW_STRUCTURE': lambda _: self._view_structure(),
            'READ_FILE': lambda path: self._read_file(path),
            'WRITE_AGENT': lambda args: self._write_agent_file(args),
            'WRITE_TEST': lambda args: self._write_test_file(args),
            'WRITE_VARIABLES': lambda args: self._write_variables(args)
        }
        
        super().__init__(
            model_name="claude-3-5-sonnet-20240620",
            tools=tools,
            manifesto=manifesto,
            memory=memory,
            tool_detection=self._detect_tool
        )
        
        # Store README content as constant context
        self.readme = self._read_file("/Users/lentan/repo/ai/agent/README.md")
        
    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect tool calls in the model's response using XML format: <TOOL: TOOL_NAME>arguments</TOOL>"""
        import re
        pattern = r'<TOOL:\s*([A-Z_]+)>(.*?)</TOOL>'
        match = re.search(pattern, text, re.DOTALL)  # re.DOTALL to support multi-line args
        if match:
            tool_name, args = match.groups()
            if tool_name in self.tools:
                return tool_name, args.strip()
        return None, None

    def _view_structure(self) -> str:
        """Run tree command to view project structure."""
        import subprocess
        result = subprocess.run(['tree', '/Users/lentan/repo/ai/agent'], 
                              capture_output=True, text=True)
        return result.stdout

    def _read_file(self, path: str) -> str:
        """Read contents of a file."""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def _write_agent_file(self, args: str) -> str:
        """Write the agent.py implementation."""
        try:
            args_dict = json.loads(args)
            agent_dir = args_dict['dir']
            content = args_dict['content']
            
            os.makedirs(agent_dir, exist_ok=True)
            with open(os.path.join(agent_dir, 'agent.py'), 'w') as f:
                f.write(content)
            return "Successfully wrote agent.py"
        except Exception as e:
            return f"Error writing agent file: {str(e)}"

    def _write_test_file(self, args: str) -> str:
        """Write the test/test_runner.py file."""
        try:
            args_dict = json.loads(args)
            agent_dir = args_dict['dir']
            content = args_dict['content']
            
            test_dir = os.path.join(agent_dir, 'test')
            os.makedirs(test_dir, exist_ok=True)
            with open(os.path.join(test_dir, 'test_runner.py'), 'w') as f:
                f.write(content)
            return "Successfully wrote test_runner.py"
        except Exception as e:
            return f"Error writing test file: {str(e)}"

    def _write_variables(self, args: str) -> str:
        """Write the variables/*.json files."""
        try:
            args_dict = json.loads(args)
            agent_dir = args_dict['dir']
            variables = args_dict['variables']  # Dict of filename -> content
            
            var_dir = os.path.join(agent_dir, 'variables')
            os.makedirs(var_dir, exist_ok=True)
            
            for filename, content in variables.items():
                with open(os.path.join(var_dir, filename), 'w') as f:
                    json.dump(content, f, indent=2)
            return "Successfully wrote variable files"
        except Exception as e:
            return f"Error writing variable files: {str(e)}"
