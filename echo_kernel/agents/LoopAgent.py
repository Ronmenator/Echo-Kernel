from echo_kernel.EchoAgent import EchoAgent
from echo_kernel.IEchoAgent import IEchoAgent
from typing import Dict

class LoopAgent(IEchoAgent):
    def __init__(self, name: str, kernel, max_iterations: int = 3, stop_phrase: str = "Final version"):
        self._name = name
        self.kernel = kernel
        self.agent = EchoAgent(name, kernel)
        self.max_iterations = max_iterations
        self.max_steps = max_iterations  # For backward compatibility
        self.stop_phrase = stop_phrase
        self._iteration_count = 0

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def iteration_count(self) -> int:
        return self._iteration_count

    @iteration_count.setter
    def iteration_count(self, value: int) -> None:
        self._iteration_count = value

    async def run(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                 top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                 context: Dict = None, system_prompt: str = None) -> str:
        return await self.iterate(task, temperature, max_tokens, top_p, 
                                frequency_penalty, presence_penalty, context, system_prompt)

    async def iterate(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                     top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                     context: Dict = None, system_prompt: str = None, stop_condition=None) -> str:
        """Iterate on a task with optional stop condition."""
        current_task = task
        self._iteration_count = 0
        
        for i in range(self.max_iterations):
            self._iteration_count = i + 1
            print(f"[{self.name}] Step {i+1}:")
            result = await self.agent.run(current_task, temperature, max_tokens, top_p, 
                                        frequency_penalty, presence_penalty, context, system_prompt)
            print(result)

            # Check stop condition
            should_stop = False
            if callable(stop_condition):
                should_stop = stop_condition(result)
            elif isinstance(stop_condition, str):
                should_stop = stop_condition.lower() in result.lower()
            else:
                should_stop = self.stop_phrase.lower() in result.lower()

            if should_stop:
                break

            current_task = f"Improve the previous output.\n\n{result}"
        return result

    def reset(self) -> None:
        """Reset the iteration counter."""
        self._iteration_count = 0

