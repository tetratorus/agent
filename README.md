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


## Basic Usage

The simplest way to run an agent is through the CLI:
```bash
python main.py
```

## Project Tree

```bash
agent/
├── lib/
│   ├── base.py      # Core agent implementation
│   └── meta.py      # Debug log wrapper
├── agents/          # Specific agent implementations
│   ├── xxx_agent/
│   │   ├── agent.py                # Agent implementation
│   │   ├── manifestos/             # Generated manifestos
│   │   │   ├── default_manifesto   # Default manifesto
│   │   │   ├── manifesto_xxx       # Variation of manifesto
│   │   │   └── manifesto_yyy
│   │   ├── scenarios/              # Generated scenarios
│   │   │   ├── scenario_aaa        # Scenario to simulatefor xxx_agent
│   │   │   └── scenario_bbb
│   │   ├── simulations/                     # Scenario simulation outputs
│   │   │   ├── simulation_scenario_aaa/     # Scenario_aaa simulation logs
│   │   │   │   ├── simulation_log_1         # Simulation log
│   │   │   │   └── simulation_log_2
│   │   │   └── simulation_scenario_bbb/
│   ├── yyy_agent/
│   │   ├── agent.py
│   │   ├── manifestos/
│   │   ├── scenarios/
│   │   └── simulations/
├── main.py             # Main runner with CLI interface
├── requirements.txt    # Dependencies
└── README.md           # Project description and instructions
```

<details>
<summary>🤖 Agent Implementation Guidelines (click to expand)</summary>

If you're an AI, you **must** follow these guidelines to implement an agent:

## **Agent Architecture**

- Agents extend `lib.base.Agent`.
  - `lib.base.Agent` implements a base agent loop, and has access to ASK_USER and TELL_USER tools.
  - All user interactions must either directly or indirectly call the ASK_USER or TELL_USER toos.
- Tools: Pure, stateless functions defined as `Dict[str, Callable[[str], str]]`.
  - Tool calls should follow the format `<TOOL: TOOL_NAME>TOOL_INPUT</TOOL>`.
  - Similarly, tool detection should be via regex pattern matching (e.g., `r'<TOOL: ([A-Z_]+)>(.*?)</TOOL>'`).
- Manifesto: Custom instructions for the agent.
- Memory: Initial memory/context for the conversation.

</details>
