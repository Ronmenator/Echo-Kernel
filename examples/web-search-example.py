"""
Web Search Example - Using Search Providers

This example demonstrates how to use the web search functionality with
different search providers in Echo-Py. It shows how to:

1. Use DuckDuckGo search provider (free, no API key required)
2. Configure Google search provider (requires API key and search engine ID)
3. Configure Bing search provider (requires API key)
4. Use the WebAccess class with different providers
5. Use the search_web tool with different providers

Example:
    ```bash
    python examples/web-search-example.py
    ```
"""

import asyncio
import json
from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.providers.OpenAITextProvider import OpenAITextProvider
from echo_kernel.providers.DuckDuckGoSearchProvider import DuckDuckGoSearchProvider
from echo_kernel.providers.GoogleSearchProvider import GoogleSearchProvider
from echo_kernel.providers.BingSearchProvider import BingSearchProvider
from tools.WebAccessTool import get_web_content, search_web
from tools.web_access import WebAccess

async def demonstrate_duckduckgo_search():
    """Demonstrate DuckDuckGo search provider usage."""
    print("=== DuckDuckGo Search Provider Demo ===")
    
    # Create DuckDuckGo search provider
    duckduckgo_provider = DuckDuckGoSearchProvider()
    
    # Create WebAccess with DuckDuckGo provider
    web_access = WebAccess(search_provider=duckduckgo_provider)
    
    # Perform a search
    query = "Python programming tutorials"
    print(f"Searching for: {query}")
    
    results = await web_access.search_web(query, max_results=3)
    
    if results['success']:
        print(f"Found {len(results['results'])} results:")
        for i, result in enumerate(results['results'], 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Snippet: {result['snippet'][:100]}...")
            print()
    else:
        print(f"Search failed: {results['error']}")
    
    print()

async def demonstrate_web_access_with_providers():
    """Demonstrate WebAccess class with different providers."""
    print("=== WebAccess with Different Providers Demo ===")
    
    # Example 1: DuckDuckGo (free, no API key needed)
    print("1. Using DuckDuckGo provider:")
    try:
        duckduckgo_provider = DuckDuckGoSearchProvider()
        web_access = WebAccess(search_provider=duckduckgo_provider)
        
        results = await web_access.search_web("machine learning basics", max_results=2)
        if results['success']:
            print(f"   Found {len(results['results'])} results from {results['provider']}")
        else:
            print(f"   Error: {results['error']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 2: Google (requires API key and search engine ID)
    print("2. Using Google provider (requires configuration):")
    try:
        # This would require actual API credentials
        # google_provider = GoogleSearchProvider(api_key="your_api_key", search_engine_id="your_search_engine_id")
        # web_access = WebAccess(search_provider=google_provider)
        print("   Google provider requires API key and search engine ID configuration")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 3: Bing (requires API key)
    print("3. Using Bing provider (requires configuration):")
    try:
        # This would require actual API credentials
        # bing_provider = BingSearchProvider(api_key="your_bing_api_key")
        # web_access = WebAccess(search_provider=bing_provider)
        print("   Bing provider requires API key configuration")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()

async def demonstrate_kernel_integration():
    """Demonstrate integration with EchoKernel."""
    print("=== EchoKernel Integration Demo ===")
    
    # Create kernel with OpenAI provider
    # Note: You'll need to set your OpenAI API key
    try:
        # kernel = EchoKernel(
        #     text_provider=OpenAITextProvider(api_key="your_openai_api_key")
        # )
        print("EchoKernel integration requires OpenAI API key configuration")
        print("To test this, uncomment the kernel creation code and add your API key")
        
        # Register tools
        # kernel.register_tool(get_web_content)
        # kernel.register_tool(search_web)
        
        # Example usage:
        # response = await kernel.generate_text(
        #     "Search for Python tutorials and summarize the first result"
        # )
        # print(response)
        
    except Exception as e:
        print(f"Error: {e}")
    
    print()

async def demonstrate_web_content_retrieval():
    """Demonstrate web content retrieval."""
    print("=== Web Content Retrieval Demo ===")
    
    # Create WebAccess instance
    web_access = WebAccess()
    
    # Retrieve content from a simple website
    url = "https://httpbin.org/html"
    print(f"Retrieving content from: {url}")
    
    result = web_access.get_page_content(url)
    
    if result['success']:
        print(f"Title: {result['title']}")
        print(f"Word count: {result['word_count']}")
        print(f"Text preview: {result['text'][:200]}...")
    else:
        print(f"Error: {result['error']}")
    
    print()

async def main():
    """Main demonstration function."""
    print("Web Search Provider Demo")
    print("=" * 50)
    print()
    
    # Demonstrate different aspects of the web search functionality
    await demonstrate_duckduckgo_search()
    await demonstrate_web_access_with_providers()
    await demonstrate_web_content_retrieval()
    await demonstrate_kernel_integration()
    
    print("Demo completed!")
    print("\nTo use Google or Bing search providers:")
    print("1. Get API keys from Google Cloud Console or Microsoft Azure")
    print("2. For Google: Create a Custom Search Engine and get the search engine ID")
    print("3. Configure the providers with your credentials")
    print("4. Use them in your WebAccess instances")

if __name__ == "__main__":
    asyncio.run(main()) 