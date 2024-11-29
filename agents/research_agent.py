import os
from serpapi import GoogleSearch
import asyncio
from agents import Agent

def search_google(query):
    """Simple Google search using SerpAPI"""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("SERPAPI_KEY environment variable not set")

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": 5  # Limit to top 5 results
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    formatted_results = []
    if "organic_results" in results:
        for result in results["organic_results"]:
            formatted_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })

    return formatted_results

# Tool definitions
tools = {
    "search": search_google
}

AGENT_INSTRUCTIONS = """You are a helpful AI assistant with access to search capabilities. Help users find and process information effectively.

Available tool:
- search: Searches the internet for current information

When you need to search, format your response like this:
<<TOOL:search>>your search query<<END>>

Guidelines:
1. Search when you need current or factual information
2. After searching, summarize the relevant information for the user
3. Use multiple searches if needed to verify information
4. When done, end your response with <<TASK_COMPLETE>>

Example:
User: What's the latest news about SpaceX?
Assistant: Let me check the recent news.
<<TOOL:search>>latest SpaceX news<<END>>
[Summary of search results...]
<<TASK_COMPLETE>>
"""

async def main():
    # Initialize the agent
    agent = Agent(
        model_name="claude-3-5-sonnet-20241022",
        tools=tools,
        agent_instructions=AGENT_INSTRUCTIONS
    )

    while True:
        try:
            user_input = input("\nEnter your question (or 'quit' to exit): ")
            if user_input.lower() == 'quit':
                break

            response = await agent.run(user_input)
            print("\nAssistant:", response.replace("<<TASK_COMPLETE>>", "").strip())

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if not os.getenv("SERPAPI_KEY"):
        print("Please set your SERPAPI_KEY environment variable")
        exit(1)

    asyncio.run(main())
