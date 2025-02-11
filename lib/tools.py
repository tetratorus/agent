
import trafilatura
from serpapi import GoogleSearch
import os

def search(query: str) -> str:
    """Execute a Google search using SerpAPI."""
    try:
        serpapi_key = os.environ.get("SERPAPI_API_KEY")
        if not serpapi_key:
            return "Error: SerpAPI key not found in environment variables"

        search = GoogleSearch({
            "q": query,
            "api_key": serpapi_key,
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

def open_url(url: str) -> str:
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
