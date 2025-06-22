"""
Tests for Search Providers

This module contains tests for the search provider implementations.
"""

import pytest
import asyncio
from echo_kernel.providers.DuckDuckGoSearchProvider import DuckDuckGoSearchProvider
from echo_kernel.providers.GoogleSearchProvider import GoogleSearchProvider
from echo_kernel.providers.BingSearchProvider import BingSearchProvider
from tools.web_access import WebAccess

class TestDuckDuckGoSearchProvider:
    """Test DuckDuckGo search provider."""
    
    @pytest.fixture
    def provider(self):
        """Create a DuckDuckGo search provider instance."""
        return DuckDuckGoSearchProvider()
    
    @pytest.mark.asyncio
    async def test_search_basic(self, provider):
        """Test basic search functionality."""
        results = await provider.search("Python programming", max_results=3)
        
        assert isinstance(results, dict)
        assert 'success' in results
        assert 'query' in results
        assert results['query'] == "Python programming"
        
        if results['success']:
            assert 'results' in results
            assert 'provider' in results
            assert results['provider'] == 'DuckDuckGo'
            assert len(results['results']) <= 3
        else:
            assert 'error' in results
    
    @pytest.mark.asyncio
    async def test_search_empty_query(self, provider):
        """Test search with empty query."""
        results = await provider.search("", max_results=3)
        
        assert isinstance(results, dict)
        assert 'success' in results
        assert 'query' in results
        assert results['query'] == ""
    
    @pytest.mark.asyncio
    async def test_search_max_results(self, provider):
        """Test search with different max_results values."""
        results = await provider.search("test", max_results=1)
        
        assert isinstance(results, dict)
        if results['success']:
            assert len(results['results']) <= 1

class TestGoogleSearchProvider:
    """Test Google search provider."""
    
    def test_initialization_without_credentials(self):
        """Test that provider can be initialized without credentials."""
        # Should not raise an exception
        provider = GoogleSearchProvider(api_key="test_key", search_engine_id="test_id")
        assert provider.api_key == "test_key"
        assert provider.search_engine_id == "test_id"
    
    @pytest.mark.asyncio
    async def test_search_without_valid_credentials(self):
        """Test search with invalid credentials."""
        provider = GoogleSearchProvider(api_key="invalid_key", search_engine_id="invalid_id")
        results = await provider.search("test query")
        
        assert isinstance(results, dict)
        assert 'success' in results
        assert 'query' in results
        # Should fail due to invalid credentials
        assert not results['success']
        assert 'error' in results

class TestBingSearchProvider:
    """Test Bing search provider."""
    
    def test_initialization_without_credentials(self):
        """Test that provider can be initialized without credentials."""
        # Should not raise an exception
        provider = BingSearchProvider(api_key="test_key")
        assert provider.api_key == "test_key"
    
    @pytest.mark.asyncio
    async def test_search_without_valid_credentials(self):
        """Test search with invalid credentials."""
        provider = BingSearchProvider(api_key="invalid_key")
        results = await provider.search("test query")
        
        assert isinstance(results, dict)
        assert 'success' in results
        assert 'query' in results
        # Should fail due to invalid credentials
        assert not results['success']
        assert 'error' in results

class TestWebAccessWithProviders:
    """Test WebAccess class with search providers."""
    
    @pytest.mark.asyncio
    async def test_web_access_with_duckduckgo(self):
        """Test WebAccess with DuckDuckGo provider."""
        provider = DuckDuckGoSearchProvider()
        web_access = WebAccess(search_provider=provider)
        
        results = await web_access.search_web("test query", max_results=2)
        
        assert isinstance(results, dict)
        assert 'success' in results
        assert 'query' in results
        assert results['query'] == "test query"
    
    @pytest.mark.asyncio
    async def test_web_access_without_provider(self):
        """Test WebAccess without provider (should fallback to DuckDuckGo)."""
        web_access = WebAccess()
        
        results = await web_access.search_web("test query", max_results=2)
        
        assert isinstance(results, dict)
        assert 'success' in results
        assert 'query' in results
        assert results['query'] == "test query"
    
    def test_web_access_page_content(self):
        """Test WebAccess page content retrieval."""
        web_access = WebAccess()
        
        # Test with a simple HTTP endpoint
        result = web_access.get_page_content("https://httpbin.org/html")
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'url' in result
        assert result['url'] == "https://httpbin.org/html"
        
        if result['success']:
            assert 'title' in result
            assert 'text' in result
            assert 'word_count' in result
        else:
            assert 'error' in result
    
    def test_web_access_invalid_url(self):
        """Test WebAccess with invalid URL."""
        web_access = WebAccess()
        
        result = web_access.get_page_content("invalid-url")
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert not result['success']
        assert 'error' in result 