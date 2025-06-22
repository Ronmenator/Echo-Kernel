from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.ITextMemory import ITextMemory
from echo_kernel.IEchoAgent import IEchoAgent
from echo_kernel.EchoAgent import EchoAgent
from typing import Dict, Any, List


class MemoryAgent(IEchoAgent):
    def __init__(self, name: str, kernel: EchoKernel, memory_interface: ITextMemory = None, agent: IEchoAgent = None):
        self._name = name
        self.kernel = kernel
        self.memory = memory_interface or kernel.get_service(ITextMemory)
        self.agent = agent or EchoAgent(name, kernel)
        
        if not self.memory:
            raise ValueError("No memory provider available")

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def memory_provider(self) -> ITextMemory:
        return self.memory

    async def run(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                 top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                 context: Dict = None, system_prompt: str = None) -> str:
        return await self.process_with_memory(task, temperature, max_tokens, top_p, 
                                            frequency_penalty, presence_penalty, context, system_prompt)

    async def process_with_memory(self, message: str, temperature: float = 0.7, max_tokens: int = 1000, 
                                top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                                context: Dict = None, system_prompt: str = None) -> str:
        """Process a message with memory context."""
        # Search for similar past messages
        similar = await self.memory.search_similar(message, limit=10)
        
        # Build context from similar messages
        context_text = "\n".join([f"- {r.get('text', str(r))}" for r in similar]) if similar else ""
        
        # Add current message to memory
        await self.memory.add_text(message, {"timestamp": "now", "agent": self.name})
        
        # Process with context
        if context_text:
            full_prompt = f"Previous relevant context:\n{context_text}\n\nCurrent message: {message}"
        else:
            full_prompt = message
        
        return await self.agent.run(full_prompt, temperature, max_tokens, top_p, 
                                  frequency_penalty, presence_penalty, context, system_prompt)

    async def add_to_memory(self, text: str, metadata: Dict[str, Any] = None) -> None:
        """Add text to memory."""
        await self.memory.add_text(text, metadata or {})

    async def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """Search memory for similar content."""
        return await self.memory.search_similar(query)

    async def conversation_context(self, task: str) -> str:
        """Get conversation context for a task."""
        similar = await self.memory.search_similar(task)
        if similar:
            context = "\n".join([f"- {r.get('text', str(r))}" for r in similar])
            return f"Previous relevant conversations:\n{context}\n\nCurrent task: {task}"
        return task
