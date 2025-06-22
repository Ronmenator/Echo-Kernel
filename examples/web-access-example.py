"""
Web Access Tool Example

This example demonstrates how to use the web access tool with EchoKernel
to retrieve web page content and extract information.

The example shows:
- Registering the web access tool with the kernel
- Using the tool to retrieve web page content
- Processing the returned structured data
- Error handling for failed requests

Run this example with:
    python examples/web-access-example.py
"""

import asyncio
import json
from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.providers.OpenAITextProvider import OpenAITextProvider
from tools.WebAccessTool import get_web_content, search_web

async def main():
    """Main example function demonstrating web access tool usage."""
    
    # Initialize the kernel with OpenAI provider
    # Make sure to set your OPENAI_API_KEY environment variable
    kernel = EchoKernel()
    
    # Register the web access tools
    kernel.register_tool(get_web_content)
    kernel.register_tool(search_web)
    
    print("🌐 Web Access Tool Example")
    print("=" * 50)
    
    # Example 1: Retrieve content from a simple website
    print("\n1. Retrieving content from example.com...")
    try:
        result = await kernel.generate_text(
            "Use the get_web_content tool to retrieve the content from https://example.com"
        )
        print(f"AI Response: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Extract specific information from a website
    print("\n2. Extracting information from a news website...")
    try:
        result = await kernel.generate_text(
            "Use the get_web_content tool to get the latest news from https://httpbin.org/html and summarize the main points"
        )
        print(f"AI Response: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Demonstrate error handling
    print("\n3. Testing error handling with invalid URL...")
    try:
        result = await kernel.generate_text(
            "Use the get_web_content tool to retrieve content from an invalid URL like 'not-a-url' and explain what went wrong"
        )
        print(f"AI Response: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Using the search placeholder
    print("\n4. Testing the search web tool (placeholder)...")
    try:
        result = await kernel.generate_text(
            "Use the search_web tool to search for 'Python programming tutorials' and explain what the tool returned"
        )
        print(f"AI Response: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Direct tool usage demonstration
    print("\n5. Direct tool usage demonstration...")
    try:
        # Use the tool directly
        content_result = get_web_content("https://httpbin.org/json")
        print("Direct tool result:")
        print(json.dumps(json.loads(content_result), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def demonstrate_web_access_features():
    """Demonstrate the WebAccess class features directly."""
    
    print("\n🔧 WebAccess Class Features Demonstration")
    print("=" * 50)
    
    from tools.web_access import WebAccess
    
    # Create web access instance
    web_access = WebAccess()
    
    # Test URL validation
    print("\nURL Validation Tests:")
    test_urls = [
        "https://example.com",
        "http://httpbin.org/json",
        "file:///etc/passwd",  # Should be rejected
        "javascript:alert('xss')",  # Should be rejected
        "not-a-url",  # Should be rejected
    ]
    
    for url in test_urls:
        is_valid = web_access._validate_url(url)
        print(f"  {url}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test content retrieval
    print("\nContent Retrieval Test:")
    try:
        result = web_access.get_page_content("https://httpbin.org/json")
        if result['success']:
            print(f"  ✅ Successfully retrieved content from {result['url']}")
            print(f"  📄 Status Code: {result['status_code']}")
            print(f"  📝 Word Count: {result['word_count']}")
        else:
            print(f"  ❌ Failed to retrieve content: {result['error']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("Starting Web Access Tool Example...")
    
    # First demonstrate the WebAccess class features
    demonstrate_web_access_features()
    
    # Then run the async example
    print("\n" + "=" * 60)
    print("Running async example with EchoKernel...")
    print("Note: Make sure OPENAI_API_KEY is set in your environment")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error running async example: {e}")
        print("This might be due to missing OPENAI_API_KEY or network issues.") 