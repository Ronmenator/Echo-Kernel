# Define the ISearchProvider protocol
from typing import Dict, Protocol, runtime_checkable, List, Optional


@runtime_checkable
class ISearchProvider(Protocol):
    async def search(self, query: str, max_results: int = 5) -> Dict[str, any]:
        """
        Perform a web search using the provider's search engine.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing search results with the following structure:
            {
                'success': bool,
                'query': str,
                'results': List[Dict] (if successful),
                'error': str (if failed)
            }
        """
        ... 