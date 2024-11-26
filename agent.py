import llms

class SimpleAgent:
    def __init__(self, model_name, tools):
        self.llm = llms.init(model_name)
        self.tools = tools
        self.memory = []

    async def run(self, user_input):
        self.memory.append(f"User: {user_input}")

        while True:
            # Get AI response
            response = await self.llm.acomplete("\n".join(self.memory))
            self.memory.append(f"Assistant: {response.text}")

            # Check for tool calls (super simple parsing)
            if "<<TOOL:" in response.text:
                tool_name = response.text.split("<<TOOL:")[1].split(">>")[0]
                tool_input = response.text.split(">>")[1].split("<<END>>")[0]

                if tool := self.tools.get(tool_name):
                    result = tool(tool_input)
                    self.memory.append(f"Tool Result: {result}")
                    continue

            return response.text
