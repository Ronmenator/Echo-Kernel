from typing import Callable, Dict, Any, get_type_hints
import inspect

def EchoTool(name: str = None, description: str = ""):
    def decorator(fn: Callable):
        # Get the function's type hints
        type_hints = get_type_hints(fn)
        type_hints.pop('return', None)
        
        # Get parameter information
        sig = inspect.signature(fn)
        parameters = {}
        required = []
        
        # Map Python types to JSON Schema types
        type_mapping = {
            'str': 'string',
            'int': 'integer',
            'float': 'number',
            'bool': 'boolean',
            'list': 'array',
            'dict': 'object'
        }
        
        for param_name, param in sig.parameters.items():
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
            
            param_type = type_hints.get(param_name, Any)
            type_name = getattr(param_type, "__name__", str(param_type))
            
            parameters[param_name] = {
                "type": type_mapping.get(type_name.lower(), 'string'),
                "description": param.annotation.__doc__ if hasattr(param.annotation, "__doc__") else ""
            }
        
        # Create the tool definition
        tool_name = name or fn.__name__
        fn._tool_definition = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description or fn.__doc__ or "",
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required
                }
            }
        }
        
        # Make the function callable as a tool
        class ToolWrapper:
            def __init__(self, func):
                self.func = func
                self.name = tool_name
            
            @property
            def definition(self) -> Dict[str, Any]:
                return self.func._tool_definition
            
            def __call__(self, *args, **kwargs) -> Any:
                return self.func(*args, **kwargs)
        
        return ToolWrapper(fn)
    return decorator 