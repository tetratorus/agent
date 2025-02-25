import trafilatura

def open_url(caller_id: str, url: str) -> str:
    """Open a URL and return its content as clean text using trafilatura.

    Args:
        url: The URL to fetch and extract content from

    Returns:
        Clean text content from the URL, or error message if extraction fails

    Raises:
        No exceptions are raised, errors are returned as strings
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return f"Error: Could not download content from URL: {url}"

        text = trafilatura.extract(downloaded)
        if text is None:
            return f"Error: Could not extract text content from URL: {url}"

        return text
    except trafilatura.exceptions.FetchError:
        return f"Error: Could not fetch URL: {url}"
    except trafilatura.exceptions.ProcessingError:
        return f"Error: Could not process content from URL: {url}"
    except Exception as e:
        return f"Unexpected error opening URL: {str(e)}"
