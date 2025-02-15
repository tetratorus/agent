from serpapi import GoogleSearch
import os

def search(input_str: str) -> str:
    """Execute a Google search using SerpAPI.

    Args:
        input_str: String in format 'query§max_results'. max_results is optional, defaults to all results.

    Returns:
        Formatted string containing search results with title, URL, and description
        Each result is separated by newlines

    Raises:
        No exceptions are raised, errors are returned as strings
    """
    try:
        parts = input_str.split('§')
        query = parts[0]
        max_results = int(parts[1]) if len(parts) > 1 else None

        serpapi_key = os.environ.get("SERPAPI_API_KEY")
        if not serpapi_key:
            return "Error: SerpAPI key not found in environment variables"

        params = {
            "q": query,
            "api_key": serpapi_key
        }
        if max_results is not None:
            params["num"] = max_results

        search = GoogleSearch(params)
        results = search.get_dict()

        # Format organic search results
        if "organic_results" not in results:
            return "No results found."

        formatted_results = []
        for result in results["organic_results"]:
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            snippet = result.get("snippet", "No description")
            formatted_results.append(f"Title: {title}\nURL: {link}\nDescription: {snippet}\n")

        return "\n".join(formatted_results)

    except Exception as e:
        return f"Search error: {str(e)}"
