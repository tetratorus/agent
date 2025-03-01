from .base import Agent
import os
import importlib.util

def create_agent(
    config: dict,
    manifesto: str,
    memory: str,
) -> Agent:
   """ Creates an agent """

   # Create a dictionary of tools by importing them from the tools directory
   tools_dict = {}
   tools_dir = os.path.join(os.path.dirname(__file__), 'tools')

   # Handle wildcard "*" to include all tools
   if "*" in config['tools']:
       # Get all Python files in the tools directory
       tool_files = [f[:-3].upper() for f in os.listdir(tools_dir) if f.endswith('.py')]
       tools_to_load = tool_files
   else:
       tools_to_load = config['tools']

   for tool_name in tools_to_load:
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
