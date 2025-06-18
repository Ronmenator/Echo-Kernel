from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.IEchoAgent import IEchoAgent


class RouterAgent(IEchoAgent):
    def __init__(self, name: str, agents: dict[str, IEchoAgent], router_prompt: str, kernel: EchoKernel):
        self.name = name
        self.agents = agents
        self.router_prompt = router_prompt
        self.kernel = kernel

    async def run(self, task: str) -> str:
        decision_prompt = f"{self.router_prompt}\nTask: {task}\nRespond ONLY with the name of the best agent."
        agent_name = (await self.kernel.generate_text(decision_prompt)).strip()
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"No agent found with name: {agent_name}")
        return await agent.run(task)
