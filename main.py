import asyncio
from echo_kernel import EchoKernel, AzureOpenAITextProvider, AzureOpenAIEmbeddingProvider, VectorMemoryProvider, ITextMemory
from echo_kernel.providers.QdrantStorageProvider import QdrantStorageProvider
from tools.CodeInterpreterTool import execute_python_code
from config import *

text_provider = AzureOpenAITextProvider(api_key=AZURE_OPENAI_API_KEY, api_base=AZURE_OPENAI_API_BASE, api_version=AZURE_OPENAI_API_VERSION, model=AZURE_OPENAI_TEXT_MODEL)
#embedding_provider = AzureOpenAIEmbeddingProvider(api_key=AZURE_OPENAI_API_KEY, api_base=AZURE_OPENAI_API_BASE, api_version=AZURE_OPENAI_API_VERSION, model=AZURE_OPENAI_EMBEDDING_MODEL)
#vector_memory_provider = VectorMemoryProvider(embedding_provider, QdrantStorageProvider(url=QDRANT_URL, collection_name=QDRANT_COLLECTION_NAME, api_key=QDRANT_API_KEY))

kernel = EchoKernel()

kernel.register_provider(text_provider)
#kernel.register_provider(embedding_provider)
#kernel.register_provider(vector_memory_provider)

kernel.register_tool(execute_python_code)

async def main():
    # Get the memory service using the new GetService pattern
    # memory_service = kernel.get_service(ITextMemory)
    # if memory_service:
        # Add some text to memory
    #    await memory_service.add_text("The weather in Austin is sunny today", {"source": "weather_report"})
        
        # Search for similar texts
    #    similar_texts = await memory_service.search_similar("What's the weather like?")
    #    print("Similar texts found:", similar_texts)
    
    # Generate text as before
    query = "Using the code interpreter tool, write a python script that prints 'Hello, World!'"
    result = await kernel.generate_text(query)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())