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

from typing import List, Dict, Any, Callable, Optional, TypeVar, Type, cast
from echo_kernel.IEmbeddingProvider import IEmbeddingProvider
from echo_kernel.ITextProvider import ITextProvider
from echo_kernel.IEchoTool import IEchoTool

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
        """Initialize a new EchoKernel instance."""
        self.providers: List[any] = []
        self._tools: Dict[str, IEchoTool] = {}

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
        self.providers.append(provider)

    def register_tool(self, tool: IEchoTool) -> None:
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
        if not isinstance(tool, IEchoTool):
            raise TypeError("Tool must implement ITool protocol")
        
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
        for provider in self.providers:
            if isinstance(provider, service_type):
                return cast(T, provider)
        return None

    @property
    def tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get all registered tool definitions.
        
        Returns:
            List of tool definition dictionaries that can be passed to AI providers.
        """
        return [tool.definition for tool in self._tools.values()]

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
        tools: List = None, 
        tool_implementations: Dict = None
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
            tool_implementations: Optional dictionary of tool implementations.
        
        Returns:
            Generated text string.
        
        Raises:
            RuntimeError: If no providers or text providers are registered.
        
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
        if tool_implementations is None:
            tool_implementations = self.tool_instances

        if not self.providers:
            raise RuntimeError("No provider services registered with the kernel")
        
        for provider in self.providers:
            if isinstance(provider, ITextProvider):
                return await provider.generate_text(
                    prompt, system_message, context, temperature, max_tokens, 
                    top_p, frequency_penalty, presence_penalty, tools, tool_implementations
                )
            
        raise RuntimeError("No text provider services registered with the kernel")

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
        if not self.providers:
            raise RuntimeError("No provider services registered with the kernel")
        
        for provider in self.providers:
            if isinstance(provider, IEmbeddingProvider):
                return await provider.generate_embedding(text)
            
        raise RuntimeError("No embedding provider services registered with the kernel")