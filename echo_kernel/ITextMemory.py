from typing import List, Dict, Any, Protocol, runtime_checkable, Optional

@runtime_checkable
class ITextMemory(Protocol):
    async def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add text to the memory store and return its ID"""
        ...
    
    async def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts in the memory store"""
        ...
    
    async def get_text(self, text_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve text and its metadata by ID"""
        ...
    
    async def delete_text(self, text_id: str) -> bool:
        """Delete text from the memory store"""
        ... 