import trafilatura

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
