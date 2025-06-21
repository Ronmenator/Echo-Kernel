from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.IEchoAgent import IEchoAgent


class RouterAgent(IEchoAgent):
    def __init__(self, name: str, kernel: EchoKernel, agents: dict[str, IEchoAgent] = None, router_prompt: str = "Choose the best agent for this task"):
        self._name = name
        self.kernel = kernel
        self.agents = agents or {}
        self.router_prompt = router_prompt

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def specialists(self) -> dict[str, IEchoAgent]:
        return self.agents

    async def run(self, task: str) -> str:
        return await self.route_task(task)

    async def route_task(self, task: str) -> str:
        """Route a task to the appropriate agent."""
        if not self.agents:
            raise ValueError("No agents available for routing")

        decision_prompt = f"{self.router_prompt}\nTask: {task}\nRespond ONLY with the name of the best agent."
        agent_name = (await self.kernel.generate_text(decision_prompt)).strip()
        agent = self.agents.get(agent_name)
        
        # If agent not found, use first available agent as fallback
        if not agent:
            agent_name = list(self.agents.keys())[0]
            agent = self.agents[agent_name]
        
        return await agent.run(task)

    async def route_task_with_fallback(self, task: str, fallback_agent: IEchoAgent) -> str:
        """Route a task with a fallback agent."""
        try:
            return await self.route_task(task)
        except Exception:
            return await fallback_agent.run(task)
