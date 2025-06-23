import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from echo_kernel import EchoKernel, AzureOpenAITextProvider
from echo_kernel.EchoAgent import EchoAgent
from echo_kernel.agents.CollaborativeAgent import CollaborativeAgent
from config import *

# Create text provider
text_provider = AzureOpenAITextProvider(
    api_key=AZURE_OPENAI_API_KEY, 
    api_base=AZURE_OPENAI_API_BASE, 
    api_version=AZURE_OPENAI_API_VERSION, 
    model=AZURE_OPENAI_TEXT_MODEL
)

async def editor_writer_collaboration():
    """Demonstrate editor-writer collaboration using CollaborativeAgent."""
    print("=" * 60)
    print("EDITOR-WRITER COLLABORATION EXAMPLE")
    print("=" * 60)
    
    # Create kernel
    kernel = EchoKernel(text_provider=text_provider, agent_logging_enabled=True)
    
    # Create specialized agents
    editor_agent = EchoAgent(
        "Editor", 
        kernel, 
        "You are a strict but fair editor. You provide constructive feedback on writing, "
        "focusing on clarity, structure, grammar, and style. Be specific about what needs "
        "improvement and why. If you're satisfied with the work, end your response with 'Final version'."
    )
    
    writer_agent = EchoAgent(
        "Writer", 
        kernel, 
        "You are a creative writer who takes feedback well and implements suggestions. "
        "You write engaging, well-structured content. When you receive feedback, you "
        "carefully consider it and make improvements. If you're satisfied with your work, "
        "end your response with 'Final version'."
    )
    
    # Create collaborative agent
    collaborative = CollaborativeAgent(
        name="EditorWriter",
        kernel=kernel,
        agent_a=editor_agent,
        agent_b=writer_agent,
        max_iterations=5,
        stop_phrase="Final version",
        agent_a_role="Editor",
        agent_b_role="Writer"
    )
    
    # Run the collaboration
    task = "Write a short story (200-300 words) about a robot who discovers emotions for the first time."
    print(f"\nTask: {task}")
    print("\nStarting collaboration...\n")
    
    result = await collaborative.run(task)
    
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(result)
    print(f"\nCollaboration completed in {collaborative.iteration_count} iterations.")

async def code_review_collaboration():
    """Demonstrate code reviewer-developer collaboration."""
    print("\n" + "=" * 60)
    print("CODE REVIEWER-DEVELOPER COLLABORATION EXAMPLE")
    print("=" * 60)
    
    # Create kernel
    kernel = EchoKernel(text_provider=text_provider, agent_logging_enabled=True)
    
    # Create specialized agents
    reviewer_agent = EchoAgent(
        "CodeReviewer", 
        kernel, 
        "You are a senior software engineer who reviews code. You focus on code quality, "
        "best practices, performance, security, and maintainability. Provide specific, "
        "actionable feedback. If the code meets your standards, end with 'Final version'."
    )
    
    developer_agent = EchoAgent(
        "Developer", 
        kernel, 
        "You are a skilled developer who writes clean, efficient code. You take code "
        "review feedback seriously and implement improvements. Write well-documented, "
        "maintainable code. If you're satisfied with your implementation, end with 'Final version'."
    )
    
    # Create collaborative agent
    collaborative = CollaborativeAgent(
        name="CodeReview",
        kernel=kernel,
        agent_a=reviewer_agent,
        agent_b=developer_agent,
        max_iterations=4,
        stop_phrase="Final version",
        agent_a_role="Code Reviewer",
        agent_b_role="Developer"
    )
    
    # Run the collaboration
    task = "Write a Python function that efficiently finds the longest common subsequence between two strings."
    print(f"\nTask: {task}")
    print("\nStarting code review collaboration...\n")
    
    result = await collaborative.run(task)
    
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(result)
    print(f"\nCode review completed in {collaborative.iteration_count} iterations.")

async def silent_collaboration():
    """Demonstrate collaboration with logging disabled."""
    print("\n" + "=" * 60)
    print("SILENT COLLABORATION (LOGGING DISABLED)")
    print("=" * 60)
    
    # Create kernel with logging disabled
    kernel = EchoKernel(text_provider=text_provider, agent_logging_enabled=False)
    
    # Create specialized agents
    planner_agent = EchoAgent(
        "Planner", 
        kernel, 
        "You are a strategic planner. You analyze problems and provide structured plans. "
        "Be thorough and consider all aspects. If your plan is complete, end with 'Final version'."
    )
    
    executor_agent = EchoAgent(
        "Executor", 
        kernel, 
        "You are an implementation specialist. You take plans and execute them step by step. "
        "Be detailed and thorough in your execution. If you're satisfied, end with 'Final version'."
    )
    
    # Create collaborative agent
    collaborative = CollaborativeAgent(
        name="SilentCollaboration",
        kernel=kernel,
        agent_a=planner_agent,
        agent_b=executor_agent,
        max_iterations=3,
        stop_phrase="Final version",
        agent_a_role="Planner",
        agent_b_role="Executor"
    )
    
    # Run the collaboration
    task = "Create a marketing strategy for a new eco-friendly water bottle."
    print(f"\nTask: {task}")
    print("\nStarting silent collaboration (no progress messages)...\n")
    
    result = await collaborative.run(task)
    
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(result)
    print(f"\nSilent collaboration completed in {collaborative.iteration_count} iterations.")

async def main():
    """Run all collaboration examples."""
    
    # Example 1: Editor-Writer collaboration
    await editor_writer_collaboration()
    
    # Example 2: Code Reviewer-Developer collaboration
    await code_review_collaboration()
    
    # Example 3: Silent collaboration (logging disabled)
    await silent_collaboration()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("The CollaborativeAgent enables two agents to work together iteratively:")
    print("• Agent A provides feedback/input")
    print("• Agent B implements/responds to the feedback")
    print("• The loop continues until one agent adds the stop phrase")
    print("• Perfect for editor-writer, reviewer-developer, or any collaborative workflow")
    print("• Supports logging control for production use")

if __name__ == "__main__":
    asyncio.run(main()) 