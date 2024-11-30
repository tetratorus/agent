# Autonomous Agent Framework

A lightweight and flexible framework for building autonomous agents powered by Large Language Models (LLMs). This framework enables agents to engage in conversations, execute tools, and maintain context memory efficiently.

## Key Features

- **Flexible Tool Integration**: Easily integrate custom tools that agents can use during execution
- **Memory Management**: Built-in memory compression for efficient storage of conversation history
- **Configurable Behavior**: Customize tool detection, end conditions, and memory management
- **LLM Agnostic**: Works with any LLM that implements the basic completion interface

## Basic Usage

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
result = await agent.run()
```

## Architecture

The agent operates in a simple loop:

1. Generate response using LLM
2. Store response in memory
3. Check for tool calls
4. Execute tools if detected
5. Check end conditions
6. Repeat until end conditions are met

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
├── tools/           # Tool implementations
└── README.md
```
