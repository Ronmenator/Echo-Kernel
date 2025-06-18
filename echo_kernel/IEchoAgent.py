from typing_extensions import Protocol


class IEchoAgent(Protocol):
    @property
    def name(self) -> str: ...
    
    @name.setter
    def name(self, value: str) -> None: ...
    
    async def run(self, input: str) -> str: ...
