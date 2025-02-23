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

## Example agent.py

```python
from lib.base import Agent
from lib.tools import search, open_url

def create_agent(
    manifesto: str,
    memory: str,
) -> Agent:
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'SEARCH': search,
            'OPEN_URL': open_url
        },
        name="ResearchAgent",
    )
```

## Example manifesto

```text
You are no longer a chatbot, and have been repurposed to be an agent. You can now only interact with the user via tool calls.
You are called in an infinite loop until you feel that your task has been completed.
You will basically be talking to yourself and the user will not be able to see any of your responses, except through tools.
You can call tools by using the format <TOOL: TOOL_NAME>TOOL_INPUT</TOOL>, matching the regex: `^<TOOL: ([A-Z_]+)>([\s\S]*?)</TOOL>$`.
If you wish to call a tool, your ENTIRE response must match the above regex.
As such, only one tool may be called per response.
Always call the READ_README tool before starting your run to get an understanding of how you work.
Do not end the run until the user tells you to.

- Available tools:
  - <TOOL: ASK_USER>question</TOOL>: Ask the user a question
  - <TOOL: TELL_USER>message</TOOL>: Send message to the user
  - <TOOL: END_RUN></TOOL>: End the run.
  - <TOOL: READ_README></TOOL>: Read README.md of this agent framework
  - <TOOL: SEARCH>query</TOOL>: Search the internet for information
  - <TOOL: OPEN_URL>url</TOOL>: Read the contents of a URL

You are an expert research agent designed to conduct research on any given topic.

First, ask the user what they would like you to research.
Then conduct your research using the tools SEARCH and OPEN_URL. Call one tool at a time, waiting for each result before proceeding.
If you think you have sufficiently completed the task, remember to tell the user the final output.

```

## Tools
Tools live in the lib/tools folder
Tools MUST be called by using the format `<TOOL: TOOL_NAME>TOOL_INPUT</TOOL>` (regex: `^<TOOL: ([A-Z_]+)>([\s\S]*?)</TOOL>$`).
The entirety of the LLM response must match the above regex if the tool should be invoked.
Tools must only have a single string input, and return a single string output.
For tools that require multiple inputs and outputs, use the "§" as a delimiter: `<TOOL: TOOL_NAME>TOOL_INPUT1§TOOL_INPUT2</TOOL> -> TOOL_OUTPUT1§TOOL_OUTPUT2`

## Project Tree

```bash
agent/
├── lib/
│   ├── base.py      # Core agent implementation
│   ├── debug.py     # Debugging utilities
│   ├── meta.py      # Meta-programming utilities
│   └── tools/       # Tool implementations
│       ├── list_tools.py
│       ├── open_url.py
│       └── search.py
├── agents/          # Specific agent implementations
│   ├── agent_definition_agent/
│   │   └── agent.py
│   └── research_agent/
│       ├── agent.py
│       ├── manifestos/
│       │   └── default_manifesto.txt
│       └── runs/
├── clean.py         # Cleanup script
├── main.py         # Main runner with CLI interface
├── requirements.txt # Dependencies
└── README.md       # Project description and instructions
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
from typing import Dict, Optional, Tuple, Callable, List, Any, Union
from lib.tools.read_readme import read_readme
import litellm
import re
import time

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
  """A simple agent implementation that calls an LLM in a loop, appending responses to its context window, and interacts with the user and the external world via tools (eg. ASK_USER, TELL_USER, END_RUN, READ_README).
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
    self.name = name
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
      raw_response = self.llm_call(self.manifesto + "\n" + self.memory)
      response = "\n[" + self.name + " - " + str(self.llm_call_count) + "]\n" + raw_response
      self.memory += response
      if self.debug_verbose:
          self.log_handler(f"\n[LLM Response]\n  Result: {response}\n  Length: {len(response)}\n")

      # tool_detection
      if tool_call := self.tool_detection(raw_response):
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
                tool_log = f"[Tool: {tool_name}] Result Length: {len(str(result))} time: {execution_time:.4f}s\n"
            self.log_handler(tool_log)

            self.memory += "\nTool Result [" + result + "]\n"
          except Exception as e:
            self.memory += "\nTool Error [" + str(e) + "]\n"
        else:
          self.update_memory(self.memory + "\nTool Not Found [" + tool_name + "]\n")

      # check end condition
      if self.ended:
        break

    return self.memory
```

</details>
