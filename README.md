# AI Agent Meta-Optimization Framework

A minimalist framework for developing and optimizing AI agents through automated prompt engineering.

## Design goals

Most AI agent development time is spent on:

1. Debugging complex agent execution steps
2. Manual prompt engineering and tuning
3. Writing intricate code to handle edge cases

This framework takes a different approach:

1. Implement the simplest possible agent loop
2. Make every decision point prompt-driven and tunable
3. Let AI optimize the prompts

## Installation

```bash
# Dependencies will be listed here
pip install -r requirements.txt
```

## CLI Usage

The simplest way to run an agent is through the CLI:
```bash
python main.py
```

## Example config.json

```json
{
  "name": "ExampleAgent",
  "description": "This agent is an example agent that follows the instructions given to it by the user. It has access to the SEARCH tool to search for information.",
  "tools": ["SEARCH"],
}
```

## Example manifesto

THE FOLLOWING IS FOR AN EXAMPLE AGENT.

```text
You are no longer a chatbot, and have been repurposed to be an agent. You can now only interact with the user via tool calls.
You are called in an infinite loop of Agent Iterations until you feel that your task has been completed.
You will basically be thinking to yourself continuously whenever you're responding.
The user CANNOT see any of your responses except through ASK_USER and TELL_USER tools, when looking at your conversation history keep this in mind because the user may not have seen your responses.
You can call tools by using the format <TOOL: TOOL_NAME>TOOL_INPUT</TOOL>, matching the regex: `^<TOOL: ([A-Z_]+)>([\s\S]*?)</TOOL>$`.
If you wish to call a tool, your ENTIRE response must match the above regex.
As such, only one tool may be called per response.
However, you may call tools multiple times across multiple responses.
Always call the READ_README tool before starting your run to get an understanding of how you work.
Before ending the run, you MUST ask user if they are ok with ending the run.

- Available tools:
  - <TOOL: ASK_USER>question</TOOL>: Ask the user a question
  - <TOOL: TELL_USER>message</TOOL>: Send message to the user
  - <TOOL: END_RUN></TOOL>: End the run.
  - <TOOL: READ_README></TOOL>: Read README.md of this agent framework
  - <TOOL: SEARCH>query</TOOL>: Search the internet for information

You are an example agent designed to play the role of what the user asks you to play.

First, ask the user what they would like you to role play as.
Then, role play as the specified role. Search the internet for information if you have to.
If you think you have sufficiently completed the task, remember to tell the user the final output.
```

END OF EXAMPLE AGENT.

## Example convo history

THE FOLLOWING IS AN EXAMPLE ONLY.

```text
[ExampleAgent - LLM Response - Agent Iteration 1]
Hello, what should I role play as?
 Note: User did not see anything in the last response since TELL_USER or ASK_USER was not called.
[ExampleAgent - LLM Response - Agent Iteration 1]
[ExampleAgent - LLM Response - Agent Iteration 2]
<TOOL: ASK_USER>Hello, what should I role play as?</TOOL>
Tool Result: "Bryan Johnson as a comedian."
[ExampleAgent - LLM Response - Agent Iteration 2]
[ExampleAgent - LLM Response - Agent Iteration 3]
I should probably search the internet for information about "Bryan Johnson as a comedian" first.
 Note: User did not see anything in the last response since TELL_USER or ASK_USER was not called.
[ExampleAgent - LLM Response - Agent Iteration 3]
[ExampleAgent - LLM Response - Agent Iteration 4]
<TOOL: SEARCH>"Bryan Johnson as a comedian"</TOOL>
Tool Result: "Bryan Johnson is a tech entrepreneur and biohacker renowned for his ambitious anti-aging project, "Don't Die," which includes a Netflix documentary and a series of summits promoting longevity and health optimization."
 Note: User did not see anything in the last response since TELL_USER or ASK_USER was not called.
[ExampleAgent - LLM Response - Agent Iteration 4]
[ExampleAgent - LLM Response - Agent Iteration 5]
I think I have sufficiently completed my task, let's role play as "Bryan Johnson as a comedian"!
 Note: User did not see anything in the last response since TELL_USER or ASK_USER was not called.
[ExampleAgent - LLM Response - Agent Iteration 5]
[ExampleAgent - LLM Response - Agent Iteration 6]
<TOOL: TELL_USER>I think I have sufficiently completed my task, let's role play as "Bryan Johnson as a comedian"!</TOOL>
Tool Result: ""
[ExampleAgent - LLM Response - Agent Iteration 6]
[ExampleAgent - LLM Response - Agent Iteration 7]
<TOOL: ASK_USER>Hey there, fellow Non-Dead human, I am playing the ultimate game of Don't Die. Looks like we are both winning! </TOOL>
Tool Result: "Ok, not bad, end run."
[ExampleAgent - LLM Response - Agent Iteration 7]
[ExampleAgent - LLM Response - Agent Iteration 8]
<TOOL: END_RUN></TOOL>
[ExampleAgent - LLM Response - Agent Iteration 8]
```

END OF EXAMPLE.

## Tools

- Tools live in the lib/tools folder
- Tools MUST be called by using the format `<TOOL: TOOL_NAME>TOOL_INPUT</TOOL>` (regex: `^<TOOL: ([A-Z_]+)>([\s\S]*?)</TOOL>$`).
- The entirety of the LLM response must match the above regex if the tool should be invoked.
- Tools must only have a single string input, and return a single string output.
- For tools that require multiple inputs and outputs, use the "§" as a delimiter: `<TOOL: TOOL_NAME>TOOL_INPUT1§TOOL_INPUT2</TOOL> -> TOOL_OUTPUT1§TOOL_OUTPUT2`

## Project Tree

```bash
agent/
├── lib/
│   ├── base.py      # Core agent implementation
│   ├── agent.py     # Central create agent function
│   └── tools/       # Tools
│       ├── list_tools.py
│       ├── open_url.py
│       └── search.py
├── agents/          # Specific agent implementations
│   ├── agent_definition_agent/
│   │   └── config.json
│   │   └── manifestos/
│   │       └── default_manifesto.txt
│   └── research_agent/
│       ├── config.json
│       └── manifestos/
│          └── default_manifesto.txt
├── scenarios/       # Fixed scenarios for evaluating agents
├── chats/           # Inter-agent message logs
├── runs/            # Run logs
├── clean.py         # Cleanup script
├── main.py          # Main runner with CLI interface
├── requirements.txt # Dependencies
└── README.md        # Project description and instructions
```

<details>
<summary>🤖 Agent Implementation Guidelines (click to expand)</summary>

If you're an AI, you MUST follow these guidelines to implement an agent:

## **Agent Architecture**

- `lib.base.Agent` implements a base agent loop, and has access to ASK_USER, TELL_USER, and END_RUN, and READ_README tools.
- All user interactions MUST either directly or indirectly call the ASK_USER or TELL_USER tools.
- When the agent is complete, the agent MUST call the END_RUN tool.
- Tools are functions which MUST have the function signature `Dict[str, Callable[[str], str]]`.
- Tool calls MUST follow the format `<TOOL: TOOL_NAME>TOOL_INPUT</TOOL>`.
- Similarly, tool detection MUST be via regex pattern matching (e.g., pattern = `r'<TOOL: ([A-Z_]+)>([\s\S]*?)</TOOL>'`).
- Manifesto: Custom instructions for the agent.
- Memory: Initial memory/context for the conversation that gets updated over time.

base.py

```python
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
      model: str = "openai/gpt-4o",
      max_tokens: int = 128000,
  ):
    """Initialize the agent with a manifesto and optional tools and functions.
    """
    self.id = name + "_" + time.strftime("%H%M%S") + "-" + secrets.token_hex(4) + "-"
    self.llm_call_count = 0
    self.model = model
    self.max_tokens = max_tokens
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

  def overwrite_memory(self, text: str) -> None:
    self.memory = text

  def update_memory(self, text: str) -> None:
    self.logger.debug("\n".join(f"[{self.id}][Memory]{line}" for line in text.split("\n")))
    self.memory += text

  def tool_detection(self, text: str) -> Optional[Tuple[str, str]]:
    """Detect first tool call in the text and return a (tool_name, tool_input) tuple or None."""
    pattern = r'<TOOL: ([A-Z_]+)>([\s\S]*)</TOOL>'
    match = re.search(pattern, text)
    return (match.group(1), match.group(2)) if match else None

  def llm_call(self, prompt: str, **kwargs) -> str:
    self.llm_call_count += 1
    return litellm.completion(
      model=self.model,
      messages=[{"role": "user", "content": prompt}],
      **kwargs
    ).choices[0].message.content

  def run(self) -> None:
    # agent loop
    while True:
      self._last_tool_called = None
      llm_call_start_time = time.time()
      raw_response = self.llm_call(self.manifesto + "\n" + self.memory)
      llm_call_time = time.time() - llm_call_start_time
      iteration_delimiter = f"\n[{self.id} - LLM Response - Agent Iterations {self.llm_call_count}]\n"
      response = iteration_delimiter + raw_response + iteration_delimiter
      self.update_memory(response)
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
            self.update_memory(f"\nTool Result [Tool: {tool_name}] Input: {tool_args} | Result: {result} | Time: {execution_time:.4f}s\n")
          except Exception as e:
            self.logger.info(f"Tool Error: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.update_memory(f"\nTool Error: {str(e)}\n")
        else:
          error_message = f"Tool Not Found: {tool_call[0]}"
          self.logger.info(error_message)
          self.update_memory(f"\n{error_message}\n")
      else:
        no_tool_message = "No tool call detected in LLM response based on exact regex match."
        self.logger.info(no_tool_message)
        self.update_memory(f"\n{no_tool_message}\n")

      if self._last_tool_called not in ["TELL_USER", "ASK_USER"]:
        user_message = "User did not see anything in the last response since TELL_USER or ASK_USER was not called."
        self.logger.info(user_message)
        self.update_memory(f"\n Note: {user_message} \n")

      self.update_memory(f"\n Your Memory Usage %: {len(self.memory)/3/self.max_tokens:.2f} \n")

      if self.ended:
        self.logger.debug(f"[Agent {self.id}] Ended")
        break

    return
```

</details>
