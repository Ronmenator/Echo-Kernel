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
        self._text_to_vector: Dict[str, str] = {}  # text_id -> vector_id
    
    async def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add text to the memory store and return its ID."""
        text_id = str(uuid.uuid4())
        embedding = await self.embedding_provider.generate_embedding(text)
        
        # Convert embedding to numpy array (1D)
        embedding_array = np.array(embedding, dtype=np.float32)
        
        # Store text separately
        self._texts[text_id] = text
        
        # Prepare metadata, ensuring text_id is always included
        final_metadata = metadata.copy() if metadata else {}
        final_metadata["text_id"] = text_id
        
        # Add vector to storage
        vector_id = await self.storage_provider.add_vector(
            embedding_array,
            final_metadata
        )
        
        # Store mapping between text_id and vector_id
        self._text_to_vector[text_id] = vector_id
        
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
            # The text_id should be in the metadata from the storage provider
            metadata = result.get("metadata", {})
            text_id = metadata.get("text_id")
            
            if text_id and text_id in self._texts:
                result["text"] = self._texts[text_id]
                # Remove text_id from metadata as it's now in the main result
                if "text_id" in metadata:
                    del metadata["text_id"]
            else:
                # Debug: print more information about what's happening
                print(f"Debug: text_id not found in metadata or text not in memory")
                print(f"  Result ID: {result.get('id')}")
                print(f"  Metadata keys: {list(metadata.keys())}")
                print(f"  Metadata: {metadata}")
                print(f"  Available text IDs: {list(self._texts.keys())}")
                print(f"  Text ID from metadata: {text_id}")
                continue
        
        return results
    
    async def get_text(self, text_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve text and its metadata by ID."""
        if text_id not in self._texts:
            return None
        
        # Get vector_id from mapping
        vector_id = self._text_to_vector.get(text_id)
        if not vector_id:
            return None
        
        # Get vector and metadata from storage
        vector_data = await self.storage_provider.get_vector(vector_id)
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
        
        # Get vector_id from mapping
        vector_id = self._text_to_vector.get(text_id)
        if not vector_id:
            return False
        
        # Delete from storage
        success = await self.storage_provider.delete_vector(vector_id)
        if success:
            # Delete text and mapping
            del self._texts[text_id]
            del self._text_to_vector[text_id]
        
        return success 