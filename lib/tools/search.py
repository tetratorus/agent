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
