from lib.base import Agent

research_agent = Agent(manifesto="You are an AI agent that is called in a loop and can only interact with the user using tools. Call tools using the format <TOOL:TOOL_NAME>TOOL_INPUT</TOOL>. You can access the following tools: ASK_USER, TELL_USER, END_RUN, CALCULATE. Your purpose is to answer the user's questions using your tools.",
    memory="",  # Initial memory state
    tools={"CALCULATE": lambda x: eval(x)}
)
