"""
Memory Service - Long-term memory storage and retrieval using Chroma Cloud
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from app.core.config import settings
from app.services.embedding_service import get_embedding_service
from app.services.chroma_connection import get_chroma_client, ChromaCollection


class Memory:
    """Represents a single memory entry."""
    
    def __init__(
        self,
        id: str,
        content: str,
        user_id: int,
        agent_type: str,
        importance: float,
        memory_type: str,
        tags: List[str],
        created_at: str,
        last_accessed: str,
        access_count: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.content = content
        self.user_id = user_id
        self.agent_type = agent_type
        self.importance = importance
        self.memory_type = memory_type
        self.tags = tags
        self.created_at = created_at
        self.last_accessed = last_accessed
        self.access_count = access_count
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "user_id": self.user_id,
            "agent_type": self.agent_type,
            "importance": self.importance,
            "memory_type": self.memory_type,
            "tags": self.tags,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "metadata": self.metadata
        }


class MemoryService:
    """
    Service for managing long-term memory using Chroma Cloud.
    Provides semantic search and memory management capabilities.
    """

    def __init__(self):
        """
        Initialize the memory service with Chroma Cloud.
        """
        self.embedding_service = get_embedding_service()

        # Get Chroma Cloud client and collection
        self.client = get_chroma_client()
        self.collection: ChromaCollection = self.client.get_or_create_collection(
            name="memories",
            metadata={"description": "Long-term memory storage for TopFloor AI agents"}
        )

    def store(
        self,
        user_id: int,
        agent_type: str,
        content: str,
        importance: float = 0.5,
        memory_type: str = "fact",
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Store a new memory.

        Args:
            user_id: ID of the user this memory belongs to
            agent_type: Type of agent (finance, data_analyst, researcher, team_lead)
            content: The memory content/text
            importance: Importance score 0-1 (higher = more important)
            memory_type: Type of memory (preference, fact, decision, summary)
            tags: Optional list of tags for categorization

        Returns:
            Memory ID
        """
        # Generate unique ID
        memory_id = f"mem_{uuid.uuid4().hex}"

        # Generate embedding
        embedding = self.embedding_service.embed(content)

        # Prepare metadata
        now = datetime.utcnow().isoformat()
        metadata = {
            "user_id": user_id,
            "agent_type": agent_type,
            "importance": importance,
            "memory_type": memory_type,
            "tags": ",".join(tags or []),
            "created_at": now,
            "last_accessed": now,
            "access_count": 0
        }

        # Store in ChromaDB
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )

        return memory_id

    def retrieve(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: ID of the memory to retrieve

        Returns:
            Memory object or None if not found
        """
        try:
            result = self.collection.get(
                ids=[memory_id],
                include=["documents", "metadatas"]
            )

            if not result["ids"]:
                return None

            # Update access metadata
            self._update_access(memory_id)

            # Parse metadata
            metadata = result["metadatas"][0]

            return Memory(
                id=result["ids"][0],
                content=result["documents"][0],
                user_id=int(metadata["user_id"]),
                agent_type=metadata["agent_type"],
                importance=float(metadata["importance"]),
                memory_type=metadata["memory_type"],
                tags=metadata["tags"].split(",") if metadata["tags"] else [],
                created_at=metadata["created_at"],
                last_accessed=metadata["last_accessed"],
                access_count=int(metadata["access_count"])
            )
        except Exception:
            return None

    def search(
        self,
        query: str,
        user_id: int,
        agent_type: Optional[str] = None,
        limit: int = 5,
        min_importance: float = 0.0
    ) -> List[Memory]:
        """
        Search for relevant memories using semantic similarity.

        Args:
            query: Search query text
            user_id: User ID to filter memories
            agent_type: Optional agent type to filter by
            limit: Maximum number of results to return
            min_importance: Minimum importance score to include

        Returns:
            List of relevant Memory objects, sorted by relevance
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed(query)

        # Build where filter
        where_filter = {
            "user_id": user_id,
            "importance": {"$gte": min_importance}
        }

        if agent_type:
            where_filter["agent_type"] = agent_type

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        # Convert to Memory objects
        memories = []
        for i in range(len(results["ids"][0])):
            memory_id = results["ids"][0][i]
            metadata = results["metadatas"][0][i]

            memory = Memory(
                id=memory_id,
                content=results["documents"][0][i],
                user_id=int(metadata["user_id"]),
                agent_type=metadata["agent_type"],
                importance=float(metadata["importance"]),
                memory_type=metadata["memory_type"],
                tags=metadata["tags"].split(",") if metadata["tags"] else [],
                created_at=metadata["created_at"],
                last_accessed=metadata["last_accessed"],
                access_count=int(metadata["access_count"]),
                metadata={"distance": results["distances"][0][i]}
            )
            memories.append(memory)

            # Update access count
            self._update_access(memory_id)

        return memories

    def delete(self, memory_id: str) -> bool:
        """
        Delete a specific memory.

        Args:
            memory_id: ID of the memory to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

    def delete_user_memories(
        self,
        user_id: int,
        agent_type: Optional[str] = None
    ) -> int:
        """
        Delete all memories for a user (or specific agent).

        Args:
            user_id: User ID whose memories to delete
            agent_type: Optional agent type to filter deletion

        Returns:
            Number of memories deleted
        """
        where_filter = {"user_id": user_id}
        if agent_type:
            where_filter["agent_type"] = agent_type

        try:
            # Get all matching memories
            results = self.collection.get(
                where=where_filter,
                include=[]
            )

            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                return len(results["ids"])

            return 0
        except Exception:
            return 0

    def prune_old_memories(
        self,
        user_id: int,
        days_old: int = 30,
        min_importance: float = 0.3,
        max_access_count: int = 2
    ) -> int:
        """
        Prune old, low-importance, rarely accessed memories.

        Args:
            user_id: User ID whose memories to prune
            days_old: Delete memories older than this many days
            min_importance: Delete memories with importance below this
            max_access_count: Delete memories accessed fewer times than this

        Returns:
            Number of memories pruned
        """
        cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()

        try:
            # Get all user memories
            results = self.collection.get(
                where={"user_id": user_id},
                include=["metadatas"]
            )

            if not results["ids"]:
                return 0

            # Filter memories to prune
            ids_to_delete = []
            for i, memory_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i]

                # Check pruning criteria
                is_old = metadata["created_at"] < cutoff_date
                is_low_importance = float(metadata["importance"]) < min_importance
                is_rarely_accessed = int(metadata["access_count"]) < max_access_count

                if is_old and is_low_importance and is_rarely_accessed:
                    ids_to_delete.append(memory_id)

            # Delete matching memories
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)

            return len(ids_to_delete)
        except Exception:
            return 0

    def prune_by_importance(
        self,
        user_id: int,
        keep_top_n: int = 100
    ) -> int:
        """
        Keep only the top N most important memories for a user.

        Args:
            user_id: User ID whose memories to prune
            keep_top_n: Number of top memories to keep

        Returns:
            Number of memories pruned
        """
        try:
            # Get all user memories
            results = self.collection.get(
                where={"user_id": user_id},
                include=["metadatas"]
            )

            if not results["ids"] or len(results["ids"]) <= keep_top_n:
                return 0

            # Sort by importance (descending)
            memories_with_importance = [
                (results["ids"][i], float(results["metadatas"][i]["importance"]))
                for i in range(len(results["ids"]))
            ]
            memories_with_importance.sort(key=lambda x: x[1], reverse=True)

            # Get IDs to delete (everything after top N)
            ids_to_delete = [m[0] for m in memories_with_importance[keep_top_n:]]

            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)

            return len(ids_to_delete)
        except Exception:
            return 0

    def list_memories(
        self,
        user_id: int,
        agent_type: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Memory]:
        """
        List memories for a user with optional filters.

        Args:
            user_id: User ID whose memories to list
            agent_type: Optional agent type filter
            memory_type: Optional memory type filter
            limit: Maximum number of memories to return

        Returns:
            List of Memory objects
        """
        where_filter = {"user_id": user_id}
        if agent_type:
            where_filter["agent_type"] = agent_type
        if memory_type:
            where_filter["memory_type"] = memory_type

        try:
            results = self.collection.get(
                where=where_filter,
                limit=limit,
                include=["documents", "metadatas"]
            )

            if not results["ids"]:
                return []

            memories = []
            for i in range(len(results["ids"])):
                metadata = results["metadatas"][i]
                memory = Memory(
                    id=results["ids"][i],
                    content=results["documents"][i],
                    user_id=int(metadata["user_id"]),
                    agent_type=metadata["agent_type"],
                    importance=float(metadata["importance"]),
                    memory_type=metadata["memory_type"],
                    tags=metadata["tags"].split(",") if metadata["tags"] else [],
                    created_at=metadata["created_at"],
                    last_accessed=metadata["last_accessed"],
                    access_count=int(metadata["access_count"])
                )
                memories.append(memory)

            return memories
        except Exception:
            return []

    def _update_access(self, memory_id: str) -> None:
        """
        Update access metadata for a memory.

        Args:
            memory_id: ID of the memory to update
        """
        try:
            # Get current metadata
            result = self.collection.get(
                ids=[memory_id],
                include=["metadatas", "documents", "embeddings"]
            )

            if not result["ids"]:
                return

            # Update metadata
            metadata = result["metadatas"][0]
            metadata["last_accessed"] = datetime.utcnow().isoformat()
            metadata["access_count"] = int(metadata["access_count"]) + 1

            # Update in ChromaDB (delete and re-add with updated metadata)
            self.collection.update(
                ids=[memory_id],
                metadatas=[metadata]
            )
        except Exception:
            pass  # Silently fail on access update

    def get_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get memory statistics for a user.

        Args:
            user_id: User ID to get stats for

        Returns:
            Dictionary with memory statistics
        """
        try:
            results = self.collection.get(
                where={"user_id": user_id},
                include=["metadatas"]
            )

            if not results["ids"]:
                return {
                    "total_memories": 0,
                    "by_agent": {},
                    "by_type": {},
                    "avg_importance": 0.0
                }

            # Calculate stats
            by_agent = {}
            by_type = {}
            total_importance = 0.0

            for metadata in results["metadatas"]:
                agent = metadata["agent_type"]
                mem_type = metadata["memory_type"]
                importance = float(metadata["importance"])

                by_agent[agent] = by_agent.get(agent, 0) + 1
                by_type[mem_type] = by_type.get(mem_type, 0) + 1
                total_importance += importance

            return {
                "total_memories": len(results["ids"]),
                "by_agent": by_agent,
                "by_type": by_type,
                "avg_importance": total_importance / len(results["ids"]) if results["ids"] else 0.0
            }
        except Exception:
            return {
                "total_memories": 0,
                "by_agent": {},
                "by_type": {},
                "avg_importance": 0.0
            }


class NullMemoryService:
    """Fallback memory service when memory is disabled or unavailable."""

    def store(
        self,
        user_id: int,
        agent_type: str,
        content: str,
        importance: float = 0.5,
        memory_type: str = "fact",
        tags: Optional[List[str]] = None
    ) -> str:
        return f"mem_disabled_{uuid.uuid4().hex}"

    def retrieve(self, memory_id: str) -> Optional[Memory]:
        return None

    def search(
        self,
        query: str,
        user_id: int,
        agent_type: Optional[str] = None,
        limit: int = 5,
        min_importance: float = 0.0
    ) -> List[Memory]:
        return []

    def delete(self, memory_id: str) -> bool:
        return False

    def delete_user_memories(
        self,
        user_id: int,
        agent_type: Optional[str] = None
    ) -> int:
        return 0

    def prune_old_memories(
        self,
        user_id: int,
        days_old: int = 30,
        min_importance: float = 0.3,
        max_access_count: int = 2
    ) -> int:
        return 0

    def prune_by_importance(self, user_id: int, keep_top_n: int = 100) -> int:
        return 0

    def list_memories(
        self,
        user_id: int,
        agent_type: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Memory]:
        return []

    def get_stats(self, user_id: int) -> Dict[str, Any]:
        return {
            "total_memories": 0,
            "by_agent": {},
            "by_type": {},
            "avg_importance": 0.0
        }


# Global singleton instance
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """
    Get the global memory service instance.
    
    Returns:
        MemoryService singleton
    """
    global _memory_service
    if _memory_service is None:
        if not settings.MEMORY_ENABLED or not settings.CHROMA_API_KEY:
            _memory_service = NullMemoryService()
        else:
            try:
                _memory_service = MemoryService()
            except Exception:
                _memory_service = NullMemoryService()
    return _memory_service
