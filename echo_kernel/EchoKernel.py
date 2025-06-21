"""
EchoKernel - Core Framework Module

This module provides the main EchoKernel class, which serves as the central hub for
managing AI providers, tools, and services in the EchoKernel framework.

The EchoKernel acts as a service locator and orchestrator, allowing you to:
- Register and manage different AI providers (text generation, embeddings)
- Register and use custom tools
- Generate text with context and tool integration
- Generate embeddings for vector operations
- Retrieve services by type for advanced usage

Example:
    ```python
    from echo_kernel import EchoKernel, AzureOpenAITextProvider
    
    # Create kernel and register provider
    kernel = EchoKernel()
    text_provider = AzureOpenAITextProvider(api_key="...", ...)
    kernel.register_provider(text_provider)
    
    # Generate text
    result = await kernel.generate_text("Hello, world!")
    print(result)
    ```
"""

from typing import List, Dict, Any, Callable, Optional, TypeVar, Type, cast, Protocol, runtime_checkable
from echo_kernel.IEmbeddingProvider import IEmbeddingProvider
from echo_kernel.ITextProvider import ITextProvider
from echo_kernel.ITextMemory import ITextMemory
from echo_kernel.IEchoTool import IEchoTool
from echo_kernel.Tool import EchoTool
from echo_kernel.IStorageProvider import IStorageProvider
import asyncio
import inspect
import functools

T = TypeVar('T')

class EchoKernel:
    """
    The central hub for managing AI providers, tools, and services.
    
    EchoKernel provides a unified interface for working with different AI providers
    and tools. It acts as a service locator, allowing you to register providers
    and tools, then use them through a consistent API.
    
    Attributes:
        providers: List of registered provider services
        _tools: Dictionary mapping tool names to tool instances
    """
    
    def __init__(self):
        """Initialize the EchoKernel."""
        self._text_providers: List[ITextProvider] = []
        self._embedding_providers: List[IEmbeddingProvider] = []
        self._memory_providers: List[ITextMemory] = []
        self._storage_providers: List[IStorageProvider] = []
        self._tools: Dict[str, IEchoTool] = {}  # Keyed by tool name

    @property
    def text_providers(self) -> List[ITextProvider]:
        """Get all registered text providers."""
        return self._text_providers

    @property
    def embedding_providers(self) -> List[IEmbeddingProvider]:
        """Get all registered embedding providers."""
        return self._embedding_providers

    @property
    def memory_providers(self) -> List[ITextMemory]:
        """Get all registered memory providers."""
        return self._memory_providers

    @property
    def tools(self) -> List[IEchoTool]:
        return list(self._tools.values())

    def register_provider(self, provider: any) -> None:
        """
        Register a provider service with the kernel.
        
        Providers can be text providers (for text generation), embedding providers
        (for vector embeddings), or other service types that implement the
        appropriate interfaces.
        
        Args:
            provider: The provider service to register. Must implement one of the
                     provider interfaces (ITextProvider, IEmbeddingProvider, etc.)
        
        Example:
            ```python
            text_provider = AzureOpenAITextProvider(api_key="...", ...)
            kernel.register_provider(text_provider)
            ```
        """
        # Prevent duplicate registrations
        if provider not in self._text_providers and provider not in self._embedding_providers and provider not in self._memory_providers and provider not in self._storage_providers:
            if isinstance(provider, ITextProvider):
                self._text_providers.append(provider)
            elif isinstance(provider, IEmbeddingProvider):
                self._embedding_providers.append(provider)
            elif isinstance(provider, ITextMemory):
                self._memory_providers.append(provider)
            elif isinstance(provider, IStorageProvider):
                self._storage_providers.append(provider)

    def register_tool(self, tool: Callable) -> None:
        """
        Register a tool with the kernel.

        Tools are callable functions that can be invoked by AI models during
        text generation. They must implement the IEchoTool protocol.

        Args:
            tool: The tool to register. Must implement the IEchoTool protocol.

        Raises:
            TypeError: If the tool doesn't implement the IEchoTool protocol.

        Example:
            ```python
            @EchoTool(description="A custom tool")
            def my_tool(param: str) -> str:
                return f"Processed: {param}"

            kernel.register_tool(my_tool)
            ```
        """
        # If the tool is not already decorated, decorate it
        if not hasattr(tool, 'name') or not hasattr(tool, 'definition'):
            tool = EchoTool(description=f"Tool: {tool.__name__}")(tool)
        # Prevent duplicate registrations by name
        if tool.name in self._tools:
            return
        self._tools[tool.name] = tool

    def get_service(self, service_type: Type[T]) -> Optional[T]:
        """
        Get a registered service of the specified type.
        
        This method allows you to retrieve specific services from the kernel
        by their type, enabling advanced usage patterns and service composition.
        
        Args:
            service_type: The type of service to retrieve.
        
        Returns:
            The first registered service of the specified type, or None if not found.
        
        Example:
            ```python
            # Get the text memory service
            memory_service = kernel.get_service(ITextMemory)
            if memory_service:
                await memory_service.add_text("Important info", {"source": "user"})
            ```
        """
        for provider in self._text_providers + self._embedding_providers + self._memory_providers + self._storage_providers:
            if isinstance(provider, service_type):
                return cast(T, provider)
        return None

    def get_providers_by_type(self, provider_type: Type[T]) -> List[T]:
        """
        Get all registered providers of the specified type.
        
        Args:
            provider_type: The type of provider to retrieve.
        
        Returns:
            List of providers of the specified type.
        """
        return [cast(T, p) for p in self._text_providers + self._embedding_providers + self._memory_providers + self._storage_providers if isinstance(p, provider_type)]

    def clear_providers(self) -> None:
        """Clear all registered providers."""
        self._text_providers.clear()
        self._embedding_providers.clear()
        self._memory_providers.clear()
        self._storage_providers.clear()
        self._tools.clear()

    def clear_tools(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()

    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get descriptions of all registered tools."""
        return [tool.definition for tool in self.tools]

    async def execute_tool(self, tool: IEchoTool | str, *args, **kwargs) -> Any:
        """Execute a registered tool."""
        if isinstance(tool, str):
            tool_obj = self._tools.get(tool)
            if not tool_obj:
                raise ValueError(f"Tool not found: {tool}")
            tool = tool_obj
        elif hasattr(tool, 'name') and tool.name in self._tools:
            tool = self._tools[tool.name]
        else:
            raise ValueError("Tool not registered")
        
        result = tool(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    async def add_text_to_memory(self, text: str, metadata: Dict[str, Any] = None) -> None:
        """Add text to memory."""
        if not self._memory_providers:
            raise ValueError("No memory providers registered")
        
        for provider in self._memory_providers:
            if isinstance(provider, ITextMemory):
                await provider.add_text(text, metadata or {})
                return
        
        raise ValueError("No memory providers available")

    async def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """Search memory for similar content."""
        if not self._memory_providers:
            raise ValueError("No memory providers registered")
        
        for provider in self._memory_providers:
            if isinstance(provider, ITextMemory):
                return await provider.search_similar(query)
        
        raise ValueError("No memory providers available")

    async def generate_text_with_tools(self, prompt: str, **kwargs) -> str:
        """
        Generate text with tools enabled.
        
        Args:
            prompt: The prompt for text generation.
            **kwargs: Additional arguments for text generation.
        
        Returns:
            Generated text.
        """
        if not self._text_providers:
            raise ValueError("No text providers registered")
        
        for provider in self._text_providers:
            if isinstance(provider, ITextProvider):
                # Try to use generate_text_with_tools if available
                if hasattr(provider, 'generate_text_with_tools'):
                    return await provider.generate_text_with_tools(prompt, **kwargs)
                else:
                    # Fall back to generate_text with tools
                    return await self.generate_text(prompt, tools=self.tool_definitions, tool_implementations=self.tool_instances, **kwargs)
        
        raise ValueError("No text providers registered")

    @property
    def tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get all registered tool definitions.
        
        Returns:
            List of tool definition dictionaries that can be passed to AI providers.
        """
        return [tool.definition for tool in self.tools]

    @property
    def tool_instances(self) -> Dict[str, Callable]:
        """
        Get all registered tool instances.
        
        Returns:
            Dictionary mapping tool names to their callable implementations.
        """
        return {name: tool for name, tool in self._tools.items()}

    async def generate_text(
        self, 
        prompt: str, 
        system_message: str = "", 
        context: Dict = None, 
        temperature: float = 0.7, 
        max_tokens: int = 1000, 
        top_p: float = 1, 
        frequency_penalty: float = 0, 
        presence_penalty: float = 0, 
        tools = None,
        tool_implementations = None
    ) -> str:
        """
        Generate text using registered text providers.
        
        This is the main method for text generation. It automatically uses
        registered tools and can work with any registered text provider.
        
        Args:
            prompt: The main prompt for text generation.
            system_message: Optional system message to set context.
            context: Optional context dictionary for the generation.
            temperature: Controls randomness (0.0 = deterministic, 1.0 = very random).
            max_tokens: Maximum number of tokens to generate.
            top_p: Nucleus sampling parameter.
            frequency_penalty: Penalty for frequent tokens.
            presence_penalty: Penalty for new tokens.
            tools: Optional list of tool definitions to use.
            tool_implementations: Optional dictionary mapping tool names to their callable implementations.
        
        Returns:
            Generated text string.
        
        Raises:
            ValueError: If no text providers are registered.
        
        Example:
            ```python
            result = await kernel.generate_text(
                "Write a Python function to sort a list",
                temperature=0.3,
                max_tokens=500
            )
            print(result)
            ```
        """
        # Use registered tools if no tools are explicitly provided
        if tools is None:
            tools = self.tool_definitions
        
        # Use provided tool implementations or fall back to registered ones
        if tool_implementations is None:
            tool_implementations = self.tool_instances

        if not self._text_providers:
            raise ValueError("No text providers registered")
        
        for provider in self._text_providers:
            if isinstance(provider, ITextProvider):
                return await provider.generate_text(
                    prompt, system_message, context, temperature, max_tokens, 
                    top_p, frequency_penalty, presence_penalty, tools, tool_implementations
                )
            
        raise ValueError("No text providers registered")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text.
        
        Args:
            text: The text to generate embeddings for.
        
        Returns:
            List of float values representing the text embedding.
        
        Raises:
            RuntimeError: If no providers or embedding providers are registered.
        
        Example:
            ```python
            embedding = await kernel.generate_embedding("Hello, world!")
            print(f"Embedding dimension: {len(embedding)}")
            ```
        """
        if not self._embedding_providers:
            raise ValueError("No embedding providers registered")
        
        for provider in self._embedding_providers:
            if isinstance(provider, IEmbeddingProvider):
                return await provider.generate_embedding(text)
            
        raise ValueError("No embedding providers registered")