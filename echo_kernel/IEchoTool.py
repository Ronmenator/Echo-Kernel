from typing import Protocol, runtime_checkable, Any, Dict

@runtime_checkable
class IEchoTool(Protocol):
    @property
    def name(self) -> str:
        """Returns the tool's name"""
        ...
    
    @property
    def definition(self) -> Dict[str, Any]:
        """Returns the tool's definition/configuration"""
        ...
    
    def __call__(self, *args, **kwargs) -> Any:
        """Executes the tool with the given arguments"""
        ...