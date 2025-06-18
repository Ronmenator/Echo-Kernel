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

from typing import Callable, Dict, Any, get_type_hints
import inspect

def EchoTool(description: str) -> Callable:
    """
    Decorator to create an EchoKernel tool from a function.
    
    This decorator transforms a regular Python function into an EchoKernel tool
    that can be used by AI models. It automatically extracts the function's
    signature, type hints, and documentation to create a tool definition.
    
    Args:
        description: A human-readable description of what the tool does.
    
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
        The function name will be used as the tool name.
    """
    def decorator(func: Callable) -> Callable:
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # Extract parameter information
        parameters = []
        for name, param in sig.parameters.items():
            if name == 'self':  # Skip self parameter for methods
                continue
                
            param_info = {
                "name": name,
                "type": str(type_hints.get(name, "Any")),
                "required": param.default == inspect.Parameter.empty
            }
            
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
                
            parameters.append(param_info)
        
        # Create tool definition
        tool_def = {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    param["name"]: {
                        "type": _python_type_to_json_type(param["type"]),
                        "description": f"Parameter: {param['name']}"
                    }
                    for param in parameters
                },
                "required": [param["name"] for param in parameters if param["required"]]
            }
        }
        
        # Create tool instance with metadata
        tool_instance = func
        tool_instance.name = func.__name__
        tool_instance.definition = tool_def
        tool_instance.description = description
        
        return tool_instance
    
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