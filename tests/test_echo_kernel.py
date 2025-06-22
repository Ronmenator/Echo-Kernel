"""
Unit tests for EchoKernel core functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.Tool import EchoTool
from echo_kernel.EchoTool import EchoTool as EchoToolClass
from echo_kernel.ITextProvider import ITextProvider
from echo_kernel.IEmbeddingProvider import IEmbeddingProvider
from echo_kernel.IStorageProvider import IStorageProvider
from echo_kernel.agents.MemoryAgent import MemoryAgent


@pytest.fixture
def mock_text_provider():
    mock = Mock(spec=ITextProvider)
    # Return 'Mock tool response' only if tools is a non-empty list
    async def generate_text_with_tools(prompt, system_prompt=None, tools=None, **kwargs):
        if tools and len(tools) > 0:
            return "Mock tool response"
        return "Mock response"
    mock.generate_text.side_effect = generate_text_with_tools
    return mock

@pytest.fixture
def mock_embedding_provider():
    mock = Mock(spec=IEmbeddingProvider)
    mock.generate_embedding.return_value = [0.1, 0.2, 0.3]
    return mock

@pytest.fixture
def mock_storage_provider():
    mock = Mock(spec=IStorageProvider)
    mock.get_vector_store = Mock(return_value=AsyncMock())
    return mock

@pytest.fixture
def sample_tool():
    def sample_tool_function(text: str) -> str:
        return f"Processed: {text}"
    return EchoToolClass(
        name="sample_tool",
        func=sample_tool_function,
        description="A sample tool.",
    )

@pytest.fixture
def sample_async_tool():
    async def sample_async_tool_function(text: str) -> str:
        return f"Processed async: {text}"
    return EchoToolClass(
        name="sample_async_tool",
        func=sample_async_tool_function,
        description="A sample async tool.",
    )

class TestEchoKernel:
    """Test cases for EchoKernel class."""

    @pytest.mark.unit
    def test_kernel_initialization(self, mock_storage_provider):
        kernel = EchoKernel(storage_provider=mock_storage_provider)
        assert isinstance(kernel, EchoKernel)
        assert kernel.storage_provider is not None
        assert len(kernel.tools) == 0

    @pytest.mark.unit
    def test_register_tool(self, sample_tool):
        kernel = EchoKernel()
        kernel.register_tool(sample_tool)
        assert len(kernel.tools) == 1
        assert kernel.get_tool("sample_tool") == sample_tool

    @pytest.mark.asyncio
    async def test_generate_text_with_provider(self, mock_text_provider):
        kernel = EchoKernel(text_provider=mock_text_provider)
        result = await kernel.generate_text("Test prompt")
        assert result == "Mock response"
        mock_text_provider.generate_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_embedding_with_provider(self, mock_embedding_provider):
        kernel = EchoKernel(embedding_provider=mock_embedding_provider)
        result = await kernel.generate_embedding("Test text")
        assert result == [0.1, 0.2, 0.3]
        mock_embedding_provider.generate_embedding.assert_called_once()

    @pytest.mark.unit
    def test_get_tool_definitions(self, sample_tool):
        kernel = EchoKernel()
        kernel.register_tool(sample_tool)
        descriptions = kernel.get_tool_definitions()
        assert len(descriptions) == 1
        assert descriptions[0]["name"] == "sample_tool"

    @pytest.mark.asyncio
    async def test_execute_tool(self, sample_tool):
        kernel = EchoKernel()
        kernel.register_tool(sample_tool)
        result = await kernel.execute_tool("sample_tool", text="hello")
        assert result == "Processed: hello"

    @pytest.mark.asyncio
    async def test_execute_async_tool(self, sample_async_tool):
        kernel = EchoKernel()
        kernel.register_tool(sample_async_tool)
        result = await kernel.execute_tool("sample_async_tool", text="hello")
        assert result == "Processed async: hello"

    @pytest.mark.unit
    def test_clear_tools(self, sample_tool):
        kernel = EchoKernel()
        kernel.register_tool(sample_tool)
        assert len(kernel.tools) == 1
        kernel.clear_tools()
        assert len(kernel.tools) == 0

    @pytest.mark.unit
    def test_echo_kernel_initialization(self):
        """Test EchoKernel initialization."""
        kernel = EchoKernel()
        
        assert kernel is not None
        assert hasattr(kernel, 'text_providers')
        assert hasattr(kernel, 'embedding_providers')
        assert hasattr(kernel, 'memory_providers')
        assert hasattr(kernel, 'tools')
        assert isinstance(kernel.text_providers, list)
        assert isinstance(kernel.embedding_providers, list)
        assert isinstance(kernel.memory_providers, list)
        assert isinstance(kernel.tools, list)

    @pytest.mark.unit
    def test_register_text_provider(self, echo_kernel, mock_text_provider):
        """Test registering a text provider."""
        initial_count = len(echo_kernel.text_providers)
        
        echo_kernel.register_provider(mock_text_provider)
        
        assert len(echo_kernel.text_providers) == initial_count + 1
        assert mock_text_provider in echo_kernel.text_providers

    @pytest.mark.unit
    def test_register_embedding_provider(self, echo_kernel, mock_embedding_provider):
        """Test registering an embedding provider."""
        initial_count = len(echo_kernel.embedding_providers)
        
        echo_kernel.register_provider(mock_embedding_provider)
        
        assert len(echo_kernel.embedding_providers) == initial_count + 1
        assert mock_embedding_provider in echo_kernel.embedding_providers

    @pytest.mark.unit
    def test_register_memory_provider(self, echo_kernel, mock_memory_provider):
        """Test registering a memory provider."""
        initial_count = len(echo_kernel.memory_providers)
        
        echo_kernel.register_provider(mock_memory_provider)
        
        assert len(echo_kernel.memory_providers) == initial_count + 1
        assert mock_memory_provider in echo_kernel.memory_providers

    @pytest.mark.unit
    def test_register_tool_with_decorator(self, echo_kernel):
        """Test registering a tool using the EchoTool decorator."""
        @EchoTool(description="Test tool")
        def test_tool(text: str) -> str:
            return f"Processed: {text}"
        
        initial_count = len(echo_kernel.tools)
        echo_kernel.register_tool(test_tool)
        
        assert len(echo_kernel.tools) == initial_count + 1
        # Check that the tool was registered with the correct name
        assert echo_kernel.get_tool("test_tool") is not None

    @pytest.mark.asyncio
    async def test_generate_text_without_provider(self, echo_kernel):
        """Test text generation without any registered providers."""
        with pytest.raises(ValueError, match="No text providers registered"):
            await echo_kernel.generate_text("Test prompt")

    @pytest.mark.asyncio
    async def test_generate_text_with_tools(self, echo_kernel, mock_text_provider, sample_tool):
        """Test text generation with tools."""
        echo_kernel.register_provider(mock_text_provider)
        echo_kernel.register_tool(sample_tool)  # Register a tool so tools is non-empty

        result = await echo_kernel.generate_text_with_tools("Test prompt")

        assert result == "Mock tool response"
        # Check that generate_text was called with tools
        assert mock_text_provider.generate_text.call_args[1]["tools"] is not None

    @pytest.mark.asyncio
    async def test_generate_text_with_tools_without_provider(self, echo_kernel):
        """Test text generation with tools without any registered providers."""
        with pytest.raises(ValueError, match="No text providers registered"):
            await echo_kernel.generate_text_with_tools("Test prompt")

    @pytest.mark.asyncio
    async def test_generate_embedding_without_provider(self, echo_kernel):
        """Test embedding generation without any registered providers."""
        with pytest.raises(ValueError, match="No embedding providers registered"):
            await echo_kernel.generate_embedding("Test text")

    @pytest.mark.asyncio
    async def test_add_text_to_memory(self, echo_kernel, mock_memory_provider):
        """Test adding text to memory."""
        echo_kernel.register_provider(mock_memory_provider)
        
        await echo_kernel.add_text_to_memory("Test text", {"source": "test"})
        
        mock_memory_provider.add_text.assert_called_once_with("Test text", {"source": "test"})

    @pytest.mark.asyncio
    async def test_add_text_to_memory_without_provider(self, echo_kernel):
        """Test adding text to memory without any registered providers."""
        with pytest.raises(ValueError, match="No memory providers registered"):
            await echo_kernel.add_text_to_memory("Test text", {"source": "test"})

    @pytest.mark.asyncio
    async def test_search_memory(self, echo_kernel, mock_memory_provider, sample_search_results):
        """Test searching memory."""
        mock_memory_provider.search_similar.return_value = sample_search_results
        echo_kernel.register_provider(mock_memory_provider)
        
        result = await echo_kernel.search_memory("Test query")
        
        assert result == sample_search_results
        mock_memory_provider.search_similar.assert_called_once_with("Test query")

    @pytest.mark.asyncio
    async def test_search_memory_without_provider(self, echo_kernel):
        """Test searching memory without any registered providers."""
        with pytest.raises(ValueError, match="No memory providers registered"):
            await echo_kernel.search_memory("Test query")

    @pytest.mark.unit
    def test_get_provider_by_type(self, echo_kernel, mock_text_provider, mock_embedding_provider):
        """Test getting providers by type."""
        echo_kernel.register_provider(mock_text_provider)
        echo_kernel.register_provider(mock_embedding_provider)
        
        text_providers = echo_kernel.get_providers_by_type(ITextProvider)
        embedding_providers = echo_kernel.get_providers_by_type(IEmbeddingProvider)
        
        assert len(text_providers) == 1
        assert len(embedding_providers) == 1
        assert text_providers[0] == mock_text_provider
        assert embedding_providers[0] == mock_embedding_provider

    @pytest.mark.unit
    def test_get_provider_by_type_empty(self, echo_kernel):
        """Test getting providers by type when none are registered."""
        text_providers = echo_kernel.get_providers_by_type(ITextProvider)
        
        assert len(text_providers) == 0

    @pytest.mark.unit
    def test_clear_providers(self, echo_kernel, mock_text_provider, mock_embedding_provider):
        """Test clearing all providers."""
        echo_kernel.register_provider(mock_text_provider)
        echo_kernel.register_provider(mock_embedding_provider)
        
        echo_kernel.clear_providers()
        
        assert len(echo_kernel.text_providers) == 0
        assert len(echo_kernel.embedding_providers) == 0
        assert len(echo_kernel.memory_providers) == 0

    @pytest.mark.unit
    def test_kernel_state_management(self, echo_kernel):
        """Test kernel state management."""
        # Test initial state
        assert echo_kernel.text_providers == []
        assert echo_kernel.embedding_providers == []
        assert echo_kernel.memory_providers == []
        assert echo_kernel.tools == []
        
        # Test state after adding providers
        mock_provider = Mock()
        echo_kernel.register_provider(mock_provider)
        
        assert len(echo_kernel.text_providers) > 0 or len(echo_kernel.embedding_providers) > 0 or len(echo_kernel.memory_providers) > 0
        
        # Test state after clearing
        echo_kernel.clear_providers()
        assert echo_kernel.text_providers == []
        assert echo_kernel.embedding_providers == []
        assert echo_kernel.memory_providers == []

    @pytest.mark.unit
    def test_provider_registration_duplicates(self, echo_kernel, mock_text_provider):
        """Test that duplicate providers are handled correctly."""
        echo_kernel.register_provider(mock_text_provider)
        initial_count = len(echo_kernel.text_providers)
        
        # Register the same provider again
        echo_kernel.register_provider(mock_text_provider)
        
        # Should not add duplicates
        assert len(echo_kernel.text_providers) == initial_count

    @pytest.mark.unit
    def test_tool_registration_duplicates(self, echo_kernel, sample_tool):
        """Test that duplicate tools are handled correctly."""
        echo_kernel.register_tool(sample_tool)
        initial_count = len(echo_kernel.tools)
        # Register the same tool again
        echo_kernel.register_tool(sample_tool)
        # Should not add duplicates
        assert len(echo_kernel.tools) == initial_count 