import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from echo_kernel import EchoKernel, AzureOpenAITextProvider, AzureOpenAIEmbeddingProvider, VectorMemoryProvider, ITextMemory
from echo_kernel.EchoAgent import EchoAgent
from echo_kernel.agents.LoopAgent import LoopAgent
from echo_kernel.agents.MemoryAgent import MemoryAgent
from echo_kernel.agents.SpecialistRouterAgent import SpecialistRouterAgent
from echo_kernel.agents.TaskDecomposerAgent import TaskDecomposerAgent
from echo_kernel.providers.QdrantStorageProvider import QdrantStorageProvider
from tools.CodeInterpreterTool import execute_python_code
from config import *

# Set up providers
text_provider = AzureOpenAITextProvider(
    api_key=AZURE_OPENAI_API_KEY, 
    api_base=AZURE_OPENAI_API_BASE, 
    api_version=AZURE_OPENAI_API_VERSION, 
    model=AZURE_OPENAI_TEXT_MODEL
)

# Uncomment these lines if you have embedding and Qdrant configured
# embedding_provider = AzureOpenAIEmbeddingProvider(
#     api_key=AZURE_OPENAI_API_KEY, 
#     api_base=AZURE_OPENAI_API_BASE, 
#     api_version=AZURE_OPENAI_API_VERSION, 
#     model=AZURE_OPENAI_EMBEDDING_MODEL
# )
# storage_provider = QdrantStorageProvider(
#     url=QDRANT_URL, 
#     collection_name=QDRANT_COLLECTION_NAME, 
#     api_key=QDRANT_API_KEY
# )
# memory_provider = VectorMemoryProvider(embedding_provider, storage_provider)

kernel = EchoKernel()

kernel.register_provider(text_provider)
# Uncomment if you have memory configured
# kernel.register_provider(embedding_provider)
# kernel.register_provider(memory_provider)

kernel.register_tool(execute_python_code)

async def main():
    # Basic agents
    code_agent = EchoAgent("CodeAgent", kernel, "You write correct Python code.")
    web_agent = EchoAgent("WebAgent", kernel, "You search and summarize web results.")
    doc_agent = EchoAgent("DocAgent", kernel, "You create well-written technical documents.")

    # Specialist router
    specialist_router = SpecialistRouterAgent("SkillRouter", kernel, {
        "CodeAgent": code_agent,
        "WebAgent": web_agent,
        "DocAgent": doc_agent,
    })

    # Memory-enhanced agent (if memory service is available)
    memory_service = kernel.get_service(ITextMemory)
    if memory_service:
        print("Using memory-enhanced agent")
        executor_agent = MemoryAgent("MemoryAgent", kernel, memory_service, specialist_router)
    else:
        print("Using specialist router directly (no memory service available)")
        executor_agent = specialist_router

    # Looping executor with retries
    executor = LoopAgent("LoopingExecutor", executor_agent, max_steps=3)

    # Task planner (uses decomposer)
    planner = TaskDecomposerAgent("TaskPlanner", kernel, executor)

    # Run high-level goal
    result = await planner.run("Build a data pipeline that scrapes articles, summarizes them, and outputs a report.")
    print(result)

if __name__ == "__main__":
    asyncio.run(main()) 