import os
import json
from typing import Dict, Optional, Tuple, Any
from lib.base import Agent

class VariableGenerationAgent(Agent):
    """Agent that generates variations of another agent's variables.
    
    Given a target agent's code and variables, analyzes its purpose and generates
    meaningful variations of its variables while preserving core functionality.
    
    Args:
        manifesto: Custom instructions for the agent
        target_agent: Name of the agent to generate variations for
        memory: Initial memory/context for the conversation
    """
    
    def __init__(
        self,
        manifesto: str,
        target_agent: str,
        memory: str = "",
    ):
        if manifesto is None:
            raise ValueError("Manifesto must be provided")
        if target_agent is None:
            raise ValueError("Target agent must be provided")
            
        model_name = "claude-3-5-sonnet-20240620"  # Using claude-3-5-sonnet-20240620 for high quality variations
        
        super().__init__(
            model_name=model_name,
            manifesto=manifesto,
            memory=memory,
            tools={
                "read_file": self._read_file,
                "list_variables": self._list_variables,
                "save_variation": self._save_variation,
            }
        )
        self.target_agent = target_agent
        self.agent_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents", target_agent)
        
    def _read_file(self, path: str) -> str:
        """Read a file's contents."""
        try:
            with open(os.path.join(self.agent_dir, path)) as f:
                return f.read()
        except Exception as e:
            return f"Error reading {path}: {e}"
            
    def _list_variables(self, _: str) -> str:
        """List all variable files in the variables directory."""
        var_dir = os.path.join(self.agent_dir, "variables")
        try:
            files = [f[:-5] for f in os.listdir(var_dir) if f.endswith('.json')]
            return json.dumps(files)
        except Exception as e:
            return f"Error listing variables: {e}"
            
    def _save_variation(self, data: str) -> str:
        """Save a variation of a variable.
        Format: {"name": "var_name", "index": 0, "content": "new content"}
        """
        try:
            data = json.loads(data)
            var_path = os.path.join(self.agent_dir, "variables", f"{data['name']}.json")
            
            with open(var_path) as f:
                variations = json.load(f)
                
            variations[data["index"]] = data["content"]
            
            with open(var_path, "w") as f:
                json.dump(variations, f, indent=2)
                
            return f"Saved variation {data['index']} for {data['name']}"
        except Exception as e:
            return f"Error saving variation: {e}"
            
    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect tool calls in the agent's response."""
        if "I need to read" in text.lower() and ".json" not in text:
            # Read agent code or other files
            path = text.split("read")[-1].strip().strip(".'\"")
            return "read_file", path
            
        if "list the variable files" in text.lower():
            return "list_variables", ""
            
        if "save this variation" in text.lower():
            # Extract the JSON data that follows
            try:
                start = text.find("{")
                end = text.find("}") + 1
                if start >= 0 and end > 0:
                    return "save_variation", text[start:end]
            except:
                pass
                
        return None, None
