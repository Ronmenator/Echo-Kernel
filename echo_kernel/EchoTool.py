from typing import Callable, Any, Dict, List
import inspect

class EchoTool:
    """A class representing a tool that can be executed by the Echo Kernel."""

    def __init__(self, name: str, func: Callable, description: str = "", parameters: Dict[str, Any] = None):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters if parameters is not None else self._extract_parameters_from_callable()

    def _extract_parameters_from_callable(self) -> Dict[str, Any]:
        """Extracts parameters from the tool's callable function."""
        try:
            sig = inspect.signature(self.func)
            params = {}
            for param in sig.parameters.values():
                params[param.name] = {
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any",
                    "required": param.default == inspect.Parameter.empty
                }
            return params
        except (ValueError, TypeError):
            return {}

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return f"EchoTool(name={self.name}, func={self.func}, description={self.description}, parameters={self.parameters})"

    def __eq__(self, other):
        if isinstance(other, EchoTool):
            return self.name == other.name and self.func == other.func and self.description == other.description and self.parameters == other.parameters
        return False

    def __hash__(self):
        return hash((self.name, self.func, self.description, self.parameters))

    def __getattr__(self, attr):
        if attr == 'definition':
            return self.to_dict()
        if attr in ['name', 'func', 'description', 'parameters']:
            return getattr(self, attr)
        raise AttributeError(f"'EchoTool' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        if attr in ['name', 'func', 'description', 'parameters']:
            object.__setattr__(self, attr, value)
        else:
            raise AttributeError(f"'EchoTool' object has no attribute '{attr}'")

    def __delattr__(self, attr):
        if attr in ['name', 'func', 'description', 'parameters']:
            object.__delattr__(self, attr)
        else:
            raise AttributeError(f"'EchoTool' object has no attribute '{attr}'")

    def __dir__(self):
        return ['name', 'func', 'description', 'parameters'] + object.__dir__(self)

    def __str__(self):
        return f"EchoTool(name={self.name}, func={self.func}, description={self.description}, parameters={self.parameters})" 