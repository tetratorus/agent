from typing import Dict, Optional, Tuple, Callable, List, Any, Union
import llms
from .meta import AgentMeta

class Agent(metaclass=AgentMeta):
  """A flexible agent framework that manages conversations with an LLM while handling tool calls and memory management.

  This class implements an autonomous agent that calls an LLM in a loop to generate responses,
  execute tools based on the model's responses, and maintain a memory context. For debugging reasons, it also tracks
  a history of all memory states in _memory_trace.

  The agent is initialized with a manifesto that is provided to the LLM in every request, and a dictionary of tools that the agent can use.
  It has access to tools, which are custom functions that the agent can call to perform actions.
  The agent can also be configured with an end_detection function that determines when the agent should end its loop,
  a tool_detection function that determines when the agent should call a tool,
  and a memory_management function that processes and potentially updates the agent's memory after each interaction.

  Attributes:
      debug_verbose: If True, logs detailed information about method calls including inputs and outputs.
      log_handler: Function that handles log messages. Default prints to console. Can be overridden.
  """

  def __init__(
      self,
      model_name: str,
      manifesto: str,
      memory: str = "",
      tools: Optional[Dict[str, Callable]] = None,
      end_detection: Optional[Callable[[str, str], bool]] = None,
      tool_detection: Optional[Callable[[str], Tuple[Optional[str], Optional[str]]]] = None,
      memory_management: Optional[Callable[[str], Optional[str]]] = None,
      memory_tracing: bool = False,
  ):
    """Initialize the agent with a manifesto and optional tools and functions.

    Args:
      model_name: Name of the language model to use
      manifesto: A string that describes the agent's purpose and capabilities.
      memory: An optional string that represents the agent's initial memory state.
      tools: An optional dictionary of tool names to tool functions.
      end_detection: An optional function that takes a string and returns a boolean indicating whether the agent should end.
      tool_detection: An optional function that takes a string and returns a tuple of (tool_name, tool_args).
      memory_management: An optional function that takes a string and returns a string to update the agent's memory.
    """
    self.log_handler = lambda msg: print(msg)
    self.debug_verbose = False
    self.llm = llms.init(model_name)
    self.manifesto = manifesto
    self.memory = memory
    self._ask_user_impl = lambda q: input(q + "\nYour response: ")
    self._tell_user_impl = lambda m: self.log_handler(m)

    # Merge provided tools with built-in tools
    self.tools = {
        "ASK_USER": self.ask_user,
        "TELL_USER": self.tell_user,
        **(tools or {})
    }

    self.end_detection = end_detection
    self.tool_detection = tool_detection
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
    # no tool detection
    if not self.tool_detection:
      return None, None

    # call tool detection function
    tool_name, tool_args = self.tool_detection(text)

    # validate tool exists
    if tool_name and tool_name in self.tools:
      self._last_tool_called = tool_name
      return tool_name, tool_args
    elif tool_name:
      print(f"Warning: Tool {tool_name} not found in tools dictionary")
      return None, None
    else:
      return None, None

  def end(self) -> bool:
    if callable(self.end_detection):
      return self.end_detection(self.manifesto, self.memory)
    elif self._last_tool_called is None:
      return True

  def llm_call(self, prompt: str, **kwargs) -> str:
    return self.llm.complete(prompt, **kwargs).text

  def run(self) -> str:
    # agent loop
    while True:
      self._last_tool_called = None
      response = self.llm_call(self.compose_request())
      self.update_memory(self.memory + "\n" + self.__class__.__name__ + ": " + response)

      # tool_detection
      tool_name, tool_args = self.tool_detection(response)
      if tool_name:
        if tool := self.tools.get(tool_name):
          self._last_tool_called = tool_name
          result = tool(tool_args)
          self.update_memory(self.memory + "\nTool Result: " + result)
        else:
          self.update_memory(self.memory + "\nTool Not Found: " + tool_name)

      # check end condition at end of loop
      if self.end():
        break

    return self.memory

  def ask_user(self, question: str) -> str:
    """Ask the user a question and return their response."""
    return self._ask_user_impl(question)

  def tell_user(self, message: str) -> None:
    """Tell the user a message."""
    self._tell_user_impl(message)

  def override_ask_user(self, new_impl: Callable[[str], str]) -> None:
    """Override the ask_user implementation."""
    self._ask_user_impl = new_impl

  def override_tell_user(self, new_impl: Callable[[str], None]) -> None:
    """Override the tell_user implementation."""
    self._tell_user_impl = new_impl
