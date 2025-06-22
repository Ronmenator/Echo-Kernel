"""
DuckDuckGo Search Provider

This module provides a search provider implementation using DuckDuckGo's
Instant Answer API. DuckDuckGo provides free search results without
requiring an API key, making it ideal for development and testing.

The provider:
- Uses DuckDuckGo's Instant Answer API
- Returns structured search results
- Handles errors gracefully
- Implements rate limiting for respectful usage
- Provides both instant answers and web search results

Example:
    ```python
    from echo_kernel.providers.DuckDuckGoSearchProvider import DuckDuckGoSearchProvider
    
    provider = DuckDuckGoSearchProvider()
    results = await provider.search("Python programming")
    ```
"""

import aiohttp
import asyncio
import time
from typing import Dict, List, Optional
from ..ISearchProvider import ISearchProvider
import json

class DuckDuckGoSearchProvider(ISearchProvider):
    """
    DuckDuckGo search provider using the Instant Answer API.
    
    This provider uses DuckDuckGo's free Instant Answer API to perform
    web searches. It doesn't require an API key and provides both
    instant answers and web search results.
    
    Attributes:
        base_url: Base URL for DuckDuckGo Instant Answer API
        last_request_time: Timestamp of last request for rate limiting
        rate_limit_delay: Minimum delay between requests in seconds
    """
    
    def __init__(self, rate_limit_delay: float = 1.0):
        """
        Initialize a new DuckDuckGoSearchProvider instance.
        
        Args:
            rate_limit_delay: Minimum delay between requests in seconds (default: 1.0)
        """
        self.base_url = "https://api.duckduckgo.com/"
        self.last_request_time = 0
        self.rate_limit_delay = rate_limit_delay

    def _rate_limit(self):
        """
        Implement rate limiting between requests.
        
        This method ensures that requests are not made too frequently
        to be respectful to DuckDuckGo's servers.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()

    async def search(self, query: str, max_results: int = 5) -> Dict[str, any]:
        """
        Perform a web search using DuckDuckGo's Instant Answer API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            Dictionary containing search results:
            {
                'success': bool,
                'query': str,
                'results': List[Dict] (if successful),
                'error': str (if failed)
            }
        """
        # Implement rate limiting
        self._rate_limit()
        
        try:
            # Prepare request parameters
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=30) as response:
                    if response.status != 200:
                        return {
                            'success': False,
                            'query': query,
                            'error': f'HTTP {response.status}: {response.reason}'
                        }
                    
                    data = await response.json()
                    
                    # Process the response
                    results = []
                    
                    # Add instant answer if available
                    if data.get('Abstract'):
                        results.append({
                            'title': data.get('AbstractSource', 'DuckDuckGo'),
                            'snippet': data.get('Abstract', ''),
                            'url': data.get('AbstractURL', ''),
                            'type': 'instant_answer'
                        })
                    
                    # Add related topics
                    if data.get('RelatedTopics'):
                        for topic in data.get('RelatedTopics', [])[:max_results]:
                            if isinstance(topic, dict) and topic.get('Text'):
                                results.append({
                                    'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                                    'snippet': topic.get('Text', ''),
                                    'url': topic.get('FirstURL', ''),
                                    'type': 'related_topic'
                                })
                    
                    # Add web search results (if available)
                    if data.get('Results'):
                        for result in data.get('Results', [])[:max_results]:
                            results.append({
                                'title': result.get('Title', ''),
                                'snippet': result.get('Snippet', ''),
                                'url': result.get('FirstURL', ''),
                                'type': 'web_result'
                            })
                    
                    return {
                        'success': True,
                        'query': query,
                        'results': results[:max_results],
                        'total_results': len(results),
                        'provider': 'DuckDuckGo'
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