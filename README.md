# AI Agent Meta-Optimization Framework

A minimalist framework for developing and optimizing AI agents through automated prompt engineering. The core thesis is that manually coding complex agent behaviors and hand-tuning prompts doesn't scale - instead, we should create minimal, flexible frameworks that let AI optimize itself.

## Philosophy

Most AI agent development time is spent on:

1. Debugging complex agent execution steps
2. Manual prompt engineering and tuning
3. Writing intricate code to handle edge cases

This framework takes a different approach:

1. Implement the simplest possible agent loop
2. Make every decision point prompt-driven and tunable
3. Let AI optimize the prompts

## Basic Usage

The simplest way to run an agent is through the CLI:
```bash
python main.py
```

To implement your own agent:

```python
from typing import Optional, Tuple
import re
from lib.base import Agent
from lib.debug import debug

class MyAgent(Agent):
    """A custom agent that does X.

    Args:
        manifesto: Custom instructions for the agent
        memory: Initial memory/context for the conversation
    """

    @debug()
    def __init__(self, manifesto: str, memory: str = ""):
        if manifesto is None:
            raise ValueError("Manifesto must be provided")

        super().__init__(
            model_name="gpt-4o",
            manifesto=manifesto,
            memory=memory,
            tools={
                "search": self._search,
                "process": self._process
                # ask_user tool is built-in and available automatically
            },
            tool_detection=self._detect_tool
        )

    @debug()
    def _search(self, query: str) -> str:
        """Search for information."""
        try:
            # Implement search logic
            return f"Results for: {query}"
        except Exception as e:
            return f"Error searching: {e}"

    @debug()
    def _process(self, data: str) -> str:
        """Process the data."""
        try:
            # Implement processing logic
            return f"Processed: {data}"
        except Exception as e:
            return f"Error processing: {e}"

    @debug()
    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect tool calls in the agent's response."""
        pattern = r'<TOOL: ([A-Z_]+)>(.*?)</TOOL>'
        match = re.search(pattern, text)
        if match:
            tool_name = match.group(1).lower()
            tool_input = match.group(2)
            return tool_name, tool_input
        return None, None
```

Then create your agent's variables in `variables/manifesto.json`:
```json
[
  "You are an agent that does X. When you need information:\n- Use <TOOL: SEARCH>query</TOOL> to search\n- Use <TOOL: PROCESS>data</TOOL> to process\n- Use <TOOL: ASK_USER>question</TOOL> to ask the user questions\n\nFormat your responses clearly and end when done."
]
```

## Built-in Tools

The base Agent provides some built-in tools that all agents can use:

1. **ask_user**: Ask the user a question and get their response
   - Usage: `<TOOL: ASK_USER>What is your preference?</TOOL>`
   - Can be overridden for testing: `agent.override_ask_user(lambda q: "test response")`

## Architecture

The agent operates in a minimal, prompt-driven loop:

1. **Compose Request**:
   - The manifesto (constant instructions) is combined with current memory
   - The manifesto defines the agent's personality and capabilities
   - Memory contains the conversation history and tool results

2. **LLM Call**:
   - Send composed request to LLM
   - Response is appended to memory with "Assistant: " prefix

3. **Tool Detection**:
   - Check if LLM response contains tool calls
   - Tool detection is customizable per agent (e.g. regex patterns)
   - If tool is found and exists, execute it
   - Tool result is appended to memory with "Tool Result: " prefix

4. **End Detection**:
   - Check if agent should stop (customizable per agent)
   - Default behavior: end if no tool was called
   - Agents can define custom end conditions (e.g. "<TASK_COMPLETED>")

This minimal loop is completely prompt-driven - the manifesto and memory are the only state, and all decision points (tool detection, end conditions) can be tuned through prompts rather than code.

## Installation

```bash
# Dependencies will be listed here
pip install -r requirements.txt
```

## Project Structure

```bash
agent/
├── lib/
│   ├── base.py      # Core agent implementation
│   └── debug.py     # Debug decorator and logging
├── agents/          # Specific agent implementations
│   ├── research_agent/
│   │   ├── agent.py           # Agent implementation
│   │   └── variables/         # Runtime variables and prompts
│   ├── text_summary_agent/
│   │   ├── agent.py
│   │   └── variables/
│   ├── logging_summary_agent/
│   │   ├── agent.py
│   │   └── variables/
│   └── variable_generation_agent/
│       ├── agent.py
│       └── variables/
├── main.py         # Main runner with CLI interface
└── requirements.txt
```

Each agent follows a simple structure:
- `agent.py`: Main implementation extending `lib.base.Agent`
- `variables/`: Directory containing JSON files for runtime variables
  - `manifesto.json`: Agent's core instructions
  - Other JSON files specific to the agent

All agents use the same standardized XML format for tool calls:
```
<TOOL: TOOL_NAME>arguments</TOOL>
```

## Quick Agent Generation

If you're using an AI-powered editor, use this prompt to generate your agent's code structure:

```
You will help to generate a new agent implementation by:
1. Reading and analyzing:
   - README
   - lib/base.py to understand the core Agent class
   - Existing agents in agents/ directory for implementation patterns

2. Creating the following structure:
   - agent.py (extending lib.base.Agent with required methods)
   - variables/ directory (empty)

Read and analyse the files first. Then ask me questions iteratively about what I want the agent to do. Keep asking follow-up questions until you have a crystal clear understanding of what I want. Ask one question at a time.

IMPORTANT:
- Use ONLY standard library modules unless absolutely necessary
- Keep implementation simple and minimal
- Do not add external dependencies without explicit justification
- For tool detection prefer to use XML-like tags

```

## Setting Up Runtime Variables

The `variables/` folders are intentionally ignored by code editors due to their size and runtime-specific nature. You'll need to set these up manually after generating your agent's code.

All variable files in the `variables/` directory must be JSON files with a specific format:
- Content must be a JSON array containing a single string
- The string contains the entire content/instructions/prompt
- No additional fields or nested objects are allowed

Example format:
```json
[
  "You are an agent that does X. Your instructions are:\n1. Do this\n2. Then do that\n\nWhen responding:\n- Format like this\n- Include these details"
]
```

To set up your agent's variables:

1. Create a `variables/` directory in your agent's folder
2. Create your JSON files (e.g. `manifesto.json`) following the format above
3. Use this prompt to generate the content for your files:
```
Read the README.

Analyze the newly generated agent.py to understand:
- What tools the agent uses
- What runtime variables it references
- Its core behavior and requirements

Then generate copyable JSON content for manifesto.json:
- Use EXACT format: ["content"]
- All newlines as \\n
- All quotes as \\\"
- Output as a single line with NO formatting
- NO explanations or markdown - just the raw JSON array
- Content must define:
  * Agent personality and behavior
  * EXACT tool call formats with proper escaping
  * Response format requirements
  * Any other runtime requirements
Note: if there is no end_detection defined, the agent will end if no tool is called! So keep that in mind when generating the manifesto.

After that, generate copyable JSON content for other variables, following the same format.
```

----

<details>
<summary>🤖 Agent Implementation Guidelines (click to expand)</summary>

If you're an AI you MUST follow these guidelines below to implement an agent:

## Agent Architecture Guidelines

Each agent in the `agents/` directory follows a modular architecture designed for prompt engineering and automated generation:

1. **Core Architecture**:
   - Each agent is a specialized extension of `lib.base.Agent`
   - Tools are defined as pure functions: `Dict[str, Callable[[str], str]]`
   - Memory and state management handled by base agent
   - All configuration through constructor, no global state

2. **Tool Protocol**:
   - Tools are stateless functions that take string input and return string output
   - Tool calls must use XML format: `<TOOL: TOOL_NAME>arguments</TOOL>`
   - Multi-line arguments are supported through the XML format
   - Tools should be pure functions with no side effects

3. **State Management**:
   - Runtime state (prompts, inputs) stored in `variables/`
   - ALL JSON files use array format `[content]` for prompt engineering
   - Variables directory designed for automated prompt optimization
   - Each agent manages own memory compression strategy

4. **Execution**:
   - Runners handle all I/O and environment setup
   - Agents receive clean inputs through constructor
   - Environment variables (API keys etc) handled by runner
   - All methods decorated with `@debug()` for monitoring

5. **Prompt Engineering**:
   - Manifesto defines agent personality and tool protocols
   - JSON array format enables automated prompt optimization
   - Each agent can define custom end conditions
   - Tool formats defined in manifesto, not hardcoded

6. **Error Handling**:
   - Required parameters validated in constructor
   - Environment variables checked before agent creation
   - Tools must handle their own errors gracefully
   - Memory compression handled by base agent

7. **Extensibility**:
   - New agents inherit core functionality from base
   - Tool sets can be mixed: external APIs and internal functions
   - Custom tool detection patterns per agent
   - Memory management customizable per agent

## Development Guidelines

### Code Style

- No default/hardcoded values for required parameters in variables folder
- All variables defined in variables folder must be explicitly passed
- No default/hardcoded values for required parameters in agent constructor
- Clear documentation of all required parameters

## Agent Implementation Guidelines

Each agent in the `agents/` directory MUST follow these conventions:

1. **Directory Structure**:
   - Agent directory name should be descriptive (e.g., `research_agent`, `text_summary_agent`)
   - Main implementation MUST be in `agent.py` (not named after the agent)
   - MUST have `run/runner.py` for running the agent
   - MUST have `variables/` directory for runtime state

2. **Variables Format**:
   - ALL JSON files in `variables/` MUST use array indexing `[0]`, not dictionary keys
   - Example: `{"text": "content"}` is WRONG, `["content"]` is CORRECT
   - `manifesto.json` MUST exist and follow this format

3. **Runner**:
   - MUST read all variables using array index `[0]`
   - Example: `json.load(f)[0]` not `json.load(f)["key"]`
   - MUST handle all file I/O, agent implementation should only take clean inputs

4. **Agent Implementation**:
   - CRITICAL: Before implementing any agent methods:
     1. Read and understand the base Agent class in `lib/base.py` first
     2. Match ALL method signatures EXACTLY as defined in base Agent class
     3. Pay special attention to tool detection and end detection interfaces
   - MUST inherit from `lib.base.Agent`
   - MUST NOT read files directly, all inputs through constructor
   - MUST use `@debug()` decorator on all methods
   - MUST implement `_detect_tool` and `_end_detection`
   - MUST follow naming convention: directory `xxx_agent` (e.g. `research_agent`) and class `XxxAgent` (e.g. `ResearchAgent`)

</details>
