from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.IEchoAgent import IEchoAgent
from typing import Dict


class SpecialistRouterAgent(IEchoAgent):
    def __init__(self, name: str, kernel: EchoKernel, agents: dict[str, IEchoAgent] = None, router_prompt: str = "", max_retries: int = 3):
        self._name = name
        self.kernel = kernel
        self.agents = agents or {}
        self.router_prompt = router_prompt or (
            "Given a subtask, choose the most appropriate specialist agent to handle it.\n"
            f"Available agents: {', '.join(self.agents.keys())}\n"
            "Respond with the name only."
        )
        self.max_retries = max_retries

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
        return await self.route_with_validation(task, temperature, max_tokens, top_p, 
                                              frequency_penalty, presence_penalty, context, system_prompt)

    async def route_with_validation(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                                  top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                                  context: Dict = None, system_prompt: str = None, validator=None) -> str:
        """Route a task with validation of agent selection."""
        routing_prompt = f"{self.router_prompt}\nSubtask: {task}"

        attempts = 0
        while attempts < self.max_retries:
            # Get routing decision
            agent_name = (await self.kernel.generate_text(routing_prompt, temperature=temperature, 
                                                         max_tokens=max_tokens, top_p=top_p, 
                                                         frequency_penalty=frequency_penalty, 
                                                         presence_penalty=presence_penalty, 
                                                         context=context, system_prompt=system_prompt)).strip()
            
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                print(f"[{self.name}] Routing to agent: {agent_name}")
                
                # Execute the task
                result = await agent.run(task, temperature, max_tokens, top_p, 
                                       frequency_penalty, presence_penalty, context, system_prompt)
                
                # If no validator, return result immediately
                if validator is None:
                    print(f"[DEBUG] No validator provided, returning result")
                    return result
                else:
                    print(f"[DEBUG] Validator provided, calling validator")
                    # Validate result
                    if validator(result):
                        print(f"[DEBUG] Validation passed")
                        return result
                    else:
                        print(f"[DEBUG] Validation failed, retrying...")
                        # Validation failed, try again
                        routing_prompt = f"Previous result failed validation. Please choose a different agent from: {', '.join(self.agents.keys())}\nSubtask: {task}"
            else:
                print(f"[DEBUG] Invalid agent name: {agent_name}")
                # Invalid agent name, try again
                routing_prompt = f"The previous agent name was invalid. Please choose from the following list: {', '.join(self.agents.keys())}\nSubtask: {task}"
            attempts += 1

        # If we get here, all retries failed
        raise ValueError(f"Failed to route task after {self.max_retries} attempts")

    async def route_with_retries(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                               top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                               context: Dict = None, system_prompt: str = None) -> str:
        """Route a task with retry logic."""
        return await self.route_with_validation(task, temperature, max_tokens, top_p, 
                                              frequency_penalty, presence_penalty, context, system_prompt)
