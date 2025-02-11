from typing import Dict, Optional, Tuple, Callable, List, Any, Union
import litellm
import re

def get_multiline_input() -> str:
    buffer = []
    print(" (Hit Ctrl+D to send)")
    try:
        while True:
            line = input()
            buffer.append(line)
    except EOFError:  # Handles Ctrl+D
        pass
    return '\n'.join(buffer)

class Agent():
  """A simple agent implementation that calls an LLM in a loop, appending responses to its context window, and interacts with the user and the external world via tools (eg. ASK_USER, TELL_USER, END_RUN).
  """

  def __init__(
      self,
      manifesto: str,
      memory: str,
      tools: Dict[str, Callable],
      model_name: str = "openai/gpt-4o",
  ):
    """Initialize the agent with a manifesto and optional tools and functions.
    """
    self.llm_call_count = 0
    self.debug_verbose = False
    self.model_name = model_name
    self.manifesto = manifesto
    self.memory = memory
    self.log_handler = lambda msg: print(msg)
    self.ask_user = lambda q: (self.log_handler(q), get_multiline_input())[1]
    self.tell_user = lambda m: (self.log_handler(m), "")[1]
    self.end_run = lambda _: (setattr(self, "ended", True), "")[1]

    self.ended = False

    # Merge provided tools with default tools
    self.tools = {
        "ASK_USER": self.ask_user,
        "TELL_USER": self.tell_user,
        "END_RUN": self.end_run,
        **(tools or {})
    }

    self._last_tool_called: Optional[str] = None

  def update_memory(self, text: str) -> None:
    self.memory = text

  def tool_detection(self, text: str) -> Tuple[Optional[str], Optional[str]]:
    """Detect if there is a tool call in the text and return the tool name and input."""
    pattern = r'<TOOL: ([A-Z_]+)>([\s\S]*?)</TOOL>'
    match = re.search(pattern, text)
    if match:
        return match.group(1), match.group(2)
    return None, None

  def llm_call(self, prompt: str, **kwargs) -> str:
    self.llm_call_count += 1
    return litellm.completion(
      model=self.model_name,
      messages=[{"role": "user", "content": prompt}],
      **kwargs
    ).choices[0].message.content

  def run(self) -> str:
    # agent loop
    while True:
      self._last_tool_called = None
      response = self.llm_call(self.manifesto + "\n" + self.memory)
      self.memory += "\n[" + self.__class__.__name__ + " - " + str(self.llm_call_count) + "]\n" + response

      # tool_detection
      tool_name, tool_args = self.tool_detection(response)
      if tool_name:
        if tool := self.tools.get(tool_name):
          self._last_tool_called = tool_name
          try:
            result = tool(tool_args)
            self.memory += "\nTool Result [" + result + "]\n"
          except Exception as e:
            self.memory += "\nTool Error [" + str(e) + "]\n"
        else:
          self.update_memory(self.memory + "\nTool Not Found [" + tool_name + "]\n")

      # check end condition
      if self.ended:
        break

    return self.memory
