from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.IEchoAgent import IEchoAgent
from typing import Dict


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

    async def run(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                 top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                 context: Dict = None, system_prompt: str = None) -> str:
        return await self.route_task(task, temperature, max_tokens, top_p, 
                                   frequency_penalty, presence_penalty, context, system_prompt)

    async def route_task(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                        top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                        context: Dict = None, system_prompt: str = None) -> str:
        """Route a task to the appropriate agent."""
        if not self.agents:
            raise ValueError("No agents available for routing")

        decision_prompt = f"{self.router_prompt}\nTask: {task}\nRespond ONLY with the name of the best agent."
        agent_name = (await self.kernel.generate_text(decision_prompt, temperature=temperature, 
                                                     max_tokens=max_tokens, top_p=top_p, 
                                                     frequency_penalty=frequency_penalty, 
                                                     presence_penalty=presence_penalty, 
                                                     context=context, system_prompt=system_prompt)).strip()
        agent = self.agents.get(agent_name)
        
        # If agent not found, use first available agent as fallback
        if not agent:
            agent_name = list(self.agents.keys())[0]
            agent = self.agents[agent_name]
        
        return await agent.run(task, temperature, max_tokens, top_p, 
                             frequency_penalty, presence_penalty, context, system_prompt)

    async def route_task_with_fallback(self, task: str, fallback_agent: IEchoAgent, 
                                     temperature: float = 0.7, max_tokens: int = 1000, 
                                     top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                                     context: Dict = None, system_prompt: str = None) -> str:
        """Route a task with a fallback agent."""
        try:
            return await self.route_task(task, temperature, max_tokens, top_p, 
                                       frequency_penalty, presence_penalty, context, system_prompt)
        except Exception:
            return await fallback_agent.run(task, temperature, max_tokens, top_p, 
                                          frequency_penalty, presence_penalty, context, system_prompt)
