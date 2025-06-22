from typing_extensions import Protocol
from typing import Dict


class IEchoAgent(Protocol):
    @property
    def name(self) -> str: ...
    
    @name.setter
    def name(self, value: str) -> None: ...
    
    async def run(self, input: str, temperature: float = 0.7, max_tokens: int = 1000, 
                 top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, 
                 context: Dict = None, system_prompt: str = None) -> str: ...
