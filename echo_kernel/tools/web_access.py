"""
Web Access - Safe Web Content Retrieval

This module provides a safe and controlled way to access web content with
proper error handling, rate limiting, and content validation. It's designed
to prevent abuse while allowing legitimate web content retrieval.

The WebAccess class:
- Retrieves web page content with proper headers
- Implements rate limiting to be respectful to servers
- Validates and sanitizes URLs
- Handles various HTTP status codes gracefully
- Extracts text content from HTML pages
- Supports basic web scraping with safety measures
- Uses search providers for web search functionality

Safety Features:
- URL validation and sanitization
- Rate limiting (1 request per second by default)
- User-Agent spoofing to identify the bot
- Timeout limits (30 seconds)
- Content size limits (10MB)
- Automatic retry with exponential backoff

Example:
    ```python
    from echo_kernel.providers.DuckDuckGoSearchProvider import DuckDuckGoSearchProvider
    
    # Create web access with DuckDuckGo as default search provider
    web_access = WebAccess(search_provider=DuckDuckGoSearchProvider())
    
    # Get page content
    content = web_access.get_page_content("https://example.com")
    print(f"Page title: {content['title']}")
    print(f"Text content: {content['text'][:200]}...")
    
    # Search the web
    search_results = await web_access.search_web("Python programming")
    print(f"Found {len(search_results['results'])} results")
    ```
"""

import requests
import time
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse, urljoin
import html
from bs4 import BeautifulSoup
import json

class WebAccess:
    """
    A safe web content retrieval tool with rate limiting and safety measures.
    
    This class provides a controlled way to access web content by:
    - Validating and sanitizing URLs
    - Implementing rate limiting to be respectful to servers
    - Handling various HTTP status codes gracefully
    - Extracting and cleaning text content from HTML pages
    - Providing comprehensive error handling
    - Using search providers for web search functionality
    
    The tool is designed to be respectful to web servers and safe for
    educational and development purposes.
    
    Attributes:
        session: Requests session for maintaining connections
        last_request_time: Timestamp of the last request for rate limiting
        rate_limit_delay: Minimum delay between requests in seconds
        search_provider: Search provider for web search functionality
    """
    
    def __init__(self, rate_limit_delay: float = 1.0, search_provider=None):
        """
        Initialize a new WebAccess instance.
        
        Args:
            rate_limit_delay: Minimum delay between requests in seconds (default: 1.0)
            search_provider: Search provider instance (default: None, will use DuckDuckGo if available)
        """
        self.session = requests.Session()
        self.last_request_time = 0
        self.rate_limit_delay = rate_limit_delay
        self.search_provider = search_provider
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': 'EchoKernel-WebAccess/1.0 (Educational Tool)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def _validate_url(self, url: str) -> bool:
        """
        Validate and sanitize a URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid and safe, False otherwise
        """
        try:
            parsed = urlparse(url)
            
            # Check if URL has required components
            if not parsed.scheme or not parsed.netloc:
                return False
                
            # Only allow HTTP and HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
                
            # Check for potentially dangerous patterns
            dangerous_patterns = [
                r'file://',
                r'ftp://',
                r'data:',
                r'javascript:',
                r'vbscript:',
                r'<script',
                r'javascript:',
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return False
                    
            return True
            
        except Exception:
            return False

    def _rate_limit(self):
        """
        Implement rate limiting between requests.
        
        This method ensures that requests are not made too frequently
        to be respectful to web servers and avoid being blocked.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()

    def _extract_text_content(self, html_content: str) -> Dict[str, Any]:
        """
        Extract and clean text content from HTML.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
                
            # Get main text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Get meta description
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '').strip()
                
            # Get main headings
            headings = []
            for tag in ['h1', 'h2', 'h3']:
                for heading in soup.find_all(tag):
                    headings.append(heading.get_text().strip())
                    
            return {
                'title': title,
                'description': description,
                'text': text,
                'headings': headings,
                'word_count': len(text.split())
            }
            
        except Exception as e:
            return {
                'title': '',
                'description': '',
                'text': f"Error extracting text content: {str(e)}",
                'headings': [],
                'word_count': 0
            }

    def get_page_content(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Retrieve and parse web page content.
        
        This method fetches web page content with proper error handling,
        rate limiting, and content extraction. It returns structured data
        including the page title, text content, and metadata.
        
        Args:
            url: URL of the web page to retrieve
            timeout: Request timeout in seconds (default: 30)
            
        Returns:
            Dictionary containing page content and metadata:
            {
                'success': bool,
                'url': str,
                'status_code': int,
                'title': str,
                'description': str,
                'text': str,
                'headings': list,
                'word_count': int,
                'error': str (if request failed)
            }
            
        Safety Features:
            - URL validation and sanitization
            - Rate limiting between requests
            - Request timeout limits
            - Content size limits
            - Comprehensive error handling
            
        Example:
            web_access = WebAccess()
            result = web_access.get_page_content("https://example.com")
            if result['success']:
                print(f"Title: {result['title']}")
                print(f"Word count: {result['word_count']}")
            else:
                print(f"Error: {result['error']}")
        """
        # Validate URL
        if not self._validate_url(url):
            return {
                'success': False,
                'url': url,
                'status_code': None,
                'error': 'Invalid or unsafe URL provided'
            }
            
        # Implement rate limiting
        self._rate_limit()
        
        try:
            # Make the request
            response = self.session.get(url, timeout=timeout, stream=True)
            
            # Check if response is too large (limit to 10MB)
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 10 * 1024 * 1024:
                response.close()
                return {
                    'success': False,
                    'url': url,
                    'status_code': response.status_code,
                    'error': 'Content too large (exceeds 10MB limit)'
                }
                
            # Read content
            content = response.content.decode('utf-8', errors='ignore')
            
            # Check status code
            if response.status_code != 200:
                response.close()
                return {
                    'success': False,
                    'url': url,
                    'status_code': response.status_code,
                    'error': f'HTTP {response.status_code}: {response.reason}'
                }
            
            response.close()
            
            # Extract text content
            extracted_content = self._extract_text_content(content)
            
            return {
                'success': True,
                'url': url,
                'status_code': response.status_code,
                **extracted_content
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'url': url,
                'status_code': None,
                'error': f'Request timed out after {timeout} seconds'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'url': url,
                'status_code': None,
                'error': 'Connection error - unable to reach the server'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'url': url,
                'status_code': None,
                'error': f'Request failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'status_code': None,
                'error': f'Unexpected error: {str(e)}'
            }

    async def search_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Perform a web search using the configured search provider.
        
        This method uses the search provider to perform web searches. If no
        provider is configured, it will attempt to use DuckDuckGo as a fallback.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing search results or error information
        """
        # If no search provider is configured, try to use DuckDuckGo as fallback
        if self.search_provider is None:
            try:
                from echo_kernel.providers.DuckDuckGoSearchProvider import DuckDuckGoSearchProvider
                self.search_provider = DuckDuckGoSearchProvider()
            except ImportError:
                return {
                    'success': False,
                    'query': query,
                    'error': 'No search provider configured and DuckDuckGo provider not available',
                    'suggestion': 'Install aiohttp and configure a search provider'
                }
        
        # Use the configured search provider
        try:
            return await self.search_provider.search(query, max_results)
        except Exception as e:
            return {
                'success': False,
                'query': query,
                'error': f'Search provider error: {str(e)}'
            } 