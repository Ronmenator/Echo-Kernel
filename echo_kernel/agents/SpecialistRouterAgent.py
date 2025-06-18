from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.IEchoAgent import IEchoAgent


class SpecialistRouterAgent(IEchoAgent):
    def __init__(self, name: str, kernel: EchoKernel, agents: dict[str, IEchoAgent], router_prompt: str = ""):
        self.name = name
        self.kernel = kernel
        self.agents = agents
        self.router_prompt = router_prompt or (
            "Given a subtask, choose the most appropriate specialist agent to handle it.\n"
            f"Available agents: {', '.join(agents.keys())}\n"
            "Respond with the name only."
        )

    async def run(self, task: str) -> str:
        routing_prompt = f"{self.router_prompt}\nSubtask: {task}"

        for _ in range(3):
            agent_name = (await self.kernel.generate_text(routing_prompt)).strip()
            if agent_name in self.agents:
                break
            routing_prompt = f"The previous agent name was invalid. Please choose from the following list: {', '.join(self.agents.keys())}\nSubtask: {task}"

        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"No agent found for: {agent_name}")

        print(f"[{self.name}] Routing to agent: {agent_name}")
        return await agent.run(task)
