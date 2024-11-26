import llms
import asyncio
from agent import SimpleAgent

def ask_human_question(question):
    print("\nTool asking:", question)
    return input("Your answer: ")

async def main():
    agent = SimpleAgent(
        model_name="claude-3-5-sonnet-20240620",
        tools={"ask_user_question": ask_human_question}  # More descriptive name
    )

    # Add initial prompt to explain the tool
    initial_prompt = """You have access to one tool:
ask_user_question: Use this to ask the human user a question and get their response. Format: <<TOOL:ask_user_question>>your question here<<END>>

Let me show you the entire conversation history so you can see what's happening:
"""
    response = await agent.run(initial_prompt)
    print("\nAssistant:", response)

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "quit":
            break

        print("\n[DEBUG] Sending to AI:", "\n".join(agent.memory))  # Show what AI sees
        response = await agent.run(user_input)
        print("\nAssistant:", response)

if __name__ == "__main__":
    asyncio.run(main())
