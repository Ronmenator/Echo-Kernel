# Define the ITextProvider protocol
from typing import Dict, Protocol, runtime_checkable


@runtime_checkable
class ITextProvider(Protocol):
    async def generate_text(self, prompt: str, system_message: str = "", context: Dict = None, temperature: float = 0.7, max_tokens: int = 1000, top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0, tools = None) -> str:
        ...