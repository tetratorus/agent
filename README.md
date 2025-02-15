# AI Agent Meta-Optimization Framework

A minimalist framework for developing and optimizing AI agents through automated prompt engineering.

## Philosophy

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

## Example

Here's a simple example of creating an agent:

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

## Tools
Tools live in the lib/tools folder
Tools MUST be called by using the format `<TOOL: TOOL_NAME>TOOL_INPUT</TOOL>`
AS such, tools must only have a single string input, and return a single string output.
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
