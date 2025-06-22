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

from typing import List, Dict, Any, Callable, Optional, TypeVar, Type, cast, Protocol, runtime_checkable, Union
from echo_kernel.IEmbeddingProvider import IEmbeddingProvider
from echo_kernel.ITextProvider import ITextProvider
from echo_kernel.ITextMemory import ITextMemory
from echo_kernel.IEchoTool import IEchoTool
from echo_kernel.EchoTool import EchoTool
from echo_kernel.IStorageProvider import IStorageProvider
import asyncio
import inspect
import functools
from functools import partial

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
    
    def __init__(self, text_provider: Optional[ITextProvider] = None, embedding_provider: Optional[IEmbeddingProvider] = None, storage_provider: Optional[IStorageProvider] = None, tools: Optional[List[EchoTool]] = None):
        """Initialize the EchoKernel."""
        self._text_providers: List[ITextProvider] = []
        self._embedding_providers: List[IEmbeddingProvider] = []
        self._memory_providers: List[ITextMemory] = []
        self._storage_providers: List[IStorageProvider] = []
        self._tools: dict[str, EchoTool] = {}
        if text_provider:
            self._text_providers.append(text_provider)
        if embedding_provider:
            self._embedding_providers.append(embedding_provider)
        if storage_provider:
            self._storage_providers.append(storage_provider)
        if tools:
            for tool in tools:
                self.register_tool(tool)

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
    def tools(self) -> List[EchoTool]:
        return list(self._tools.values())

    @property
    def storage_provider(self) -> Optional[IStorageProvider]:
        """Get the first registered storage provider."""
        return self._storage_providers[0] if self._storage_providers else None

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

    def register_tool(self, tool: Union[EchoTool, Callable]):
        """Register a tool with the kernel. If a tool with the same name already exists, it will be updated."""
        if isinstance(tool, EchoTool):
            self._tools[tool.name] = tool
        elif callable(tool):
            # Handle decorated functions from EchoTool decorator
            if hasattr(tool, '_echo_tool_metadata'):
                # Create EchoTool instance from decorated function
                metadata = tool._echo_tool_metadata
                echo_tool = EchoTool(
                    name=metadata.name,
                    func=tool,
                    description=metadata.description,
                    parameters=metadata.parameters
                )
                self._tools[echo_tool.name] = echo_tool
            else:
                # Create EchoTool instance from regular function
                echo_tool = EchoTool(
                    name=tool.__name__,
                    func=tool,
                    description=tool.__doc__ or "",
                    parameters=None
                )
                self._tools[echo_tool.name] = echo_tool
        else:
            raise ValueError("Tool must be an EchoTool instance or a callable function")

    def get_tool(self, tool_name: str) -> Optional[EchoTool]:
        return self._tools.get(tool_name)

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

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get descriptions of all registered tools."""
        return [tool.to_dict() for tool in self.tools]

    async def execute_tool(self, tool: Union[EchoTool, str], **kwargs) -> Any:
        """Execute a registered tool."""
        if isinstance(tool, str):
            tool_to_run = self._tools.get(tool)
            if not tool_to_run:
                raise ValueError(f"Tool '{tool}' not found")
        else:
            tool_to_run = tool

        if inspect.iscoroutinefunction(tool_to_run.func):
            return await tool_to_run.func(**kwargs)
        else:
            loop = asyncio.get_running_loop()
            func = partial(tool_to_run.func, **kwargs)
            return await loop.run_in_executor(None, func)

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
                    return await self.generate_text(prompt, tools=self.get_tool_definitions(), **kwargs)
        
        raise ValueError("No text providers registered")

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, 
                          temperature: float = 0.7, max_tokens: int = 1000, top_p: float = 1, 
                          frequency_penalty: float = 0, presence_penalty: float = 0, context: Dict = None) -> str:
        """
        Generate text using registered text providers.
        
        This is the main method for text generation. It automatically uses
        registered tools and can work with any registered text provider.
        
        Args:
            prompt: The main prompt for text generation.
            system_prompt: Optional system message to set context.
            tools: Optional list of tool definitions to pass to the provider.
            temperature: Controls randomness in the response (0.0 to 2.0).
            max_tokens: Maximum number of tokens to generate.
            top_p: Controls diversity via nucleus sampling (0.0 to 1.0).
            frequency_penalty: Reduces repetition of frequent tokens (-2.0 to 2.0).
            presence_penalty: Reduces repetition of any tokens (-2.0 to 2.0).
            context: Optional context dictionary for the generation.
        
        Returns:
            Generated text string.
        
        Raises:
            ValueError: If no text providers are registered.
        
        Example:
            ```python
            result = await kernel.generate_text(
                "Write a Python function to sort a list",
                system_prompt="You are a helpful assistant.",
                temperature=0.8,
                max_tokens=500
            )
            print(result)
            ```
        """
        if not self._text_providers:
            raise ValueError("No text providers registered")
        
        # Use provided tools or get from registered tools
        tools_to_use = tools if tools is not None else self.get_tool_definitions()
        
        for provider in self._text_providers:
            if isinstance(provider, ITextProvider):
                return await provider.generate_text(
                    prompt, 
                    system_message=system_prompt or "", 
                    tools=tools_to_use,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    context=context
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