"""
Web Access Tool for EchoKernel

This module provides a safe web content retrieval tool that can be used by AI models
to access web pages and extract content. The tool includes safety measures, rate limiting,
and proper error handling to prevent abuse while allowing legitimate web access.

The web access tool:
- Retrieves web page content with proper headers
- Implements rate limiting to be respectful to servers
- Validates and sanitizes URLs for safety
- Extracts text content from HTML pages
- Handles various HTTP status codes gracefully
- Returns structured data including title, text, and metadata
- Uses search providers for web search functionality

Example:
    ```python
    from tools.WebAccessTool import get_web_content, search_web
    from echo_kernel.providers.DuckDuckGoSearchProvider import DuckDuckGoSearchProvider
    
    # Register with kernel
    kernel.register_tool(get_web_content)
    kernel.register_tool(search_web)
    
    # AI can now use the tool to access web content and search
    result = await kernel.generate_text(
        "Get the latest news from a specific website"
    )
    ```
"""

import asyncio
from typing import Any, Dict, List

from echo_kernel.EchoTool import EchoTool

from .web_access import WebAccess

web_access = WebAccess()

async def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Asynchronously searches the web for the given query.
    :param query: The query to search for.
    :param max_results: The maximum number of results to return.
    :return: A dictionary containing the search results.
    """
    if max_results is None:
        max_results = 5
    return await web_access.search_web(query, max_results=max_results)

async def get_web_content(url: str) -> Dict[str, Any]:
    """
    Asynchronously gets the content of a web page.
    :param url: The URL of the web page.
    :return: A dictionary containing the content of the web page.
    """
    return await web_access.get_page_content(url)

def web_access_tools() -> List[EchoTool]:
    """
    Returns a list of web access tools.
    :return: A list of web access tools.
    """
    return [
        EchoTool(
            name="search_web",
            description="Searches the web for the given query.",
            func=search_web,
        ),
        EchoTool(
            name="get_web_content",
            description="Gets the content of a web page.",
            func=get_web_content,
        ),
    ] 