from .base import Agent
import os
import importlib.util
import sys

def create_agent(
    config: dict,
    manifesto: str,
    memory: str,
) -> Agent:
   """ Creates an agent """

   # Create a dictionary of tools by importing them from the tools directory
   tools_dict = {}
   tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
   
   for tool_name in config['tools']:
       # Convert tool name to lowercase filename
       filename = tool_name.lower() + '.py'
       filepath = os.path.join(tools_dir, filename)
       
       if os.path.exists(filepath):
           # Import the module dynamically
           module_name = f"lib.tools.{tool_name.lower()}"
           spec = importlib.util.spec_from_file_location(module_name, filepath)
           if spec and spec.loader:
               module = importlib.util.module_from_spec(spec)
               spec.loader.exec_module(module)
               
               # Get the function with the same name as the file (without .py)
               func_name = tool_name.lower()
               if hasattr(module, func_name):
                   tools_dict[tool_name] = getattr(module, func_name)
               else:
                   print(f"Warning: Function {func_name} not found in {filepath}")

   agent_params = {
        "manifesto": manifesto,
        "memory": memory,
        "tools": tools_dict,
        "name": config['name'],
   }

   if 'model' in config:
       agent_params["model"] = config['model']

   return Agent(**agent_params)
