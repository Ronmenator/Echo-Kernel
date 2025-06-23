import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from echo_kernel import EchoKernel, AzureOpenAITextProvider
from echo_kernel.EchoAgent import EchoAgent
from echo_kernel.agents.LoopAgent import LoopAgent
from echo_kernel.agents.TaskDecomposerAgent import TaskDecomposerAgent
from config import *

# Create text provider
text_provider = AzureOpenAITextProvider(
    api_key=AZURE_OPENAI_API_KEY, 
    api_base=AZURE_OPENAI_API_BASE, 
    api_version=AZURE_OPENAI_API_VERSION, 
    model=AZURE_OPENAI_TEXT_MODEL
)

async def run_with_logging_enabled():
    """Run agents with logging enabled (default behavior)."""
    print("=" * 60)
    print("RUNNING WITH AGENT LOGGING ENABLED")
    print("=" * 60)
    
    # Create kernel with logging enabled (default)
    kernel = EchoKernel(text_provider=text_provider, agent_logging_enabled=True)
    
    # Create agents
    executor_agent = EchoAgent("Executor", kernel, "You are a helpful assistant.")
    loop_agent = LoopAgent("LoopAgent", kernel, max_iterations=2)
    task_agent = TaskDecomposerAgent("TaskAgent", kernel, executor_agent)
    
    # Run a simple task
    result = await task_agent.run("Write a short poem about coding.")
    print("\nFinal Result:")
    print(result)

async def run_with_logging_disabled():
    """Run agents with logging disabled."""
    print("\n" + "=" * 60)
    print("RUNNING WITH AGENT LOGGING DISABLED")
    print("=" * 60)
    
    # Create kernel with logging disabled
    kernel = EchoKernel(text_provider=text_provider, agent_logging_enabled=False)
    
    # Create agents
    executor_agent = EchoAgent("Executor", kernel, "You are a helpful assistant.")
    loop_agent = LoopAgent("LoopAgent", kernel, max_iterations=2)
    task_agent = TaskDecomposerAgent("TaskAgent", kernel, executor_agent)
    
    # Run the same task
    result = await task_agent.run("Write a short poem about coding.")
    print("\nFinal Result:")
    print(result)

async def run_with_environment_variable():
    """Run agents using the AGENT_LOGGING_ENABLED environment variable."""
    print("\n" + "=" * 60)
    print("RUNNING WITH ENVIRONMENT VARIABLE CONTROL")
    print("=" * 60)
    
    # The kernel will automatically use the AGENT_LOGGING_ENABLED setting from config.py
    # which reads from the environment variable
    kernel = EchoKernel(text_provider=text_provider)
    
    # Create agents
    executor_agent = EchoAgent("Executor", kernel, "You are a helpful assistant.")
    loop_agent = LoopAgent("LoopAgent", kernel, max_iterations=2)
    task_agent = TaskDecomposerAgent("TaskAgent", kernel, executor_agent)
    
    # Run the same task
    result = await task_agent.run("Write a short poem about coding.")
    print("\nFinal Result:")
    print(result)

async def main():
    """Demonstrate different ways to control agent logging."""
    
    # Method 1: Explicitly enable logging
    await run_with_logging_enabled()
    
    # Method 2: Explicitly disable logging
    await run_with_logging_disabled()
    
    # Method 3: Use environment variable (if set)
    # You can set AGENT_LOGGING_ENABLED=False in your .env file or environment
    await run_with_environment_variable()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("To disable agent logging, you can:")
    print("1. Pass agent_logging_enabled=False to EchoKernel constructor")
    print("2. Set AGENT_LOGGING_ENABLED=False in your .env file")
    print("3. Set AGENT_LOGGING_ENABLED=False as an environment variable")
    print("\nWhen logging is disabled, agents will run silently without print statements.")

if __name__ == "__main__":
    asyncio.run(main()) 