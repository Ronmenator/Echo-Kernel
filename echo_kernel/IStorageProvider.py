from typing import Dict, Any, List, Optional, Protocol, runtime_checkable
import numpy as np

@runtime_checkable
class IStorageProvider(Protocol):
    """Interface for vector storage providers."""
    
    async def initialize(self, dimension: int) -> None:
        """Initialize the storage with the given vector dimension."""
        ...
    
    async def add_vector(self, vector: np.ndarray, metadata: Dict[str, Any]) -> str:
        """Add a vector to storage and return its ID."""
        ...
    
    async def search_vectors(self, query_vector: np.ndarray, limit: int) -> List[Dict[str, Any]]:
        """Search for similar vectors and return their metadata and similarity scores."""
        ...
    
    async def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a vector and its metadata by ID."""
        ...
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from storage."""
        ... 