"""
Unit tests for EchoKernel agents.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

from echo_kernel.EchoKernel import EchoKernel
from echo_kernel.EchoAgent import EchoAgent
from echo_kernel.agents.TaskDecomposerAgent import TaskDecomposerAgent
from echo_kernel.agents.LoopAgent import LoopAgent
from echo_kernel.agents.RouterAgent import RouterAgent
from echo_kernel.agents.SpecialistRouterAgent import SpecialistRouterAgent
from echo_kernel.agents.MemoryAgent import MemoryAgent


class TestEchoAgent:
    """Test cases for EchoAgent class."""

    @pytest.mark.unit
    def test_echo_agent_initialization(self, echo_kernel):
        """Test EchoAgent initialization."""
        agent = EchoAgent("TestAgent", echo_kernel, persona="You are a helpful assistant.")
        
        assert agent.name == "TestAgent"
        assert agent.kernel == echo_kernel
        assert agent.persona == "You are a helpful assistant."
        assert agent.tools == []

    @pytest.mark.unit
    def test_echo_agent_add_tool(self, echo_kernel):
        """Test adding tools to EchoAgent."""
        agent = EchoAgent("TestAgent", echo_kernel)
        
        def test_tool(text: str) -> str:
            return f"Tool: {text}"
        
        agent.add_tool(test_tool)
        
        assert len(agent.tools) == 1
        assert any(t.name == test_tool.__name__ for t in agent.tools)

    @pytest.mark.asyncio
    async def test_echo_agent_process_message(self, echo_kernel, mock_text_provider):
        """Test EchoAgent message processing."""
        echo_kernel.register_provider(mock_text_provider)
        agent = EchoAgent("TestAgent", echo_kernel, persona="You are helpful.")
        
        result = await agent.process_message("Hello")
        
        assert result == "Mock response"
        mock_text_provider.generate_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_echo_agent_process_message_with_tools(self, echo_kernel, mock_text_provider):
        """Test EchoAgent message processing with tools."""
        echo_kernel.register_provider(mock_text_provider)
        agent = EchoAgent("TestAgent", echo_kernel)
        
        def test_tool(text: str) -> str:
            return f"Tool: {text}"
        
        agent.add_tool(test_tool)
        
        result = await agent.process_message_with_tools("Use the tool")
        
        assert result == "Mock tool response"
        mock_text_provider.generate_text_with_tools.assert_called_once()


class TestTaskDecomposerAgent:
    """Test cases for TaskDecomposerAgent class."""

    @pytest.mark.unit
    def test_task_decomposer_initialization(self, echo_kernel):
        """Test TaskDecomposerAgent initialization."""
        executor = EchoAgent("Executor", echo_kernel)
        decomposer = TaskDecomposerAgent("Decomposer", echo_kernel, executor)
        
        assert decomposer.name == "Decomposer"
        assert decomposer.kernel == echo_kernel
        assert decomposer.executor == executor

    @pytest.mark.asyncio
    async def test_task_decomposer_decompose_task(self, echo_kernel, mock_text_provider):
        """Test task decomposition."""
        echo_kernel.register_provider(mock_text_provider)
        executor = EchoAgent("Executor", echo_kernel)
        decomposer = TaskDecomposerAgent("Decomposer", echo_kernel, executor)
        
        # Mock the response to simulate task decomposition
        mock_text_provider.generate_text.return_value = "1. Step one\n2. Step two\n3. Step three"
        
        subtasks = await decomposer.decompose_task("Complex task")
        
        assert isinstance(subtasks, list)
        assert len(subtasks) > 0
        mock_text_provider.generate_text.assert_called()

    @pytest.mark.asyncio
    async def test_task_decomposer_execute_task(self, echo_kernel, mock_text_provider):
        """Test task execution."""
        echo_kernel.register_provider(mock_text_provider)
        executor = EchoAgent("Executor", echo_kernel)
        decomposer = TaskDecomposerAgent("Decomposer", echo_kernel, executor)
        
        result = await decomposer.execute_task("Simple task")
        
        assert result is not None
        mock_text_provider.generate_text.assert_called()

    @pytest.mark.asyncio
    async def test_task_decomposer_coordinate_execution(self, echo_kernel, mock_text_provider):
        """Test task coordination."""
        echo_kernel.register_provider(mock_text_provider)
        executor = EchoAgent("Executor", echo_kernel)
        decomposer = TaskDecomposerAgent("Decomposer", echo_kernel, executor)
        
        # Mock decomposition and execution
        mock_text_provider.generate_text.side_effect = [
            "1. Step one\n2. Step two",
            "Result 1",
            "Result 2"
        ]
        
        result = await decomposer.coordinate_execution("Complex task")
        
        assert result is not None
        assert mock_text_provider.generate_text.call_count >= 3


class TestLoopAgent:
    """Test cases for LoopAgent class."""

    @pytest.mark.unit
    def test_loop_agent_initialization(self, echo_kernel):
        """Test LoopAgent initialization."""
        agent = LoopAgent("LoopAgent", echo_kernel, max_iterations=5)
        
        assert agent.name == "LoopAgent"
        assert agent.kernel == echo_kernel
        assert agent.max_iterations == 5
        assert agent.iteration_count == 0

    @pytest.mark.asyncio
    async def test_loop_agent_iterate_with_stop_condition(self, echo_kernel, mock_text_provider):
        """Test LoopAgent iteration with stop condition."""
        echo_kernel.register_provider(mock_text_provider)
        agent = LoopAgent("LoopAgent", echo_kernel, max_iterations=3)
        
        def stop_condition(result: str) -> bool:
            return "final" in result.lower()
        
        # Mock responses that eventually meet stop condition
        mock_text_provider.generate_text.side_effect = [
            "First iteration",
            "Second iteration",
            "Final result"
        ]
        
        result = await agent.iterate("Initial task", stop_condition)
        
        assert result == "Final result"
        assert agent.iteration_count == 3

    @pytest.mark.asyncio
    async def test_loop_agent_iterate_max_iterations(self, echo_kernel, mock_text_provider):
        """Test LoopAgent iteration with max iterations reached."""
        echo_kernel.register_provider(mock_text_provider)
        agent = LoopAgent("LoopAgent", echo_kernel, max_iterations=2)
        
        def stop_condition(result: str) -> bool:
            return False  # Never stop
        
        mock_text_provider.generate_text.return_value = "Iteration result"
        
        result = await agent.iterate("Initial task", stop_condition)
        
        assert result == "Iteration result"
        assert agent.iteration_count == 2

    @pytest.mark.unit
    def test_loop_agent_reset(self, echo_kernel):
        """Test LoopAgent reset functionality."""
        agent = LoopAgent("LoopAgent", echo_kernel)
        agent.iteration_count = 5
        
        agent.reset()
        
        assert agent.iteration_count == 0


class TestRouterAgent:
    """Test cases for RouterAgent class."""

    @pytest.mark.unit
    def test_router_agent_initialization(self, echo_kernel):
        """Test RouterAgent initialization."""
        specialists = {
            "coding": EchoAgent("Coder", echo_kernel),
            "writing": EchoAgent("Writer", echo_kernel)
        }
        router = RouterAgent("Router", echo_kernel, specialists)
        
        assert router.name == "Router"
        assert router.kernel == echo_kernel
        assert router.specialists == specialists

    @pytest.mark.asyncio
    async def test_router_agent_route_task(self, echo_kernel, mock_text_provider):
        """Test task routing."""
        echo_kernel.register_provider(mock_text_provider)
        specialists = {
            "coding": EchoAgent("Coder", echo_kernel),
            "writing": EchoAgent("Writer", echo_kernel)
        }
        router = RouterAgent("Router", echo_kernel, specialists)
        
        # Mock routing decision
        mock_text_provider.generate_text.return_value = "coding"
        
        result = await router.route_task("Write a Python function")
        
        assert result is not None
        mock_text_provider.generate_text.assert_called()

    @pytest.mark.asyncio
    async def test_router_agent_route_task_with_fallback(self, echo_kernel, mock_text_provider):
        """Test task routing with fallback."""
        echo_kernel.register_provider(mock_text_provider)
        specialists = {
            "coding": EchoAgent("Coder", echo_kernel),
            "writing": EchoAgent("Writer", echo_kernel)
        }
        router = RouterAgent("Router", echo_kernel, specialists)
        
        # Mock invalid routing decision
        mock_text_provider.generate_text.return_value = "invalid_specialist"
        
        result = await router.route_task("Some task")
        
        # Should use first specialist as fallback
        assert result is not None


class TestSpecialistRouterAgent:
    """Test cases for SpecialistRouterAgent class."""

    @pytest.mark.unit
    def test_specialist_router_initialization(self, echo_kernel):
        """Test SpecialistRouterAgent initialization."""
        specialists = {
            "coding": EchoAgent("Coder", echo_kernel),
            "writing": EchoAgent("Writer", echo_kernel)
        }
        router = SpecialistRouterAgent("SpecialistRouter", echo_kernel, specialists)
        
        assert router.name == "SpecialistRouter"
        assert router.kernel == echo_kernel
        assert router.specialists == specialists
        assert router.max_retries == 3

    @pytest.mark.asyncio
    async def test_specialist_router_route_with_validation(self, echo_kernel, mock_text_provider):
        """Test routing with validation."""
        echo_kernel.register_provider(mock_text_provider)
        specialists = {
            "coding": EchoAgent("Coder", echo_kernel),
            "writing": EchoAgent("Writer", echo_kernel)
        }
        router = SpecialistRouterAgent("SpecialistRouter", echo_kernel, specialists)
        
        def validator(result: str) -> bool:
            return "valid" in result.lower()
        
        # Mock responses
        mock_text_provider.generate_text.side_effect = [
            "coding",  # Routing decision
            "valid result"  # Specialist response
        ]
        
        result = await router.route_with_validation("Task", validator)
        
        assert result is not None
        assert mock_text_provider.generate_text.call_count == 2

    @pytest.mark.asyncio
    async def test_specialist_router_route_with_retries(self, echo_kernel, mock_text_provider):
        """Test routing with retries."""
        echo_kernel.register_provider(mock_text_provider)
        specialists = {
            "coding": EchoAgent("Coder", echo_kernel),
            "writing": EchoAgent("Writer", echo_kernel)
        }
        router = SpecialistRouterAgent("SpecialistRouter", echo_kernel, specialists, max_retries=2)

        def validator(result: str) -> bool:
            return False  # Always fail validation

        # Mock responses
        mock_text_provider.generate_text.side_effect = [
            "coding", "invalid",  # First attempt
            "writing", "invalid",  # Second attempt
            "coding", "final result"  # Third attempt
        ]

        with pytest.raises(ValueError, match="Failed to route task after 2 attempts"):
            await router.route_with_validation("Task", validator)


class TestMemoryAgent:
    """Test cases for MemoryAgent class."""

    @pytest.mark.unit
    def test_memory_agent_initialization(self, echo_kernel, mock_memory_provider):
        """Test MemoryAgent initialization."""
        echo_kernel.register_provider(mock_memory_provider)
        agent = MemoryAgent("MemoryAgent", echo_kernel)
        
        assert agent.name == "MemoryAgent"
        assert agent.kernel == echo_kernel
        assert agent.memory_provider == mock_memory_provider

    @pytest.mark.asyncio
    async def test_memory_agent_process_with_memory(self, echo_kernel, mock_text_provider, mock_memory_provider):
        """Test MemoryAgent processing with memory."""
        echo_kernel.register_provider(mock_text_provider)
        echo_kernel.register_provider(mock_memory_provider)
        agent = MemoryAgent("MemoryAgent", echo_kernel)
        
        # Mock memory search results
        mock_memory_provider.search_similar.return_value = [
            {"text": "Previous conversation", "score": 0.8}
        ]
        
        result = await agent.process_with_memory("New message")
        
        assert result is not None
        mock_memory_provider.search_similar.assert_called_once()
        mock_text_provider.generate_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_memory_agent_add_to_memory(self, echo_kernel, mock_memory_provider):
        """Test MemoryAgent adding to memory."""
        echo_kernel.register_provider(mock_memory_provider)
        agent = MemoryAgent("MemoryAgent", echo_kernel)
        
        await agent.add_to_memory("Important information", {"source": "test"})
        
        mock_memory_provider.add_text.assert_called_once_with(
            "Important information", {"source": "test"}
        )

    @pytest.mark.asyncio
    async def test_memory_agent_search_memory(self, echo_kernel, mock_memory_provider, sample_search_results):
        """Test MemoryAgent memory search."""
        echo_kernel.register_provider(mock_memory_provider)
        agent = MemoryAgent("MemoryAgent", echo_kernel)
        
        mock_memory_provider.search_similar.return_value = sample_search_results
        
        results = await agent.search_memory("Query")
        
        assert results == sample_search_results
        mock_memory_provider.search_similar.assert_called_once_with("Query")

    @pytest.mark.asyncio
    async def test_memory_agent_conversation_context(self, echo_kernel, mock_text_provider, mock_memory_provider):
        """Test MemoryAgent conversation context management."""
        echo_kernel.register_provider(mock_text_provider)
        echo_kernel.register_provider(mock_memory_provider)
        agent = MemoryAgent("MemoryAgent", echo_kernel)
        
        # Mock memory search
        mock_memory_provider.search_similar.return_value = []
        
        # Process multiple messages
        await agent.process_with_memory("First message")
        await agent.process_with_memory("Second message")
        await agent.process_with_memory("Third message")
        
        # Should have added each message to memory
        assert mock_memory_provider.add_text.call_count == 3


class TestAgentIntegration:
    """Integration tests for agent interactions."""

    @pytest.mark.asyncio
    async def test_agent_chain_execution(self, echo_kernel, mock_text_provider):
        """Test chaining multiple agents together."""
        echo_kernel.register_provider(mock_text_provider)

        # Create a chain: Router -> TaskDecomposer -> LoopAgent
        executor = EchoAgent("Executor", echo_kernel)
        decomposer = TaskDecomposerAgent("Decomposer", echo_kernel, executor)
        loop_agent = LoopAgent("LoopAgent", echo_kernel, max_iterations=2)
        router = RouterAgent("Router", echo_kernel, {"decompose": decomposer, "loop": loop_agent})

        # Mock responses
        mock_text_provider.generate_text.side_effect = [
            "decompose",  # Router decision
            "1. Step one\n2. Step two",  # Decomposition
            "Result 1",  # Step one result
            "Result 2",  # Step two result
            "Final result"  # Coordination result
        ]

        result = await router.route_task("Complex task")

        assert result is not None
        assert mock_text_provider.generate_text.call_count >= 4

    @pytest.mark.asyncio
    async def test_memory_agent_with_specialist_router(self, echo_kernel, mock_text_provider, mock_memory_provider):
        """Test MemoryAgent working with SpecialistRouterAgent."""
        echo_kernel.register_provider(mock_text_provider)
        echo_kernel.register_provider(mock_memory_provider)
        
        memory_agent = MemoryAgent("MemoryAgent", echo_kernel)
        specialists = {"memory": memory_agent}
        router = SpecialistRouterAgent("Router", echo_kernel, specialists)
        
        # Mock responses
        mock_text_provider.generate_text.side_effect = [
            "memory",  # Routing decision
            "Response with context"  # Memory agent response
        ]
        mock_memory_provider.search_similar.return_value = []
        
        def validator(result: str) -> bool:
            return "context" in result.lower()
        
        result = await router.route_with_validation("Task with context", validator)
        
        assert result is not None
        assert "context" in result.lower() 