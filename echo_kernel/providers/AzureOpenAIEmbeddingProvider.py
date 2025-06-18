from typing import List
from openai import AzureOpenAI
from echo_kernel.IEmbeddingProvider import IEmbeddingProvider

class AzureOpenAIEmbeddingProvider(IEmbeddingProvider):
    def __init__(self, api_key: str, api_base: str, api_version: str, model: str):
        self.client = AzureOpenAI(api_key=api_key, azure_endpoint=api_base, api_version=api_version)
        self.model = model

    async def generate_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding