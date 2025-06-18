from typing import List
import openai
from ..IEmbeddingProvider import IEmbeddingProvider

class OpenAIImbeddingProvider(IEmbeddingProvider):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    async def generate_embedding(self, text: str) -> List[float]:
        response = await openai.Embedding.acreate(
            model=self.model,
            input=text
        )
        return response.data[0].embedding 