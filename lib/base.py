import llms

class Agent:

  def __init__(self, model_name, tools, agent_instructions):
    self.llm = llms.init(model_name)
    self.tools = tools
    self.agent_instructions = agent_instructions
    self.memory_trace = []
    self.memory = ""

  async def run(self, user_input):
    self.memory += f"User: {user_input}\n"
    self.memory_trace.append(self.memory)
    while True:
      response = await self.llm.complete(self.agent_instructions + self.memory)
      self.memory += f"Assistant: {response.text}"
      if "<<TOOL:" in response.text:
        tool_name = response.text.split("<<TOOL:")[1].split(">>")[0]
        tool_input = response.text.split("<<TOOL:")[1].split(">>")[1].split("<<END>>")[0]
        if tool := self.tools.get(tool_name):
          result = tool(tool_input)
          self.memory.append(f"Tool Result: {result}")
          continue
      if "<<TASK_COMPLETE>>" in response.text:
        return response.text
