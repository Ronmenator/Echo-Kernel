from typing import List, Dict, Any, Optional
import uuid
import numpy as np
from ..ITextMemory import ITextMemory
from ..IEmbeddingProvider import IEmbeddingProvider
from ..IStorageProvider import IStorageProvider
from .InMemoryStorageProvider import InMemoryStorageProvider

class VectorMemoryProvider(ITextMemory):
    def __init__(self, embedding_provider: IEmbeddingProvider, storage_provider: Optional[IStorageProvider] = None):
        """Initialize the vector memory provider with an embedding provider and optional storage provider.
        
        Args:
            embedding_provider: Provider for generating embeddings
            storage_provider: Optional storage provider (defaults to InMemoryStorageProvider)
        """
        self.embedding_provider = embedding_provider
        self.storage_provider = storage_provider or InMemoryStorageProvider()
        self._texts: Dict[str, str] = {}  # text_id -> text
    
    async def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add text to the memory store and return its ID."""
        text_id = str(uuid.uuid4())
        embedding = await self.embedding_provider.generate_embedding(text)
        
        # Convert embedding to numpy array (1D)
        embedding_array = np.array(embedding, dtype=np.float32)
        
        # Store text separately
        self._texts[text_id] = text
        
        # Add vector to storage
        await self.storage_provider.add_vector(
            embedding_array,
            {"text_id": text_id, **(metadata or {})}
        )
        
        return text_id
    
    async def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts in the memory store."""
        if not self._texts:
            return []
            
        # Generate embedding for the query
        query_embedding = await self.embedding_provider.generate_embedding(query)
        query_array = np.array(query_embedding, dtype=np.float32)
        
        # Search using storage provider
        results = await self.storage_provider.search_vectors(query_array, limit)
        
        # Add text to results
        for result in results:
            text_id = result["metadata"]["text_id"]
            result["text"] = self._texts[text_id]
            # Remove text_id from metadata as it's now in the main result
            del result["metadata"]["text_id"]
        
        return results
    
    async def get_text(self, text_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve text and its metadata by ID."""
        if text_id not in self._texts:
            return None
        
        # Get vector and metadata from storage
        vector_data = await self.storage_provider.get_vector(text_id)
        if vector_data is None:
            return None
        
        return {
            "id": text_id,
            "text": self._texts[text_id],
            "metadata": vector_data["metadata"]
        }
    
    async def delete_text(self, text_id: str) -> bool:
        """Delete text from the memory store."""
        if text_id not in self._texts:
            return False
        
        # Delete from storage
        success = await self.storage_provider.delete_vector(text_id)
        if success:
            # Delete text
            del self._texts[text_id]
        
        return success 