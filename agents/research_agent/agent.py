import os
from typing import Dict, Optional, Callable, Tuple
import re
import trafilatura

from serpapi import GoogleSearch
from lib.base import Agent

class ResearchAgent(Agent):
    """An agent specialized for conducting web research using SerpAPI.

    This agent receives a research topic and uses SerpAPI to search for information on the topic.
    It continues to format and synthesize the information it has gathered until it has satisfied the research topic.

    Args:
        manifesto: Custom instructions for the agent.
        memory: Initial memory/context for the conversation
    """

    def __init__(self,
                 manifesto: str,
                 memory: str = ""):

        # check if all required parameters are provided

        if manifesto is None:
            raise ValueError("Manifesto must be provided")

        model_name = "openai/gpt-4o"

        self.serpapi_key = os.environ.get("SERPAPI_API_KEY")
        if not self.serpapi_key:
            raise ValueError("SerpAPI key must be provided either through serpapi_key parameter or SERPAPI_API_KEY environment variable")

        # Create tools dictionary with proper typing
        tools: Dict[str, Callable[[str], str]] = {
            'SEARCH': lambda q: self._search(q),
            'OPEN_URL': lambda o: self._open_url(o)
        }

        # Initialize base agent with search tool
        super().__init__(
            model_name=model_name,
            tools=tools,
            tool_detection=self._detect_tool,
            manifesto=manifesto,
            memory=memory
        )

    def _get_research_topic(self) -> str:
        """Get the research topic from memory."""
        # Extract research topic from memory if present
        if hasattr(self, '_research_topic'):
            return self._research_topic

        # Ask user for research topic
        topic = self.ask_user("What would you like me to research?")
        self._research_topic = topic
        return topic

    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect if there is a tool call in the text and return the tool name and input."""
        pattern = r'<TOOL: ([A-Z_]+)>(.*?)</TOOL>'
        match = re.search(pattern, text)
        if match:
            tool_name = match.group(1)
            tool_input = match.group(2)
            return tool_name, tool_input
        else:
            return None, None

    def _open_url(self, url: str) -> str:
        """Open a URL and return its content as clean text using trafilatura."""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded is None:
                return f"Error: Could not download content from URL: {url}"

            text = trafilatura.extract(downloaded)
            if text is None:
                return f"Error: Could not extract text content from URL: {url}"

            return text
        except Exception as e:
            return f"Error opening URL: {str(e)}"

    def _search(self, query: str) -> str:
        """Execute a Google search using SerpAPI."""
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 5  # Limit to top 5 results
            })
            results = search.get_dict()

            # Format organic search results
            if "organic_results" not in results:
                return "No results found."

            formatted_results = []
            for result in results["organic_results"][:5]:
                title = result.get("title", "No title")
                link = result.get("link", "No link")
                snippet = result.get("snippet", "No description")
                formatted_results.append(f"Title: {title}\nURL: {link}\nDescription: {snippet}\n")

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Search error: {str(e)}"
