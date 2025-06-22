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

from typing import Optional
from tools.web_access import WebAccess
from echo_kernel.Tool import EchoTool
import json
import asyncio

@EchoTool(description="Retrieve web page content and extract text, title, and metadata")
def get_web_content(url: str, timeout: Optional[int] = 30) -> str:
    """
    Retrieve and parse web page content from a given URL.
    
    This tool allows AI models to safely access web content. The tool implements
    rate limiting, URL validation, and content extraction to provide structured
    data from web pages.
    
    Args:
        url: The URL of the web page to retrieve (must be HTTP or HTTPS)
        timeout: Request timeout in seconds (default: 30, max: 60)
    
    Returns:
        JSON string containing web page content with the following structure:
        {
            "success": bool,
            "url": str,
            "status_code": int,
            "title": str,
            "description": str,
            "text": str,
            "headings": list,
            "word_count": int,
            "error": str (if request failed)
        }
    
    Safety Features:
        - URL validation and sanitization (only HTTP/HTTPS allowed)
        - Rate limiting (1 request per second)
        - Request timeout limits (30 seconds default)
        - Content size limits (10MB maximum)
        - User-Agent identification
        - Comprehensive error handling
    
    Example:
        ```python
        result = get_web_content("https://example.com")
        # Returns: {
        #   "success": true,
        #   "url": "https://example.com",
        #   "status_code": 200,
        #   "title": "Example Domain",
        #   "description": "This domain is for use in illustrative examples...",
        #   "text": "Example Domain This domain is for use in illustrative examples...",
        #   "headings": ["Example Domain"],
        #   "word_count": 15
        # }
        ```
    
    Note:
        This tool is designed for educational and development purposes.
        It implements rate limiting to be respectful to web servers.
        Do not use it for aggressive web scraping or in production environments
        without proper consideration of server policies.
    """
    # Validate timeout parameter
    if timeout is None:
        timeout = 30
    elif timeout > 60:
        timeout = 60  # Cap at 60 seconds for safety
    
    try:
        # Create web access instance
        web_access = WebAccess()
        
        # Retrieve page content
        result = web_access.get_page_content(url, timeout=timeout)
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        # Handle any errors in the execution process
        error_result = {
            "success": False,
            "url": url,
            "error": f"Tool execution error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)

@EchoTool(description="Search the web for information using configured search providers")
async def search_web(query: str, max_results: Optional[int] = 5, provider_type: Optional[str] = "duckduckgo") -> str:
    """
    Search the web for information using configured search providers.
    
    This tool uses search providers to perform web searches. By default, it uses
    DuckDuckGo which doesn't require an API key. You can also configure Google
    or Bing search providers for more comprehensive results.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5, max: 10)
        provider_type: Type of search provider to use ("duckduckgo", "google", "bing")
    
    Returns:
        JSON string containing search results:
        {
            "success": bool,
            "query": str,
            "results": List[Dict] (if successful),
            "error": str (if failed),
            "provider": str
        }
    
    Example:
        ```python
        result = await search_web("Python programming tutorials")
        # Returns search results from the configured provider
        ```
    
    Note:
        - DuckDuckGo: Free, no API key required (default)
        - Google: Requires Google API key and Custom Search Engine ID
        - Bing: Requires Bing Search API key
    """
    # Validate max_results parameter
    if max_results is None:
        max_results = 5
    elif max_results > 10:
        max_results = 10  # Cap at 10 results for safety
    
    try:
        # Create web access instance with appropriate search provider
        if provider_type.lower() == "google":
            # For Google, you would need to configure API key and search engine ID
            # This is a placeholder - in practice, you'd pass these as parameters
            return json.dumps({
                "success": False,
                "query": query,
                "error": "Google search provider requires API key and search engine ID configuration",
                "suggestion": "Use DuckDuckGo provider or configure Google API credentials"
            }, indent=2)
        elif provider_type.lower() == "bing":
            # For Bing, you would need to configure API key
            # This is a placeholder - in practice, you'd pass this as a parameter
            return json.dumps({
                "success": False,
                "query": query,
                "error": "Bing search provider requires API key configuration",
                "suggestion": "Use DuckDuckGo provider or configure Bing API credentials"
            }, indent=2)
        else:
            # Default to DuckDuckGo
            try:
                from echo_kernel.providers.DuckDuckGoSearchProvider import DuckDuckGoSearchProvider
                web_access = WebAccess(search_provider=DuckDuckGoSearchProvider())
            except ImportError:
                return json.dumps({
                    "success": False,
                    "query": query,
                    "error": "DuckDuckGo provider not available - aiohttp may not be installed",
                    "suggestion": "Install aiohttp: pip install aiohttp"
                }, indent=2)
        
        # Perform search
        result = await web_access.search_web(query, max_results=max_results)
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        # Handle any errors in the execution process
        error_result = {
            "success": False,
            "query": query,
            "error": f"Tool execution error: {str(e)}"
        }
        return json.dumps(error_result, indent=2) 