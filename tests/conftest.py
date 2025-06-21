"""
Pytest configuration and common fixtures for EchoKernel tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.ITextProvider import ITextProvider
from echo_kernel.IEmbeddingProvider import IEmbeddingProvider
from echo_kernel.IStorageProvider import IStorageProvider
from echo_kernel.ITextMemory import ITextMemory


@pytest.fixture
def mock_text_provider():
    """Create a mock text provider for testing."""
    provider = Mock(spec=ITextProvider)
    provider.generate_text = AsyncMock(return_value="Mock response")
    provider.generate_text_with_tools = AsyncMock(return_value="Mock tool response")
    return provider


@pytest.fixture
def mock_embedding_provider():
    """Create a mock embedding provider for testing."""
    provider = Mock(spec=IEmbeddingProvider)
    provider.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
    return provider


@pytest.fixture
def mock_storage_provider():
    """Create a mock storage provider for testing."""
    provider = Mock(spec=IStorageProvider)
    provider.add_text = AsyncMock()
    provider.search_similar = AsyncMock(return_value=[])
    provider.get_text = AsyncMock(return_value=None)
    provider.delete_text = AsyncMock()
    return provider


@pytest.fixture
def mock_memory_provider():
    """Create a mock memory provider for testing."""
    provider = Mock(spec=ITextMemory)
    provider.add_text = AsyncMock()
    provider.search_similar = AsyncMock(return_value=[])
    provider.get_text = AsyncMock(return_value=None)
    provider.delete_text = AsyncMock()
    return provider


@pytest.fixture
def echo_kernel():
    """Create a fresh EchoKernel instance for each test."""
    return EchoKernel()


@pytest.fixture
def sample_tool():
    """Create a sample tool for testing."""
    def sample_tool_function(text: str, count: int = 1) -> str:
        """A sample tool that repeats text."""
        return text * count
    
    return sample_tool_function


@pytest.fixture
def sample_async_tool():
    """Create a sample async tool for testing."""
    async def sample_async_tool_function(text: str, count: int = 1) -> str:
        """A sample async tool that repeats text."""
        await asyncio.sleep(0.01)  # Simulate async work
        return text * count
    
    return sample_async_tool_function


@pytest.fixture
def sample_text_data():
    """Sample text data for testing."""
    return {
        "text": "This is a sample text for testing",
        "metadata": {"source": "test", "category": "sample"}
    }


@pytest.fixture
def sample_embedding():
    """Sample embedding vector for testing."""
    return [0.1, 0.2, 0.3, 0.4, 0.5]


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        {"text": "Result 1", "score": 0.95, "metadata": {"id": "1"}},
        {"text": "Result 2", "score": 0.85, "metadata": {"id": "2"}},
        {"text": "Result 3", "score": 0.75, "metadata": {"id": "3"}}
    ]


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest for EchoKernel tests."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# Async test utilities
class AsyncTestCase:
    """Base class for async test cases."""
    
    @pytest.fixture(autouse=True)
    def setup_event_loop(self, event_loop):
        """Set up event loop for async tests."""
        self.loop = event_loop
        asyncio.set_event_loop(self.loop)
    
    def run_async(self, coro):
        """Run an async coroutine in the test event loop."""
        return self.loop.run_until_complete(coro) 