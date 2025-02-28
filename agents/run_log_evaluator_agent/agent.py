from lib.tools.read_agent_run_log import read_agent_run_log
from lib.tools.list_agent_run_logs import list_agent_run_logs
from lib.tools.list_agents import list_agents
from lib.base import Agent

def create_agent(manifesto: str, memory: str) -> Agent:
    """Creates a Run Log Evaluator Agent
    This agent analyzes run logs to identify any major logical flaws or oversights.
    """
    return Agent(
        manifesto=manifesto,
        memory=memory,
        tools={
            'READ_AGENT_RUN_LOG': read_agent_run_log,
            'LIST_AGENT_RUN_LOGS': list_agent_run_logs,
            'LIST_AGENTS': list_agents,
        },
        name="RunLogEvaluatorAgent",
    )
