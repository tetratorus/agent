from typing import Dict, Optional, Tuple, Callable, List, Any, Union
import litellm
import re
from .meta import AgentMeta

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
  """A flexible agent framework that manages conversations with an LLM while handling tool calls and memory management.

  Attributes:
    debug_verbose: If True, logs detailed information about method calls including inputs and outputs.
    model_name: Name of the language model to use.
    manifesto: A string that describes the agent's purpose and capabilities.
    memory: A string that represents the agent's initial memory state. Can be the empty string.
    tools: An optional dictionary of tool names to tool functions.
    _ask_user_impl: Function that handles user questions. Default prompts and gets input from console. Can be overridden.
    _tell_user_impl: Function that handles user answers. Default prints to console. Can be overridden.
    _log_handler_impl: Function that handles log messages. Default prints to console. Can be overridden.
    llm_call_count: Number of times the LLM has been called.
    llm: The LLM instance used by the agent.
    ended: If True, the agent has ended its conversation.

  """

  def __init__(
      self,
      manifesto: str,
      memory: str,
      tools: Dict[str, Callable],
      model_name: str = "openai/gpt-4o",
  ):
    """Initialize the agent with a manifesto and optional tools and functions.

    Args:
      model_name: Name of the language model to use
      manifesto: A string that describes the agent's purpose and capabilities.
      memory: A string that represents the agent's initial memory state. Can be the empty string.
      tools: An optional dictionary of tool names to tool functions.
      model_name: Name of the language model to use
    """
    self.llm_call_count = 0
    self.debug_verbose = False
    self.model_name = model_name
    self.manifesto = manifesto
    self.memory = memory
    self._log_handler_impl = lambda msg: (self.log_handler(msg), "")[1]
    self._ask_user_impl = lambda q: (self.log_handler(q), get_multiline_input())[1]
    self._tell_user_impl = lambda m: (self.log_handler(m), "")[1]
    self.ended = False

    # Merge provided tools with built-in tools
    self.tools = {
        "ASK_USER": self.ask_user,
        "TELL_USER": self.tell_user,
        "END_RUN": self.end_run,
        **(tools or {})
    }

    self._last_tool_called: Optional[str] = None

  def update_memory(self, text: str) -> None:
    # if memory tracing is not enabled, update memory directly
    self.memory = text

  def compose_request(self) -> str:
    return self.manifesto + "\n" + self.memory

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
      response = self.llm_call(self.compose_request())
      self.update_memory(self.memory + "\n[" + self.__class__.__name__ + " - " + str(self.llm_call_count) + "]\n" + response)

      # tool_detection
      tool_name, tool_args = self.tool_detection(response)
      if tool_name:
        if tool := self.tools.get(tool_name):
          self._last_tool_called = tool_name
          try:
            result = tool(tool_args)
            self.update_memory(self.memory + "\nTool Result [" + result + "]\n")
          except Exception as e:
            self.update_memory(self.memory + "\nTool Error [" + str(e) + "]\n")
        else:
          self.update_memory(self.memory + "\nTool Not Found [" + tool_name + "]\n")

      # check end condition at end of loop
      if self.ended:
        break

    return self.memory

  def end_run(self, _: str) -> str:
    self.ended = True
    return ""

  def ask_user(self, question: str) -> str:
    """Ask the user a question and return their response."""
    return self._ask_user_impl(question)

  def tell_user(self, message: str) -> str:
    """Tell the user a message."""
    return self._tell_user_impl(message)

  def log_handler(self, message: str) -> str:
    """Handle log messages."""
    return self._log_handler_impl(message)
