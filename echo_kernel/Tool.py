"""
EchoKernel Tool System

This module provides the EchoTool decorator and related functionality for creating
tools that can be used by AI models in the EchoKernel framework.

Tools are callable functions that can be invoked by AI models during text generation.
They provide a way to extend the capabilities of AI models with custom functionality
like API calls, data processing, file operations, etc.

Example:
    ```python
    from echo_kernel.Tool import EchoTool
    
    @EchoTool(description="Calculate the sum of two numbers")
    def add_numbers(a: int, b: int) -> int:
        return a + b
    
    # Register with kernel
    kernel.register_tool(add_numbers)
    ```
"""

from typing import Callable, Dict, Any, get_type_hints, Optional, List
import inspect
import functools

def EchoTool(description: str = None, name: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> Callable:
    """
    Decorator to create an EchoKernel tool from a function.
    
    This decorator transforms a regular Python function into an EchoKernel tool
    that can be used by AI models. It automatically extracts the function's
    signature, type hints, and documentation to create a tool definition.
    
    Args:
        description: A human-readable description of what the tool does. If None, uses docstring or function name.
        name: Optional custom name for the tool (defaults to function name).
        parameters: Optional custom parameter definitions.
    
    Returns:
        A decorator function that wraps the original function with tool metadata.
    
    Example:
        ```python
        @EchoTool(description="Fetch weather data for a city")
        def get_weather(city: str, country: str = "US") -> Dict[str, Any]:
            # Implementation here
            return {"temperature": 72, "condition": "sunny"}
        ```
    
    Note:
        The decorated function must have type hints for all parameters and return value.
        The function name will be used as the tool name unless a custom name is provided.
    """
    def decorator(func: Callable) -> Callable:
        # Validate parameters
        if description is not None and not description.strip():
            raise ValueError("Description cannot be empty")
        if name is not None and not name.strip():
            raise ValueError("Name cannot be empty")
        
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # Use custom name or function name
        tool_name = name or func.__name__
        
        # Use custom description, docstring, or function name
        if description is not None:
            tool_description = description
        elif func.__doc__:
            tool_description = func.__doc__.strip().split('\n')[0]
        else:
            tool_description = func.__name__
        
        # Use custom parameters or extract from function signature
        if parameters is not None:
            tool_params = parameters
        else:
            # Extract parameter information
            param_properties = {}
            required_params = []
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':  # Skip self parameter for methods
                    continue
                    
                param_type = type_hints.get(param_name, "Any")
                param_info = {
                    "type": _python_type_to_json_type(str(param_type)),
                    "description": f"Parameter: {param_name}"
                }
                
                if param.default != inspect.Parameter.empty:
                    param_info["default"] = param.default
                else:
                    required_params.append(param_name)
                    
                param_properties[param_name] = param_info
            
            tool_params = {
                "type": "object",
                "properties": param_properties,
                "required": required_params
            }
        
        # Create tool definition
        tool_def = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_description,
                "parameters": tool_params
            }
        }
        
        # Create tool metadata
        tool_metadata = ToolMetadata(tool_name, tool_description, tool_params)
        
        # Check if function is already wrapped by another decorator
        if hasattr(func, '_echo_tool_metadata'):
            # Function already has EchoTool metadata, just update it
            func._echo_tool_metadata = tool_metadata
            func.name = tool_name
            func.definition = tool_def
            func.description = tool_description
            return func
        
        # Create a wrapper that preserves metadata
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Copy metadata to wrapper
        wrapper._echo_tool_metadata = tool_metadata
        wrapper.name = tool_name
        wrapper.definition = tool_def
        wrapper.description = tool_description
        
        return wrapper
    
    return decorator

def _python_type_to_json_type(python_type: str) -> str:
    """
    Convert Python type hints to JSON schema types.
    
    Args:
        python_type: Python type as string (e.g., "str", "int", "List[str]")
    
    Returns:
        JSON schema type string
    """
    type_mapping = {
        "str": "string",
        "int": "integer", 
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "dict": "object",
        "Any": "object"
    }
    
    # Handle basic types
    if python_type in type_mapping:
        return type_mapping[python_type]
    
    # Handle List types
    if python_type.startswith("List[") or python_type.startswith("list["):
        return "array"
    
    # Handle Dict types
    if python_type.startswith("Dict[") or python_type.startswith("dict["):
        return "object"
    
    # Default to object for complex types
    return "object"

class ToolMetadata:
    """Metadata for EchoKernel tools."""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    def __eq__(self, other):
        if not isinstance(other, ToolMetadata):
            return False
        return (self.name == other.name and 
                self.description == other.description and 
                self.parameters == other.parameters)
    
    def __repr__(self):
        return f"ToolMetadata(name='{self.name}', description='{self.description}')" 