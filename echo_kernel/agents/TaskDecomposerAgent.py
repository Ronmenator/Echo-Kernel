from typing import List
from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.IEchoAgent import IEchoAgent


class TaskDecomposerAgent(IEchoAgent):
    def __init__(self, name: str, kernel: EchoKernel, executor_agent: IEchoAgent):
        self.name = name
        self.kernel = kernel
        self.executor_agent = executor_agent

    async def run(self, task: str) -> str:
        # Step 1: Generate a list of subtasks
        plan_prompt = (
            f"You are a planning agent.\n"
            f"Decompose the following task into 3–5 concrete, sequential subtasks:\n\n"
            f"Task: {task}\n\n"
            f"Return the list of subtasks as plain numbered steps."
        )
        plan = await self.kernel.generate_text(plan_prompt)

        print(f"[{self.name}] Plan generated:\n{plan}\n")

        # Step 2: Parse the subtasks
        subtasks = self._parse_subtasks(plan)

        # Step 3: Execute each subtask
        results = []
        for i, subtask in enumerate(subtasks):
            print(f"[{self.name}] Executing Subtask {i+1}: {subtask}")
            result = await self.executor_agent.run(subtask)
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