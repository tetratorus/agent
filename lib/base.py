import llms
import re
import zlib


class Agent:
  """A flexible agent framework that manages conversations with an LLM while handling tool calls and memory management.

  This class implements an autonomous agent that calls an LLM in a loop to generate responses,
  execute tools based on the model's responses, and maintain a memory context. For debugging reasons, it also tracks
  a history of all memory states in _memory_trace.

  Execution loop:
  1. Call the LLM to generate a response
  2. Store the LLM's response in memory
  3. Check for tool calls in the LLM's response
  4. If a tool call is detected, call the tool and store the result in memory
  5. Check if the agent should end
  6. If the agent should end, return the final memory state
  7. Repeat steps 1-6 until the agent ends

  Args:
      model_name (str): Name of the language model to use
      tools (dict, optional): Dictionary mapping tool names to their callable implementations.
          Each tool should be a function that takes a string input and returns a string result.
      end_detection (callable, optional): Function that determines when to end the agent loop.
          Takes the current request context and returns a boolean. If None, ends when no tool is called.
      tool_detection (Union[str, callable], optional): Method to detect tool calls in LLM responses.
          Can be either a regex pattern string with two capture groups (tool name and input),
          or a function that takes response text and returns (tool_name, tool_input) tuple.
      memory_management (callable, optional): Function to process and potentially transform memory
          before storing. Takes the new text and returns processed text. If None, stores text as is.
      manifesto (str, optional): Static context provided to the LLM in every request.
      memory (str, optional): Initial memory/context for the conversation.

  Attributes:
      memory (str): Current conversation context
      _memory_trace (list): Compressed history of all memory states
      _last_tool_called (str): Name of the last tool that was called, or None if no tool was called

  The agent maintains its conversation history in two forms:
  1. Current memory (uncompressed) for immediate access
  2. Complete history trace (compressed using zlib) for efficient storage
  """

  def __init__(self,
               model_name,
               tools={},
               end_detection=None,
               tool_detection=None,
               memory_management=None,
               manifesto="",
               memory=""):
    self.llm = llms.init(model_name)
    self.end_detection = end_detection
    self.tools = tools
    self.tool_detection = tool_detection
    self.end_detection = end_detection
    self.memory_management = memory_management
    self.manifesto = manifesto
    self.memory = memory
    self._memory_trace = []
    self._last_tool_called = None

  def _compress_text(self, text):
    return zlib.compress(text.encode('utf-8'))

  def _decompress_bytes(self, compressed_bytes):
    return zlib.decompress(compressed_bytes).decode('utf-8')

  def update_memory(self, text):
    # Decompress existing traces if they exist
    decompressed_traces = [self._decompress_bytes(trace) if isinstance(trace, bytes) else trace for trace in self._memory_trace]
    decompressed_traces.append(self.memory)
    # Compress all traces
    self._memory_trace = [self._compress_text(trace) for trace in decompressed_traces]
    if callable(self.memory_management):
      self.memory = self.memory_management(text)
    else:
      self.memory = text

  def compose_request(self):
    return "\nManifesto: " + self.manifesto + "\nMemory:" + self.memory

  def tool_detection(self, text):
    # no tool detection
    if not self.tool_detection:
      return None, None
    # check if tool detection is a regex
    elif isinstance(self.tool_detection, str):
      match = re.search(self.tool_detection, text)
      if match:
        tool_name = match.group(1)
        tool_input = match.group(2)
        return tool_name, tool_input
      else:
        return None, None
    # check if tool detection is a function
    elif callable(self.tool_detection):
      tool_name, tool_input = self.tool_detection(text)
      return tool_name, tool_input
    else:
      return None, None

  def end(self):
    if callable(self.end_detection):
      return self.end_detection(self.compose_request())

    # default to end if no last tool called
    elif self._last_tool_called is None:
      return True
    else:
      return False

  async def run(self):
    # agent loop
    while not self.end():
      self._last_tool_called = None
      response = await self.llm.complete(self.compose_request())
      self.update_memory(self.memory + "\nAssistant: " + response.text)
      # tool_detection
      tool_name, tool_input = self.tool_detection(response.text)
      if tool_name:
        if tool := self.tools.get(tool_name):
          self._last_tool_called = tool_name
          result = tool(tool_input)
          self.update_memory(self.memory + "\nTool Result: " + result)
        else:
          self.update_memory(self.memory + "\nTool Not Found: " + tool_name)

    # return last response
    return self.memory
