"""
Bing Search Provider

This module provides a search provider implementation using Microsoft's
Bing Search API. This requires a Bing Search API key to function.

The provider:
- Uses Bing Search API
- Returns structured search results
- Handles errors gracefully
- Implements rate limiting for respectful usage
- Provides high-quality web search results

Example:
    ```python
    from echo_kernel.providers.BingSearchProvider import BingSearchProvider
    
    provider = BingSearchProvider(api_key="your_bing_api_key")
    results = await provider.search("Python programming")
    ```
"""

import aiohttp
import asyncio
import time
from typing import Dict, List, Optional
from ..ISearchProvider import ISearchProvider
import json

class BingSearchProvider(ISearchProvider):
    """
    Bing search provider using the Bing Search API.
    
    This provider uses Microsoft's Bing Search API to perform web searches.
    It requires a Bing Search API key to function.
    
    Attributes:
        api_key: Bing Search API key for authentication
        base_url: Base URL for Bing Search API
        last_request_time: Timestamp of last request for rate limiting
        rate_limit_delay: Minimum delay between requests in seconds
    """
    
    def __init__(self, api_key: str, rate_limit_delay: float = 1.0):
        """
        Initialize a new BingSearchProvider instance.
        
        Args:
            api_key: Bing Search API key for authentication
            rate_limit_delay: Minimum delay between requests in seconds (default: 1.0)
        """
        self.api_key = api_key
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
        self.last_request_time = 0
        self.rate_limit_delay = rate_limit_delay

    def _rate_limit(self):
        """
        Implement rate limiting between requests.
        
        This method ensures that requests are not made too frequently
        to stay within Bing's API rate limits.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()

    async def search(self, query: str, max_results: int = 5) -> Dict[str, any]:
        """
        Perform a web search using Bing's Search API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 5, max: 50)
            
        Returns:
            Dictionary containing search results:
            {
                'success': bool,
                'query': str,
                'results': List[Dict] (if successful),
                'error': str (if failed)
            }
        """
        # Validate max_results (Bing API limit is 50 per request)
        if max_results > 50:
            max_results = 50
        
        # Implement rate limiting
        self._rate_limit()
        
        try:
            # Prepare request parameters
            params = {
                'q': query,
                'count': min(max_results, 50),  # Bing API limit
                'responseFilter': 'Webpages',
                'textFormat': 'Raw'
            }
            
            # Prepare headers
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, headers=headers, timeout=30) as response:
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
                            'error': f"Bing API Error: {data['error'].get('message', 'Unknown error')}"
                        }
                    
                    # Process the response
                    results = []
                    
                    if 'webPages' in data and 'value' in data['webPages']:
                        for item in data['webPages']['value']:
                            results.append({
                                'title': item.get('name', ''),
                                'snippet': item.get('snippet', ''),
                                'url': item.get('url', ''),
                                'type': 'web_result'
                            })
                    
                    return {
                        'success': True,
                        'query': query,
                        'results': results[:max_results],
                        'total_results': data.get('webPages', {}).get('totalEstimatedMatches', len(results)),
                        'provider': 'Bing'
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