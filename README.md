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

- Available tools:
  - <TOOL: ASK_USER>question</TOOL>: Ask the user a question
  - <TOOL: TELL_USER>message</TOOL>: Send message to the user
  - <TOOL: END_RUN></TOOL>: End the run.
  - <TOOL: SEARCH>query</TOOL>: Search the internet for information
  - <TOOL: OPEN_URL>url</TOOL>: Read the contents of a URL

You are an expert research agent designed to conduct research on any given topic.

First, ask the user what they would like you to research.
Then conduct your research using the tools SEARCH and OPEN_URL. Call one tool at a time, waiting for each result before proceeding.
If you think you have sufficiently completed the task, remember to tell the user the final output.
Do not end the run until the user tells you to.


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
│       │   └── default_manifesto
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

- `lib.base.Agent` implements a base agent loop, and has access to ASK_USER, TELL_USER, and END_RUN tools.
- All user interactions MUST either directly or indirectly call the ASK_USER or TELL_USER tools.
- When the agent is complete, the agent MUST call the END_RUN tool.
- Tools are functions which MUST have the function signature `Dict[str, Callable[[str], str]]`.
- Tool calls MUST follow the format `<TOOL: TOOL_NAME>TOOL_INPUT</TOOL>`.
- Similarly, tool detection MUST be via regex pattern matching (e.g., pattern = `r'<TOOL: ([A-Z_]+)>([\s\S]*?)</TOOL>'`).
- Manifesto: Custom instructions for the agent.
- Memory: Initial memory/context for the conversation that gets updated over time.

</details>
