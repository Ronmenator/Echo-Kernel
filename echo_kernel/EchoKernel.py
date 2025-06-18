from typing import List, Dict, Any, Callable, Optional, TypeVar, Type, cast
from echo_kernel.IEmbeddingProvider import IEmbeddingProvider
from echo_kernel.ITextProvider import ITextProvider
from echo_kernel.IEchoTool import IEchoTool

T = TypeVar('T')

class EchoKernel:
    
    def __init__(self):
        self.providers: List[any] = []
        self._tools: Dict[str, IEchoTool] = {}

    def register_provider(self, provider: any):
        """Register a provider service with the kernel."""
        self.providers.append(provider)

    def register_tool(self, tool: IEchoTool) -> None:
        """Register a tool with the kernel"""
        if not isinstance(tool, IEchoTool):
            raise TypeError("Tool must implement ITool protocol")
        
        self._tools[tool.name] = tool

    def get_service(self, service_type: Type[T]) -> Optional[T]:
        """Get a registered service of the specified type."""
        for provider in self.providers:
            if isinstance(provider, service_type):
                return cast(T, provider)
        return None

    @property
    def tool_definitions(self) -> List[Dict[str, Any]]:
        """Get all registered tool definitions"""
        return [tool.definition for tool in self._tools.values()]

    @property
    def tool_instances(self) -> Dict[str, Callable]:
        """Get all registered tool instances"""
        return {name: tool for name, tool in self._tools.items()}

    async def generate_text(self, prompt: str, system_message: str = "", context: Dict = None, temperature: float = 0.7, max_tokens: int = 1000, top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, tools : List = None, tool_implementations: Dict = None) -> str:
        # Use registered tools if no tools are explicitly provided
        if tools is None:
            tools = self.tool_definitions
        if tool_implementations is None:
            tool_implementations = self.tool_instances

        if not self.providers:
            raise RuntimeError("No provider services registered with the kernel")
        
        for provider in self.providers:
            if isinstance(provider, ITextProvider):
                return await provider.generate_text(prompt, system_message, context, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, tools, tool_implementations)
            
        raise RuntimeError("No text provider services registered with the kernel")

    async def generate_embedding(self, text: str) -> List[float]:
        if not self.providers:
            raise RuntimeError("No provider services registered with the kernel")
        
        for provider in self.providers:
            if isinstance(provider, IEmbeddingProvider):
                return await provider.generate_embedding(text)
            
        raise RuntimeError("No embedding provider services registered with the kernel")