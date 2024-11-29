import llms
import re
import zlib

class Agent:

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
