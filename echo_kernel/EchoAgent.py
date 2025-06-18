from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.IEchoAgent import IEchoAgent

class EchoAgent(IEchoAgent):
    def __init__(self, name: str, kernel: EchoKernel, persona: str = ""):
        self.name = name
        self.kernel = kernel
        self.persona = persona

    async def run(self, task: str) -> str:
        prompt = f"{self.persona}\n{task}" if self.persona else task
        return await self.kernel.generate_text(prompt)

