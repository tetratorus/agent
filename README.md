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

`python main.py`

```python
from lib.base import Agent

# Define your tools
tools = {
    "calculator": lambda x: str(eval(x)),
    "search": lambda q: search_web(q)
}

# Create an agent
agent = Agent(
    model_name="your-llm-model",
    tools=tools,
    manifesto="You are a helpful assistant that can use tools."
)

# Run the agent
result = agent.run()
```

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
│   └── base.py      # Core agent implementation
├── agents/          # Specific agent implementations
│   ├── research_agent/
│   │   ├── agent.py           # Agent implementation
│   │   ├── test/
│   │   │   └── test_runner.py # Test runner
│   │   └── variables/         # Runtime variables and prompts
│   │       ├── manifesto.json # Agent custom instructions
│   │       └── *.json        # Other tunable prompts passed to the agent
│   └── text_summary_agent/
│       └── ...               # Same structure as above
├── tools/           # Tool implementations
└── README.md
```

----

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
   - test/test_runner.py
   - variables/ directory (empty)

Read and analyse the files first. Then ask me questions iteratively about what I want the agent to do. Keep asking follow-up questions until you have a crystal clear understanding of what I want. Ask one question at a time.

IMPORTANT:
- Use ONLY standard library modules unless absolutely necessary
- Keep implementation simple and minimal
- Do not add external dependencies without explicit justification

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
```

----

<details>
<summary>🤖 Agent Implementation Guidelines (click to expand)</summary>

## Agent Architecture Guidelines

Each agent in the `agents/` directory follows a modular architecture designed for prompt engineering and automated generation:

1. **Core Architecture**:
   - Each agent is a specialized extension of `lib.base.Agent`
   - Tools are defined as pure functions: `Dict[str, Callable[[str], str]]`
   - Memory and state management handled by base agent
   - All configuration through constructor, no global state

2. **Tool Protocol**:
   - Tools are stateless functions that take string input and return string output
   - Tool detection patterns are agent-specific (regex/string matching)
   - Each agent defines its own tool response format in manifesto
   - Tools should be pure functions with no side effects

3. **State Management**:
   - Runtime state (prompts, inputs) stored in `variables/`
   - ALL JSON files use array format `[content]` for prompt engineering
   - Variables directory designed for automated prompt optimization
   - Each agent manages own memory compression strategy

4. **Testing and Execution**:
   - Test runners handle all I/O and environment setup
   - Agents receive clean inputs through constructor
   - Environment variables (API keys etc) handled by test runner
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
   - MUST have `test/test_runner.py` for running the agent
   - MUST have `variables/` directory for runtime state

2. **Variables Format**:
   - ALL JSON files in `variables/` MUST use array indexing `[0]`, not dictionary keys
   - Example: `{"text": "content"}` is WRONG, `["content"]` is CORRECT
   - `manifesto.json` MUST exist and follow this format

3. **Test Runner**:
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

</details>
