from typing import Dict, Optional, Tuple, Callable
import logging
from lib.tools.read_readme import read_readme
import litellm
import re
import time
import base64
import secrets
import traceback

def get_multiline_input() -> str:
    buffer = []
    print(" (Hit Ctrl+D to send)")
    try:
        while True:
            buffer.append(input())
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
      name: str,
      tools: Dict[str, Callable],
      model_name: str = "openai/gpt-4o",
  ):
    """Initialize the agent with a manifesto and optional tools and functions.
    """
    self.id = name + "_" + time.strftime("%H%M%S") + "-" + secrets.token_hex(4) + "-"
    self.llm_call_count = 0
    self.model_name = model_name
    encoded_str = "=$=$Q$I$h$E$S$I$X$9$E$T$M$9$k$R$g$Q$1$U$V$1$E$I$P$R$1$U$F$Z$U$S$O$F$U$T$g$Q$l$T$F$d$U$Q$g$4$0$T$J$R$1$Q$V$J$F$V$T$5$U$S$g$0$U$R$U$N$V$W$T$B$C$V$O$F$E$V$S$9$E$U$N$l$U$I$h$E$S$I"
    parts = encoded_str.split('$')
    parts.reverse()
    banner = base64.b64decode(''.join(parts)).decode("utf-8")
    self.manifesto = banner + "\n" + manifesto + "\n" + banner
    self.memory = memory
    self.logger = logging.getLogger(f'agent.{self.id}')
    self.log_handler = lambda msg: self.logger.info(msg)
    self.ask_user = lambda _, q: (self.logger.info(f"[ASK_USER] {q}"), get_multiline_input())[1]
    self.tell_user = lambda _, m: (self.logger.info(f"[TELL_USER] {m}"), "")[1]
    self.end_run = lambda _, x: (setattr(self, "ended", True), "")[1]
    self.ended = False

    # Merge provided tools with default tools
    self.tools = {
        "ASK_USER": lambda agent_id, args: self.ask_user(agent_id, args),
        "TELL_USER": lambda agent_id, args: self.tell_user(agent_id, args),
        "END_RUN": lambda agent_id, args: self.end_run(agent_id, args),
        "READ_README": read_readme,
        **(tools or {})
    }
    self._last_tool_called = None

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
      llm_call_time = time.time() - llm_call_start_time
      iteration_delimiter = f"\n[{self.id} - LLM Response - Agent Iterations {self.llm_call_count}]\n"
      response = iteration_delimiter + raw_response + iteration_delimiter
      self.memory += response
      self.logger.info(f"[LLM Response] Length: {len(response)} | Time: {llm_call_time:.4f}s")
      self.logger.debug(f"[LLM Response] Result: {response}")

      # tool_detection
      tool_call = self.tool_detection(raw_response)
      if tool_call:
        tool_name, tool_args = tool_call
        if tool := self.tools.get(tool_name):
          self._last_tool_called = tool_name
          try:
            start_time = time.time()
            result = tool(self.id, tool_args)
            execution_time = time.time() - start_time
            self.logger.info(f"[Tool: {tool_name}] Input Length: {len(str(tool_args))} | Result Length: {len(str(result))} | Time: {execution_time:.4f}s")
            self.logger.debug(f"[Tool: {tool_name}] Input: {tool_args} | Result: {result}")
            self.memory += f"\nTool Result [Tool: {tool_name}] Input: {tool_args} | Result: {result} | Time: {execution_time:.4f}s\n"
          except Exception as e:
            self.logger.info(f"Tool Error: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.memory += f"\nTool Error: {str(e)}\n"
        else:
          error_message = f"Tool Not Found: {tool_call[0]}"
          self.logger.info(error_message)
          self.memory += f"\n{error_message}\n"
      else:
        no_tool_message = "No tool call detected in LLM response based on exact regex match."
        self.logger.info(no_tool_message)
        self.memory += f"\n{no_tool_message}\n"

      if self._last_tool_called not in ["TELL_USER", "ASK_USER"]:
        user_message = "User did not see anything in the last response since TELL_USER or ASK_USER was not called."
        self.logger.info(user_message)
        self.memory += f"\n Note: {user_message} \n"

      if self.ended:
        self.logger.debug(f"[Agent {self.id}] Ended")
        self.logger.debug(f"[Manifesto]\n{self.manifesto}] \n[Memory]\n {self.memory}\n")
        break

    return self.manifesto + "\n" + self.memory
