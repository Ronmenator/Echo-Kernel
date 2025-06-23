from typing import List, Dict
from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.IEchoAgent import IEchoAgent


class TaskDecomposerAgent(IEchoAgent):
    def __init__(self, name: str, kernel: EchoKernel, executor_agent: IEchoAgent):
        self._name = name
        self.kernel = kernel
        self.executor_agent = executor_agent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def executor(self) -> IEchoAgent:
        return self.executor_agent

    async def run(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                 top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                 context: Dict = None, system_prompt: str = None) -> str:
        return await self.coordinate_execution(task, temperature, max_tokens, top_p, 
                                             frequency_penalty, presence_penalty, context, system_prompt)

    async def decompose_task(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                           top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                           context: Dict = None, system_prompt: str = None) -> List[str]:
        """Decompose a task into subtasks."""
        plan_prompt = (
            f"You are a planning agent.\n"
            f"Decompose the following task into 3–5 concrete, sequential subtasks:\n\n"
            f"Task: {task}\n\n"
            f"Return the list of subtasks as plain numbered steps."
        )
        plan = await self.kernel.generate_text(plan_prompt, temperature=temperature, max_tokens=max_tokens,
                                             top_p=top_p, frequency_penalty=frequency_penalty, 
                                             presence_penalty=presence_penalty, context=context, 
                                             system_prompt=system_prompt)
        return self._parse_subtasks(plan)

    async def execute_task(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                          top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                          context: Dict = None, system_prompt: str = None) -> str:
        """Execute a single task."""
        return await self.executor_agent.run(task, temperature, max_tokens, top_p, 
                                           frequency_penalty, presence_penalty, context, system_prompt)

    async def coordinate_execution(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                                 top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                                 context: Dict = None, system_prompt: str = None) -> str:
        """Coordinate the execution of a decomposed task."""
        # Step 1: Generate a list of subtasks
        plan_prompt = (
            f"You are a planning agent.\n"
            f"Decompose the following task into 3–5 concrete, sequential subtasks:\n\n"
            f"Task: {task}\n\n"
            f"Return the list of subtasks as plain numbered steps."
        )
        plan = await self.kernel.generate_text(plan_prompt, temperature=temperature, max_tokens=max_tokens,
                                             top_p=top_p, frequency_penalty=frequency_penalty, 
                                             presence_penalty=presence_penalty, context=context, 
                                             system_prompt=system_prompt)

        if self.kernel.agent_logging_enabled:
            print(f"[{self.name}] Plan generated:\n{plan}\n")

        # Step 2: Parse the subtasks
        subtasks = self._parse_subtasks(plan)

        # Step 3: Execute each subtask
        results = []
        for i, subtask in enumerate(subtasks):
            if self.kernel.agent_logging_enabled:
                print(f"[{self.name}] Executing Subtask {i+1}: {subtask}")
            result = await self.executor_agent.run(subtask, temperature, max_tokens, top_p, 
                                                 frequency_penalty, presence_penalty, context, system_prompt)
            results.append(f"Subtask {i+1} Result:\n{result}\n")

        return "\n".join(results)

    def _parse_subtasks(self, plan_text: str) -> List[str]:
        lines = plan_text.strip().splitlines()
        subtasks = []
        for line in lines:
            if '.' in line:
                parts = line.split('.', 1)
                subtasks.append(parts[1].strip())
            elif '-' in line:
                parts = line.split('-', 1)
                subtasks.append(parts[1].strip())
        return [s for s in subtasks if s]