from typing import Dict, Any, List, Optional
import uuid
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from ..IStorageProvider import IStorageProvider

class QdrantStorageProvider(IStorageProvider):
    def __init__(self, url: str, collection_name: str = "vectors", api_key: Optional[str] = None):
        """Initialize the Qdrant storage provider.
        
        Args:
            url: Qdrant server URL
            collection_name: Name of the collection to use
            api_key: Optional API key for authentication
        """
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self._initialized = False
    
    async def initialize(self, dimension: int) -> None:
        """Initialize the Qdrant collection with the given dimension."""
        if not self._initialized:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=dimension,
                        distance=models.Distance.COSINE
                    )
                )
            self._initialized = True
    
    async def add_vector(self, vector: np.ndarray, metadata: Dict[str, Any]) -> str:
        """Add a vector to Qdrant and store its metadata."""
        if not self._initialized:
            await self.initialize(vector.shape[0])
        
        vector_id = str(uuid.uuid4())
        
        # Add vector to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=vector_id,
                    vector=vector.tolist(),
                    payload=metadata
                )
            ]
        )
        
        return vector_id
    
    async def search_vectors(self, query_vector: np.ndarray, limit: int) -> List[Dict[str, Any]]:
        """Search for similar vectors using Qdrant."""
        if not self._initialized:
            return []
        
        # Search using Qdrant
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=limit
        )
        
        # Convert results to the expected format
        results = []
        for scored_point in search_result:
            results.append({
                "id": scored_point.id,
                "metadata": scored_point.payload,
                "similarity": float(scored_point.score)
            })
        
        return results
    
    async def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a vector and its metadata by ID."""
        if not self._initialized:
            return None
        
        try:
            point = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[vector_id]
            )[0]
            
            return {
                "id": point.id,
                "vector": np.array(point.vector),
                "metadata": point.payload
            }
        except Exception:
            return None
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from Qdrant."""
        if not self._initialized:
            return False
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[vector_id]
                )
            )
            return True
        except Exception:
            return False 