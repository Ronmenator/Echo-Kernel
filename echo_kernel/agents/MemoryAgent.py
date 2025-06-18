from echo_kernel import EchoKernel, ITextMemory
from echo_kernel.IEchoAgent import IEchoAgent


class MemoryAgent:
    def __init__(self, name: str, kernel: EchoKernel, memory_interface: ITextMemory, agent: IEchoAgent):
        self.name = name
        self.kernel = kernel
        self.memory = memory_interface
        self.agent = agent

    async def run(self, task: str) -> str:
        similar = await self.memory.search_similar(task)
        context = "\n".join([f"- {r.text}" for r in similar]) if similar else ""

        contextual_prompt = f"Use the following prior context if useful:\n{context}\n\nNow answer:\n{task}"
        result = await self.agent.run(contextual_prompt)

        await self.memory.add_text(result, {"source": self.name, "task": task})
        return result
