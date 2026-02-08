"""
Chroma Cloud Connection - Singleton client and collection management
"""

# Import from chromadb package (installed by chromadb-client)
# We'll use direct HTTP client approach to avoid Python 3.14 compatibility issues
import httpx
from typing import Dict, Any, List, Optional
from fastapi import Depends
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Global singleton instances
_client: Optional['ChromaCloudClient'] = None
_collection: Optional['ChromaCollection'] = None


class ChromaCollection:
    """Wrapper for Chroma collection operations."""
    
    def __init__(self, client: 'ChromaCloudClient', name: str):
        self.client = client
        self.name = name
        self.id = None
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure collection exists."""
        # Get or create collection
        response = self.client._request("POST", "/api/v1/collections", {
            "name": self.name,
            "get_or_create": True
        })
        self.id = response.get("id")
    
    def add(self, ids: List[str], embeddings: List[List[float]], 
            documents: List[str], metadatas: List[Dict[str, Any]]):
        """Add items to collection."""
        self.client._request("POST", f"/api/v1/collections/{self.id}/add", {
            "ids": ids,
            "embeddings": embeddings,
            "documents": documents,
            "metadatas": metadatas
        })
    
    def get(self, ids: List[str] = None, where: Dict = None, 
            limit: int = None, include: List[str] = None):
        """Get items from collection."""
        payload = {}
        if ids:
            payload["ids"] = ids
        if where:
            payload["where"] = where
        if limit:
            payload["limit"] = limit
        if include:
            payload["include"] = include
        
        return self.client._request("POST", f"/api/v1/collections/{self.id}/get", payload)
    
    def query(self, query_embeddings: List[List[float]], n_results: int = 10,
              where: Dict = None, include: List[str] = None):
        """Query collection."""
        payload = {
            "query_embeddings": query_embeddings,
            "n_results": n_results
        }
        if where:
            payload["where"] = where
        if include:
            payload["include"] = include
        
        return self.client._request("POST", f"/api/v1/collections/{self.id}/query", payload)
    
    def update(self, ids: List[str], metadatas: List[Dict[str, Any]]):
        """Update items in collection."""
        self.client._request("POST", f"/api/v1/collections/{self.id}/update", {
            "ids": ids,
            "metadatas": metadatas
        })
    
    def delete(self, ids: List[str] = None, where: Dict = None):
        """Delete items from collection."""
        payload = {}
        if ids:
            payload["ids"] = ids
        if where:
            payload["where"] = where
        
        self.client._request("POST", f"/api/v1/collections/{self.id}/delete", payload)


class ChromaCloudClient:
    """Simple HTTP client for Chroma Cloud."""
    
    def __init__(self, api_key: str, tenant: str, database: str):
        self.api_key = api_key
        self.tenant = tenant
        self.database = database
        self.base_url = f"https://api.trychroma.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Chroma-Tenant": tenant,
            "X-Chroma-Database": database,
            "Content-Type": "application/json"
        }
        self.client = httpx.Client(timeout=30.0)
    
    def _request(self, method: str, path: str, data: Dict = None) -> Dict:
        """Make HTTP request to Chroma Cloud."""
        url = f"{self.base_url}{path}"
        
        if method == "GET":
            response = self.client.get(url, headers=self.headers)
        elif method == "POST":
            response = self.client.post(url, headers=self.headers, json=data)
        elif method == "DELETE":
            response = self.client.delete(url, headers=self.headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def list_collections(self) -> List[Dict]:
        """List all collections."""
        return self._request("GET", "/api/v1/collections")
    
    def get_or_create_collection(self, name: str, metadata: Dict = None) -> ChromaCollection:
        """Get or create a collection."""
        return ChromaCollection(self, name)


def get_chroma_client() -> ChromaCloudClient:
    """
    Get or create the Chroma Cloud client singleton.
    
    Returns:
        ChromaCloudClient: Chroma Cloud client instance
    """
    global _client
    if _client is None:
        api_key = os.getenv("CHROMA_API_KEY")
        tenant = os.getenv("CHROMA_TENANT", "733bcc53-ea72-4613-81b9-9f7baa2331a3")
        database = os.getenv("CHROMA_DATABASE", "topfloor")
        
        if not api_key:
            raise ValueError(
                "CHROMA_API_KEY environment variable is required for Chroma Cloud connection"
            )
        
        _client = ChromaCloudClient(
            api_key=api_key,
            tenant=tenant,
            database=database
        )
    
    return _client


def get_chroma_collection(
    client: ChromaCloudClient = Depends(get_chroma_client)
) -> ChromaCollection:
    """
    Get or create the memories collection singleton.
    
    Args:
        client: Chroma Cloud client (injected by FastAPI)
        
    Returns:
        ChromaCollection: Chroma collection for memories
    """
    global _collection
    if _collection is None:
        _collection = client.get_or_create_collection(
            name="memories",
            metadata={"description": "Long-term memory storage for TopFloor AI agents"}
        )
    
    return _collection


def reset_chroma_connection():
    """
    Reset the global client and collection instances.
    Useful for testing or reconnection scenarios.
    """
    global _client, _collection
    _client = None
    _collection = None
