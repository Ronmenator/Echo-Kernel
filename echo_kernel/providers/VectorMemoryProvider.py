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
        # Create a new dictionary to avoid modifying the original
        final_metadata = {}
        if metadata:
            final_metadata.update(metadata)
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
        valid_results = []
        for result in results:
            # The text_id should be in the metadata from the storage provider
            metadata = result.get("metadata", {})
            text_id = metadata.get("text_id")
            
            if text_id and text_id in self._texts:
                result["text"] = self._texts[text_id]
                # Create a copy of metadata without text_id for the result
                result_metadata = metadata.copy()
                if "text_id" in result_metadata:
                    del result_metadata["text_id"]
                result["metadata"] = result_metadata
                valid_results.append(result)
            else:
                # Skip this result as it's not properly linked to text
                continue
        
        return valid_results
    
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
    
    async def debug_memory_state(self) -> Dict[str, Any]:
        """Debug method to check the state of memory and identify any inconsistencies."""
        debug_info = {
            "texts_count": len(self._texts),
            "text_to_vector_count": len(self._text_to_vector),
            "text_ids": list(self._texts.keys()),
            "vector_ids": list(self._text_to_vector.values()),
            "orphaned_vectors": []
        }
        
        # Check for orphaned vectors (vectors in storage but not in text mapping)
        for text_id, vector_id in self._text_to_vector.items():
            vector_data = await self.storage_provider.get_vector(vector_id)
            if vector_data is None:
                debug_info["orphaned_vectors"].append({
                    "text_id": text_id,
                    "vector_id": vector_id,
                    "issue": "Vector not found in storage"
                })
            else:
                metadata = vector_data.get("metadata", {})
                stored_text_id = metadata.get("text_id")
                if stored_text_id != text_id:
                    debug_info["orphaned_vectors"].append({
                        "text_id": text_id,
                        "vector_id": vector_id,
                        "stored_text_id": stored_text_id,
                        "issue": "Text ID mismatch"
                    })
        
        return debug_info
    
    async def cleanup_orphaned_vectors(self) -> int:
        """Clean up orphaned vectors that exist in storage but not in the text mapping.
        
        Returns:
            Number of orphaned vectors cleaned up
        """
        debug_info = await self.debug_memory_state()
        orphaned_count = 0
        
        for orphaned in debug_info["orphaned_vectors"]:
            vector_id = orphaned["vector_id"]
            # Delete the orphaned vector from storage
            success = await self.storage_provider.delete_vector(vector_id)
            if success:
                orphaned_count += 1
        
        return orphaned_count
    
    async def clear_memory(self) -> None:
        """Clear all stored texts and vectors from memory."""
        # Clear text storage
        self._texts.clear()
        self._text_to_vector.clear()
        
        # Reset storage provider
        if hasattr(self.storage_provider, 'reset'):
            await self.storage_provider.reset()
        
        print("Memory cleared successfully.") 