from echo_kernel.EchoAgent import EchoAgent
from echo_kernel.IEchoAgent import IEchoAgent
from typing import Dict, Optional

class CollaborativeAgent(IEchoAgent):
    """
    A collaborative agent that manages two sub-agents in a synchronous loop.
    
    This agent is useful for scenarios where two agents need to work together
    iteratively, such as an editor providing feedback to a writer who implements changes.
    The loop continues until one of the agents adds the stop_phrase to their response.
    
    Example:
        editor_agent = EchoAgent("Editor", kernel, "You are a strict editor providing feedback.")
        writer_agent = EchoAgent("Writer", kernel, "You are a writer who implements feedback.")
        collaborative = CollaborativeAgent("EditorWriter", kernel, editor_agent, writer_agent)
        result = await collaborative.run("Write a short story about a robot.")
    """
    
    def __init__(self, name: str, kernel, agent_a: IEchoAgent, agent_b: IEchoAgent, 
                 max_iterations: int = 10, stop_phrase: str = "Final version", 
                 agent_a_role: str = "Agent A", agent_b_role: str = "Agent B"):
        """
        Initialize the CollaborativeAgent.
        
        Args:
            name: Name of the collaborative agent
            kernel: EchoKernel instance
            agent_a: First sub-agent (e.g., editor)
            agent_b: Second sub-agent (e.g., writer)
            max_iterations: Maximum number of iterations before stopping
            stop_phrase: Phrase that indicates the collaboration should stop
            agent_a_role: Role description for agent A (used in prompts)
            agent_b_role: Role description for agent B (used in prompts)
        """
        self._name = name
        self.kernel = kernel
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.max_iterations = max_iterations
        self.stop_phrase = stop_phrase
        self.agent_a_role = agent_a_role
        self.agent_b_role = agent_b_role
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
        """Run the collaborative workflow."""
        return await self.collaborate(task, temperature, max_tokens, top_p, 
                                    frequency_penalty, presence_penalty, context, system_prompt)

    async def collaborate(self, task: str, temperature: float = 0.7, max_tokens: int = 1000, 
                         top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                         context: Dict = None, system_prompt: str = None) -> str:
        """
        Execute the collaborative workflow between the two agents.
        
        The workflow alternates between agent A and agent B until one adds the stop_phrase
        or the maximum iterations are reached.
        """
        current_task = task
        current_result = ""
        self._iteration_count = 0
        stop = False
        for i in range(self.max_iterations):
            self._iteration_count = i + 1
            
            # Agent A's turn (e.g., editor providing feedback)
            if self.kernel.agent_logging_enabled: print(f"[{self.name}] {self.agent_a_role} turn (iteration {i+1}):")
            
            agent_a_prompt = self._build_agent_a_prompt(current_task, current_result, i)
            agent_a_result = await self.agent_a.run(agent_a_prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, context, system_prompt)
            
            if self.kernel.agent_logging_enabled: print(f"[{self.agent_a.name}] {agent_a_result}")
            
            # Check if agent A wants to stop
            if self.stop_phrase.lower() in agent_a_result.lower():
                if self.kernel.agent_logging_enabled: print(f"[{self.name}] {self.agent_a_role} decided to stop.")
                stop = True
                break
            
            # Agent B's turn (e.g., writer implementing feedback)
            if self.kernel.agent_logging_enabled: print(f"[{self.name}] {self.agent_b_role} turn (iteration {i+1}):")
            
            agent_b_prompt = self._build_agent_b_prompt(current_task, agent_a_result, i)
            agent_b_result = await self.agent_b.run(agent_b_prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, context, system_prompt)
            
            if self.kernel.agent_logging_enabled: print(f"[{self.agent_b.name}] {agent_b_result}")
            
            # Check if agent B wants to stop
            if stop:
                if self.kernel.agent_logging_enabled: print(f"[{self.name}] {self.agent_b_role} decided to stop.")
                return agent_b_result
            
            # Update current result for next iteration
            current_result = agent_b_result
        
        # If we reach here, max iterations were reached
        if self.kernel.agent_logging_enabled: print(f"[{self.name}] Maximum iterations ({self.max_iterations}) reached.")
        
        return current_result

    def _build_agent_a_prompt(self, original_task: str, current_result: str, iteration: int) -> str:
        """Build the prompt for agent A (e.g., editor)."""
        if iteration == 0:
            # First iteration - agent A starts the process
            return f"Original task: {original_task}\n\nPlease start working on this task."
        else:
            # Subsequent iterations - agent A provides feedback
            return f"Original task: {original_task}\n\nCurrent result:\n{current_result}\n\nPlease review and provide feedback or improvements. If you're satisfied, end your response with '{self.stop_phrase}'."

    def _build_agent_b_prompt(self, original_task: str, agent_a_feedback: str, iteration: int) -> str:
        """Build the prompt for agent B (e.g., writer)."""
        if iteration == 0:
            # First iteration - agent B responds to agent A's initial work
            return f"Original task: {original_task}\n\n{self.agent_a_role}'s work:\n{agent_a_feedback}\n\nPlease continue or improve upon this work."
        else:
            # Subsequent iterations - agent B implements feedback
            return f"Original task: {original_task}\n\n{self.agent_a_role}'s feedback:\n{agent_a_feedback}\n\nPlease implement the feedback and improve the work. If you're satisfied with the result, end your response with '{self.stop_phrase}'."

    def reset(self) -> None:
        """Reset the iteration counter."""
        self._iteration_count = 0 