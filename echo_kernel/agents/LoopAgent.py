from echo_kernel.EchoAgent import EchoAgent
from echo_kernel.IEchoAgent import IEchoAgent

class LoopAgent(IEchoAgent):
    def __init__(self, name: str, agent: EchoAgent, max_steps: int = 3, stop_phrase: str = "Final version"):
        self.name = name
        self.agent = agent
        self.max_steps = max_steps
        self.stop_phrase = stop_phrase

    async def run(self, task: str) -> str:
        current_task = task
        for i in range(self.max_steps):
            print(f"[{self.name}] Step {i+1}:")
            result = await self.agent.run(current_task)
            print(result)

            if self.stop_phrase.lower() in result.lower():
                break

            current_task = f"Improve the previous output.\n\n{result}"
        return result

