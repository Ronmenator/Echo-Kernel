# Define the IEmbeddingProvider protocol
from typing import List, Protocol, runtime_checkable


@runtime_checkable
class IEmbeddingProvider(Protocol):
    async def generate_embedding(self, text: str) -> List[float]:
        ...