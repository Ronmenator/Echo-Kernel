from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.IEchoAgent import IEchoAgent
from echo_kernel.IEchoTool import IEchoTool
from echo_kernel.Tool import EchoTool
from typing import List, Dict, Any, Callable

class EchoAgent(IEchoAgent):
    def __init__(self, name: str, kernel: EchoKernel, persona: str = ""):
        self._name = name
        self.kernel = kernel
        self.persona = persona
        self._tools: List[IEchoTool] = []

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def tools(self) -> List[IEchoTool]:
        return self._tools

    async def run(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                 top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                 context: Dict = None, system_prompt: str = None) -> str:
        """
        Run the agent with the given task and generation parameters.
        
        Args:
            task: The task to execute.
            temperature: Controls randomness in the response (0.0 to 2.0).
            max_tokens: Maximum number of tokens to generate.
            top_p: Controls diversity via nucleus sampling (0.0 to 1.0).
            frequency_penalty: Reduces repetition of frequent tokens (-2.0 to 2.0).
            presence_penalty: Reduces repetition of any tokens (-2.0 to 2.0).
            context: Optional context dictionary for the generation.
            system_prompt: Optional system message to override the agent's persona.
        
        Returns:
            Generated text response.
        """
        prompt = f"{self.persona}\n{task}" if self.persona else task
        return await self.kernel.generate_text(
            prompt, 
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            context=context
        )

    def add_tool(self, tool: Callable) -> None:
        """Add a tool to this agent."""
        # If the tool is not already decorated, decorate it
        if not hasattr(tool, 'name') or not hasattr(tool, 'definition'):
            tool = EchoTool(description=f"Tool: {tool.__name__}")(tool)
        self._tools.append(tool)
        self.kernel.register_tool(tool)

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process a message with optional context."""
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt = f"{context_str}\n\n{message}"
        else:
            full_prompt = message
        
        return await self.run(full_prompt)

    async def process_message_with_tools(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process a message with tools enabled."""
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt = f"{context_str}\n\n{message}"
        else:
            full_prompt = message
        
        return await self.kernel.generate_text_with_tools(full_prompt)

