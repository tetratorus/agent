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

class Agent(metaclass=AgentMeta):
  """A flexible agent framework that manages conversations with an LLM while handling tool calls and memory management.

  This code defines an Agent that repeatedly calls an LLM using a manifesto (system instructions) and memory as context.
  After each LLM response, it checks for a special <TOOL: NAME> tag.
  If found, it calls the corresponding Python function (“tool”), updates its memory with the tool’s result, and continues.
  The agent ends when an END_RUN tool call appears.

  Implementations of agents MUST extend `lib.base.Agent`, they cannot override any of the methods except __init__.
  `lib.base.Agent` implements a base agent loop, and has access to ASK_USER, TELL_USER, and END_RUN tools.
  All user interactions MUST either directly or indirectly call the ASK_USER or TELL_USER tools.
  When the agent is complete, the agent MUST call the END_RUN tool.
  Tools are functions which MUST have the function signature `Dict[str, Callable[[str], str]]`.
  Tool calls MUST follow the format `<TOOL: TOOL_NAME>TOOL_INPUT</TOOL>`.
  Similarly, tool detection MUST be via regex pattern matching (e.g., `r'<TOOL: ([A-Z_]+)>(.*?)</TOOL>'`).
  Manifesto are custom instructions for the agent and provide a flexible way to control the agent's behavior.
  Memory provides the context for the conversation and is updated as the agent runs.

  Attributes:
      debug_verbose: If True, logs detailed information about method calls including inputs and outputs.
      log_handler: Function that handles log messages. Default prints to console. Can be overridden.
  """

  def __init__(
      self,
      manifesto: str,
      memory: str,
      model_name: str = "openai/gpt-4o",
      tools: Optional[Dict[str, Callable]] = None,
      memory_management: Optional[Callable[[str], Optional[str]]] = None,
      memory_tracing: bool = False,
  ):
    """Initialize the agent with a manifesto and optional tools and functions.

    Args:
      model_name: Name of the language model to use
      manifesto: A string that describes the agent's purpose and capabilities.
      memory: A string that represents the agent's initial memory state. Can be empty
      tools: An optional dictionary of tool names to tool functions.
      memory_management: An optional function that takes a string and returns a string to update the agent's memory.
      memory_tracing: If True, memory tracing is enabled. Defaults to False
    """
    self.llm_call_count = 0
    self.log_handler = lambda msg: print(msg)
    self.debug_verbose = False
    self.model_name = model_name
    self.manifesto = manifesto
    self.memory = memory
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

    self.memory_management = memory_management
    self._memory_trace: List[str] = []
    self._last_tool_called: Optional[str] = None
    self.memory_tracing = memory_tracing

  def get_memory_trace(self) -> List[str]:
    return self._memory_trace

  def override_log_handler(self, new_impl: Callable[[str], None]) -> None:
    self.log_handler = new_impl

  def update_memory(self, text: str) -> None:
    # if memory tracing is not enabled, update memory directly
    if not self.memory_tracing:
      if callable(self.memory_management):
        self.memory = self.memory_management(text)
      else:
        self.memory = text
      return

    # else update memory and memory trace
    self._memory_trace.append(self.memory)

    # Update memory based on memory management function
    if callable(self.memory_management):
      self.memory = self.memory_management(text)
    else:
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

  def override_ask_user(self, new_impl: Callable[[str], str]) -> None:
    """Override the ask_user implementation."""
    self._ask_user_impl = new_impl

  def override_tell_user(self, new_impl: Callable[[str], str]) -> None:
    """Override the tell_user implementation."""
    self._tell_user_impl = new_impl
