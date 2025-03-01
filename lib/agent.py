from .base import Agent
from lib.tools import *  # Import all available tools

def create_agent(
    config: dict,
    manifesto: str,
    memory: str,
) -> Agent:
   """ Creates an agent """

   # Create a dictionary of tools by filtering globals based on config['tools']
   tools_dict = {}
   for tool_name in config['tools']:
       if tool_name in globals():
           tools_dict[tool_name] = globals()[tool_name]

   agent_params = {
        "manifesto": manifesto,
        "memory": memory,
        "tools": tools_dict,
        "name": config['name'],
   }

   if 'model' in config:
       agent_params["model"] = config['model']

   return Agent(**agent_params)
