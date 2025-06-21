from typing import Dict, Any, List, Optional
import uuid
import numpy as np
import faiss
from ..IStorageProvider import IStorageProvider

class InMemoryStorageProvider(IStorageProvider):
    def __init__(self):
        """Initialize the in-memory storage provider."""
        self._index = None
        self._metadata: Dict[str, Dict[str, Any]] = {}  # vector_id -> metadata
        self._id_to_index: Dict[str, int] = {}  # vector_id -> FAISS index
        self._index_to_id: Dict[int, str] = {}  # FAISS index -> vector_id
        self._next_index = 0
    
    async def initialize(self, dimension: int) -> None:
        """Initialize the FAISS index with the given dimension."""
        self._index = faiss.IndexFlatL2(dimension)
    
    async def add_vector(self, vector: np.ndarray, metadata: Dict[str, Any]) -> str:
        """Add a vector to the FAISS index and store its metadata."""
        if self._index is None:
            await self.initialize(vector.shape[0])
        
        vector_id = str(uuid.uuid4())
        
        # Ensure vector is 2D and has correct data type for FAISS
        if vector.ndim == 1:
            vector = vector.reshape(1, -1)
        vector = vector.astype(np.float32)
        
        # Add vector to FAISS index
        self._index.add(vector)
        
        # Store mapping between vector_id and FAISS index
        self._id_to_index[vector_id] = self._next_index
        self._index_to_id[self._next_index] = vector_id
        self._next_index += 1
        
        # Store metadata
        self._metadata[vector_id] = metadata
        
        return vector_id
    
    async def search_vectors(self, query_vector: np.ndarray, limit: int) -> List[Dict[str, Any]]:
        """Search for similar vectors using FAISS."""
        if self._index is None or not self._metadata:
            return []
        
        # Ensure query vector is 2D and has correct data type for FAISS
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        query_vector = query_vector.astype(np.float32)
        
        # Search using FAISS
        distances, indices = self._index.search(query_vector, limit)
        
        # Convert results to the expected format
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # FAISS returns -1 for empty slots
                vector_id = self._index_to_id[idx]
                metadata = self._metadata[vector_id]
                # Convert L2 distance to similarity score (1 / (1 + distance))
                similarity = 1 / (1 + distance)
                results.append({
                    "id": vector_id,
                    "metadata": metadata,
                    "similarity": float(similarity)
                })
        
        return results
    
    async def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a vector and its metadata by ID."""
        if vector_id not in self._metadata:
            return None
        
        idx = self._id_to_index[vector_id]
        vector = faiss.vector_to_array(self._index.reconstruct(idx))
        
        return {
            "id": vector_id,
            "vector": vector,
            "metadata": self._metadata[vector_id]
        }
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from storage."""
        if vector_id not in self._metadata:
            return False
        
        # Get the FAISS index for this vector_id
        idx = self._id_to_index[vector_id]
        
        # Remove from FAISS index (FAISS doesn't support direct deletion, so we'll need to rebuild)
        if self._index is not None:
            # Create a new index
            dimension = self._index.d
            new_index = faiss.IndexFlatL2(dimension)
            
            # Rebuild the index excluding the deleted vector
            vectors = []
            new_id_to_index = {}
            new_index_to_id = {}
            new_next_index = 0
            
            for old_idx, old_vector_id in self._index_to_id.items():
                if old_vector_id != vector_id:
                    # Get the vector from the original index
                    vector = faiss.vector_to_array(self._index.reconstruct(old_idx))
                    vectors.append(vector)
                    new_id_to_index[old_vector_id] = new_next_index
                    new_index_to_id[new_next_index] = old_vector_id
                    new_next_index += 1
            
            if vectors:
                vectors_array = np.array(vectors, dtype=np.float32)
                new_index.add(vectors_array)
            
            self._index = new_index
            self._id_to_index = new_id_to_index
            self._index_to_id = new_index_to_id
            self._next_index = new_next_index
        
        # Remove from metadata
        del self._metadata[vector_id]
        del self._id_to_index[vector_id]
        
        return True 