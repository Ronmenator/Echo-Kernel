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

    async def run(self, task: str) -> str:
        prompt = f"{self.persona}\n{task}" if self.persona else task
        return await self.kernel.generate_text(prompt)

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

