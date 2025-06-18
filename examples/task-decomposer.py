import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from echo_kernel import EchoKernel, AzureOpenAITextProvider
from echo_kernel.EchoAgent import EchoAgent
from echo_kernel.agents.TaskDecomposerAgent import TaskDecomposerAgent
from tools.CodeInterpreterTool import execute_python_code
from config import *

text_provider = AzureOpenAITextProvider(api_key=AZURE_OPENAI_API_KEY, api_base=AZURE_OPENAI_API_BASE, api_version=AZURE_OPENAI_API_VERSION, model=AZURE_OPENAI_TEXT_MODEL)

kernel = EchoKernel()

kernel.register_provider(text_provider)
kernel.register_tool(execute_python_code)

async def main():
    # Create basic worker agent
    executor = EchoAgent("PythonWorker", kernel, persona="You are a helpful Python expert.")

    # Create task-decomposing coordinator
    planner = TaskDecomposerAgent("Planner", kernel, executor)

    # Run high-level task
    task = "Create a weather notification system that fetches data and alerts users if it's raining"
    result = await planner.run(task)
    print("\n[Final Output]\n", result)

if __name__ == "__main__":
    asyncio.run(main())