"""
Google Search Provider

This module provides a search provider implementation using Google's
Custom Search API. This requires a Google API key and Custom Search
Engine ID to function.

The provider:
- Uses Google Custom Search API
- Returns structured search results
- Handles errors gracefully
- Implements rate limiting for respectful usage
- Provides high-quality web search results

Example:
    ```python
    from echo_kernel.providers.GoogleSearchProvider import GoogleSearchProvider
    
    provider = GoogleSearchProvider(api_key="your_api_key", search_engine_id="your_search_engine_id")
    results = await provider.search("Python programming")
    ```
"""

import aiohttp
import asyncio
import time
from typing import Dict, List, Optional
from ..ISearchProvider import ISearchProvider
import json

class GoogleSearchProvider(ISearchProvider):
    """
    Google search provider using the Custom Search API.
    
    This provider uses Google's Custom Search API to perform web searches.
    It requires a Google API key and Custom Search Engine ID to function.
    
    Attributes:
        api_key: Google API key for authentication
        search_engine_id: Custom Search Engine ID
        base_url: Base URL for Google Custom Search API
        last_request_time: Timestamp of last request for rate limiting
        rate_limit_delay: Minimum delay between requests in seconds
    """
    
    def __init__(self, api_key: str, search_engine_id: str, rate_limit_delay: float = 1.0):
        """
        Initialize a new GoogleSearchProvider instance.
        
        Args:
            api_key: Google API key for authentication
            search_engine_id: Custom Search Engine ID
            rate_limit_delay: Minimum delay between requests in seconds (default: 1.0)
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.last_request_time = 0
        self.rate_limit_delay = rate_limit_delay

    def _rate_limit(self):
        """
        Implement rate limiting between requests.
        
        This method ensures that requests are not made too frequently
        to stay within Google's API rate limits.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()

    async def search(self, query: str, max_results: int = 5) -> Dict[str, any]:
        """
        Perform a web search using Google's Custom Search API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 5, max: 10)
            
        Returns:
            Dictionary containing search results:
            {
                'success': bool,
                'query': str,
                'results': List[Dict] (if successful),
                'error': str (if failed)
            }
        """
        # Validate max_results (Google API limit is 10 per request)
        if max_results > 10:
            max_results = 10
        
        # Implement rate limiting
        self._rate_limit()
        
        try:
            # Prepare request parameters
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(max_results, 10)  # Google API limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=30) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'query': query,
                            'error': f'HTTP {response.status}: {response.reason}. {error_text}'
                        }
                    
                    data = await response.json()
                    
                    # Check for API errors
                    if 'error' in data:
                        return {
                            'success': False,
                            'query': query,
                            'error': f"Google API Error: {data['error'].get('message', 'Unknown error')}"
                        }
                    
                    # Process the response
                    results = []
                    
                    if 'items' in data:
                        for item in data['items']:
                            results.append({
                                'title': item.get('title', ''),
                                'snippet': item.get('snippet', ''),
                                'url': item.get('link', ''),
                                'type': 'web_result'
                            })
                    
                    return {
                        'success': True,
                        'query': query,
                        'results': results[:max_results],
                        'total_results': data.get('searchInformation', {}).get('totalResults', len(results)),
                        'provider': 'Google'
                    }
                    
        except asyncio.TimeoutError:
            return {
                'success': False,
                'query': query,
                'error': 'Request timed out after 30 seconds'
            }
        except aiohttp.ClientError as e:
            return {
                'success': False,
                'query': query,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'query': query,
                'error': f'Unexpected error: {str(e)}'
            } 