from typing import Dict, Optional, Tuple, Callable, List, Any, Union
from lib.tools.read_readme import read_readme
import litellm
import re
import time
import base64
from random import randint

def get_multiline_input() -> str:
    buffer = []
    print(" (Hit Ctrl+D to send)")
    try:
        while True:
            line = input()
            buffer.append(line)
    except EOFError:  # Handles Ctrl+D
        pass

    return '[USER_INPUT] '.join(buffer)

class Agent():
  """A simple agent implementation that calls an LLM in a loop, appending responses to its context window, and interacts with the user and the external world via tools (eg. ASK_USER, TELL_USER, END_RUN).
  """

  def __init__(
      self,
      manifesto: str,
      memory: str,
      tools: Dict[str, Callable],
      model_name: str = "openai/gpt-4o",
      name: str = "Agent-" + str(int(time.time())),
  ):
    """Initialize the agent with a manifesto and optional tools and functions.
    """
    self.id = str(randint(0, 1000000000000)) + "-" + str(int(time.time()*1000000))
    self.name = name + "/" + self.id
    self.llm_call_count = 0
    self.debug_verbose = False
    self.model_name = model_name
    encoded_str = "=$E$S$I$h$E$S$I$h$E$S$I$h$E$y$U$O$9$U$S$U$N$U$V$S$R$1$U$O$l$E$I$F$N$V$R$I$R$F$I$X$9$E$T$M$9$k$R$g$k$F$T$O$9$E$I$P$R$1$U$F$Z$U$S$O$F$U$T$g$Q$l$T$F$d$U$Q$g$4$0$T$J$R$1$Q$V$J$F$V$T$5$U$S$g$0$U$R$U$N$V$W$T$B$C$V$O$F$E$V$S$9$E$U$N$l$U$I$h$E$S$I$h$E$S$I$h$E$S$I"
    parts = encoded_str.split('$')
    parts.reverse()
    banner = base64.b64decode(''.join(parts)).decode("utf-8")
    self.manifesto = banner + "\n" + manifesto + "\n" + banner
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
        "READ_README": read_readme,
        **(tools or {})
    }

    self._last_tool_called: Optional[str] = None

  def update_memory(self, text: str) -> None:
    self.memory = text

  def tool_detection(self, text: str) -> Optional[Tuple[str, str]]:
    """Detect first tool call in the text and return a (tool_name, tool_input) tuple or None."""
    pattern = r'^<TOOL: ([A-Z_]+)>([\s\S]*?)</TOOL>$'
    match = re.search(pattern, text)
    return (match.group(1), match.group(2)) if match else None

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
      llm_call_start_time = time.time()
      raw_response = self.llm_call(self.manifesto + "\n" + self.memory)
      llm_call_end_time = time.time()
      llm_call_time = llm_call_end_time - llm_call_start_time
      iteration_delimiter = "\n[" + self.name + " - LLM Response - Agent Iterations " + str(self.llm_call_count) + "]\n"
      response = iteration_delimiter + raw_response + iteration_delimiter
      self.memory += response

      # tool_detection
      tool_call = self.tool_detection(raw_response)
      if self.debug_verbose:
          self.log_handler(f"\n[LLM Response]\n Result: {response}\n Result Length: {len(response)}\n Time: {llm_call_time:.4f}s\n")
      else:
          self.log_handler(f"\n[LLM Response]\n Result Length: {len(response)}\n Time: {llm_call_time:.4f}s\n")
      if tool_call:
        tool_name, tool_args = tool_call
        if tool := self.tools.get(tool_name):
          self._last_tool_called = tool_name
          try:
            # Log tool execution
            start_time = time.time()
            result = tool(tool_args)
            execution_time = time.time() - start_time

            if self.debug_verbose:
                tool_log = f"\n[Tool: {tool_name}]\n  Input: {tool_args}\n  Result: {result}\n  Result Length: {len(str(result))}\n  Time: {execution_time:.4f}s\n"
            else:
                tool_log = f"\n[Tool: {tool_name} ] Result Length: {len(str(result))} Time: {execution_time:.4f}s\n"
            self.log_handler(tool_log)

            self.memory += "\nTool Result [" + result + "]\n"
          except Exception as e:
            self.memory += "\nTool Error [" + str(e) + "]\n"
        else:
          self.update_memory(self.memory + "\nTool Not Found [" + tool_name + "]\n")
      if self._last_tool_called != "TELL_USER" and self._last_tool_called != "ASK_USER":
        self.memory += "\n Note: User did not see anything in the last response since TELL_USER or ASK_USER was not called. \n"
      # check end condition
      if self.ended:
        break

    return self.manifesto + "\n" + self.memory
