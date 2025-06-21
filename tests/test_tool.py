"""
Unit tests for Tool module and EchoTool decorator.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from unittest.mock import Mock
import functools

from echo_kernel.Tool import EchoTool, ToolMetadata


class TestEchoTool:
    """Test cases for EchoTool decorator."""

    @pytest.mark.unit
    def test_echo_tool_decorator_basic(self):
        """Test basic EchoTool decorator functionality."""
        @EchoTool(description="A simple test tool")
        def test_tool(text: str) -> str:
            return f"Processed: {text}"
        
        # Check that the function still works
        result = test_tool("hello")
        assert result == "Processed: hello"
        
        # Check that metadata was added
        assert hasattr(test_tool, '_echo_tool_metadata')
        assert test_tool._echo_tool_metadata.description == "A simple test tool"
        assert test_tool._echo_tool_metadata.name == "test_tool"

    @pytest.mark.unit
    def test_echo_tool_decorator_with_name(self):
        """Test EchoTool decorator with custom name."""
        @EchoTool(description="Custom named tool", name="custom_tool")
        def some_function(text: str) -> str:
            return f"Custom: {text}"
        
        assert some_function._echo_tool_metadata.name == "custom_tool"
        assert some_function._echo_tool_metadata.description == "Custom named tool"

    @pytest.mark.unit
    def test_echo_tool_decorator_with_parameters(self):
        """Test EchoTool decorator with parameter information."""
        @EchoTool(
            description="Tool with parameters",
            parameters={
                "text": {"type": "string", "description": "Input text"},
                "count": {"type": "integer", "description": "Repeat count", "default": 1}
            }
        )
        def repeat_tool(text: str, count: int = 1) -> str:
            return text * count
        
        metadata = repeat_tool._echo_tool_metadata
        assert metadata.description == "Tool with parameters"
        assert "text" in metadata.parameters
        assert "count" in metadata.parameters
        assert metadata.parameters["text"]["type"] == "string"
        assert metadata.parameters["count"]["type"] == "integer"

    @pytest.mark.unit
    def test_echo_tool_decorator_async_function(self):
        """Test EchoTool decorator with async function."""
        @EchoTool(description="Async test tool")
        async def async_tool(text: str) -> str:
            await asyncio.sleep(0.01)  # Simulate async work
            return f"Async: {text}"
        
        assert hasattr(async_tool, '_echo_tool_metadata')
        assert async_tool._echo_tool_metadata.description == "Async test tool"

    @pytest.mark.unit
    def test_echo_tool_decorator_complex_types(self):
        """Test EchoTool decorator with complex parameter types."""
        @EchoTool(
            description="Complex tool",
            parameters={
                "items": {"type": "array", "description": "List of items"},
                "config": {"type": "object", "description": "Configuration object"}
            }
        )
        def complex_tool(items: List[str], config: Dict[str, Any]) -> str:
            return f"Processed {len(items)} items with config: {config}"
        
        metadata = complex_tool._echo_tool_metadata
        assert metadata.parameters["items"]["type"] == "array"
        assert metadata.parameters["config"]["type"] == "object"

    @pytest.mark.unit
    def test_echo_tool_decorator_without_description(self):
        """Test EchoTool decorator without description (should use docstring)."""
        @EchoTool()
        def docstring_tool(text: str) -> str:
            """This is a tool with a docstring."""
            return f"Docstring: {text}"
        
        metadata = docstring_tool._echo_tool_metadata
        assert metadata.description == "This is a tool with a docstring."

    @pytest.mark.unit
    def test_echo_tool_decorator_without_docstring(self):
        """Test EchoTool decorator without docstring (should use function name)."""
        @EchoTool()
        def no_docstring_tool(text: str) -> str:
            return f"No docstring: {text}"
        
        metadata = no_docstring_tool._echo_tool_metadata
        assert metadata.description == "no_docstring_tool"

    @pytest.mark.unit
    def test_echo_tool_decorator_multiple_decorators(self):
        """Test EchoTool decorator with other decorators."""
        def other_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return f"Wrapped: {func(*args, **kwargs)}"
            return wrapper
        
        @other_decorator
        @EchoTool(description="Multiple decorators")
        def multi_decorator_tool(text: str) -> str:
            return f"Original: {text}"
        
        # Check that EchoTool metadata is preserved
        assert hasattr(multi_decorator_tool, '_echo_tool_metadata')
        assert multi_decorator_tool._echo_tool_metadata.description == "Multiple decorators"
        
        # Check that other decorator still works
        result = multi_decorator_tool("test")
        assert result == "Wrapped: Original: test"

    @pytest.mark.unit
    def test_echo_tool_decorator_class_method(self):
        """Test EchoTool decorator with class method."""
        class TestClass:
            @EchoTool(description="Class method tool")
            def class_method_tool(self, text: str) -> str:
                return f"Class method: {text}"
        
        instance = TestClass()
        assert hasattr(instance.class_method_tool, '_echo_tool_metadata')
        assert instance.class_method_tool._echo_tool_metadata.description == "Class method tool"

    @pytest.mark.unit
    def test_echo_tool_decorator_static_method(self):
        """Test EchoTool decorator with static method."""
        class TestClass:
            @staticmethod
            @EchoTool(description="Static method tool")
            def static_method_tool(text: str) -> str:
                return f"Static method: {text}"
        
        assert hasattr(TestClass.static_method_tool, '_echo_tool_metadata')
        assert TestClass.static_method_tool._echo_tool_metadata.description == "Static method tool"

    @pytest.mark.unit
    def test_echo_tool_decorator_lambda_function(self):
        """Test EchoTool decorator with lambda function."""
        lambda_tool = EchoTool(description="Lambda tool")(lambda x: f"Lambda: {x}")
        
        assert hasattr(lambda_tool, '_echo_tool_metadata')
        assert lambda_tool._echo_tool_metadata.description == "Lambda tool"
        
        result = lambda_tool("test")
        assert result == "Lambda: test"

    @pytest.mark.unit
    def test_echo_tool_decorator_return_type_annotation(self):
        """Test EchoTool decorator preserves return type annotations."""
        @EchoTool(description="Return type test")
        def return_type_tool(text: str) -> str:
            return text
        
        # Check that type annotations are preserved
        import inspect
        sig = inspect.signature(return_type_tool)
        assert sig.return_annotation == str
        assert sig.parameters['text'].annotation == str

    @pytest.mark.unit
    def test_echo_tool_decorator_metadata_access(self):
        """Test accessing EchoTool metadata."""
        @EchoTool(
            description="Metadata test tool",
            name="metadata_test",
            parameters={"text": {"type": "string", "description": "Input text"}}
        )
        def metadata_test_tool(text: str) -> str:
            return text
        
        metadata = metadata_test_tool._echo_tool_metadata
        
        assert metadata.name == "metadata_test"
        assert metadata.description == "Metadata test tool"
        assert "text" in metadata.parameters
        assert metadata.parameters["text"]["type"] == "string"

    @pytest.mark.unit
    def test_echo_tool_decorator_inheritance(self):
        """Test EchoTool decorator with inherited functions."""
        class BaseClass:
            @EchoTool(description="Base tool")
            def base_tool(self, text: str) -> str:
                return f"Base: {text}"
        
        class DerivedClass(BaseClass):
            @EchoTool(description="Derived tool")
            def derived_tool(self, text: str) -> str:
                return f"Derived: {text}"
        
        base_instance = BaseClass()
        derived_instance = DerivedClass()
        
        # Check that both have metadata
        assert hasattr(base_instance.base_tool, '_echo_tool_metadata')
        assert hasattr(derived_instance.derived_tool, '_echo_tool_metadata')
        assert hasattr(derived_instance.base_tool, '_echo_tool_metadata')

    @pytest.mark.unit
    def test_echo_tool_decorator_error_handling(self):
        """Test EchoTool decorator error handling."""
        # Test with invalid parameters
        with pytest.raises(ValueError):
            @EchoTool(description="", name="")  # Empty description and name
            def invalid_tool(text: str) -> str:
                return text

    @pytest.mark.unit
    def test_echo_tool_decorator_function_signature_preservation(self):
        """Test that EchoTool decorator preserves function signature."""
        @EchoTool(description="Signature test")
        def signature_test_tool(text: str, count: int = 1, prefix: str = "Test") -> str:
            """Test function with complex signature."""
            return f"{prefix}: {text * count}"
        
        import inspect
        sig = inspect.signature(signature_test_tool)
        
        # Check parameters
        assert 'text' in sig.parameters
        assert 'count' in sig.parameters
        assert 'prefix' in sig.parameters
        
        # Check default values
        assert sig.parameters['count'].default == 1
        assert sig.parameters['prefix'].default == "Test"
        
        # Check annotations
        assert sig.parameters['text'].annotation == str
        assert sig.parameters['count'].annotation == int
        assert sig.parameters['prefix'].annotation == str
        assert sig.return_annotation == str
        
        # Check docstring
        assert signature_test_tool.__doc__ == "Test function with complex signature."


class TestToolMetadata:
    """Test cases for ToolMetadata class."""

    @pytest.mark.unit
    def test_tool_metadata_creation(self):
        """Test ToolMetadata creation."""
        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool description",
            parameters={"text": {"type": "string"}}
        )
        
        assert metadata.name == "test_tool"
        assert metadata.description == "Test tool description"
        assert metadata.parameters == {"text": {"type": "string"}}

    @pytest.mark.unit
    def test_tool_metadata_default_values(self):
        """Test ToolMetadata with default values."""
        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool"
        )
        
        assert metadata.name == "test_tool"
        assert metadata.description == "Test tool"
        assert metadata.parameters == {}

    @pytest.mark.unit
    def test_tool_metadata_to_dict(self):
        """Test ToolMetadata to_dict method."""
        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool description",
            parameters={"text": {"type": "string", "description": "Input text"}}
        )
        
        metadata_dict = metadata.to_dict()
        
        assert metadata_dict["name"] == "test_tool"
        assert metadata_dict["description"] == "Test tool description"
        assert metadata_dict["parameters"] == {"text": {"type": "string", "description": "Input text"}}

    @pytest.mark.unit
    def test_tool_metadata_equality(self):
        """Test ToolMetadata equality."""
        metadata1 = ToolMetadata("test", "description", {"param": {"type": "string"}})
        metadata2 = ToolMetadata("test", "description", {"param": {"type": "string"}})
        metadata3 = ToolMetadata("different", "description", {"param": {"type": "string"}})
        
        assert metadata1 == metadata2
        assert metadata1 != metadata3

    @pytest.mark.unit
    def test_tool_metadata_repr(self):
        """Test ToolMetadata string representation."""
        metadata = ToolMetadata("test_tool", "Test description")
        
        repr_str = repr(metadata)
        assert "test_tool" in repr_str
        assert "Test description" in repr_str 