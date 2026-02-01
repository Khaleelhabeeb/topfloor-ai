"""
Artifact Service - Business logic for artifact/file management
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, desc
from app.models.artifact import Artifact
from app.schemas.artifact import ArtifactCreate
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import os
import pathlib


class ArtifactService:
    """Service for managing artifacts with CRUD operations and file management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_artifact(self, user_id: int, artifact_data: ArtifactCreate) -> Artifact:
        """
        Create a new artifact record for a user.
        
        Args:
            user_id: ID of the user who owns the artifact
            artifact_data: Artifact creation data
            
        Returns:
            Created artifact object
            
        Raises:
            ValueError: If artifact creation fails
        """
        # Generate unique artifact_id
        artifact_id = f"artifact_{uuid.uuid4().hex[:16]}"
        
        # Create artifact object
        db_artifact = Artifact(
            artifact_id=artifact_id,
            user_id=user_id,
            task_id=artifact_data.task_id,
            agent_type=artifact_data.agent_type,
            file_name=artifact_data.file_name,
            file_type=artifact_data.file_type,
            file_path=artifact_data.file_path,
            file_size=artifact_data.file_size,
            mime_type=artifact_data.mime_type,
            meta_data=artifact_data.metadata,
        )
        
        self.db.add(db_artifact)
        try:
            self.db.commit()
            self.db.refresh(db_artifact)
            return db_artifact
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create artifact: {str(e)}")
    
    def get_artifact_by_id(self, artifact_id: int, user_id: Optional[int] = None) -> Optional[Artifact]:
        """
        Get an artifact by its database ID.
        
        Args:
            artifact_id: Database ID of the artifact
            user_id: Optional user ID to filter by (for authorization)
            
        Returns:
            Artifact object if found, None otherwise
        """
        query = self.db.query(Artifact).filter(Artifact.id == artifact_id)
        
        if user_id is not None:
            query = query.filter(Artifact.user_id == user_id)
        
        return query.first()
    
    def get_artifact_by_artifact_id(
        self, 
        artifact_id: str, 
        user_id: Optional[int] = None
    ) -> Optional[Artifact]:
        """
        Get an artifact by its unique artifact_id string.
        
        Args:
            artifact_id: Unique artifact_id string
            user_id: Optional user ID to filter by (for authorization)
            
        Returns:
            Artifact object if found, None otherwise
        """
        query = self.db.query(Artifact).filter(Artifact.artifact_id == artifact_id)
        
        if user_id is not None:
            query = query.filter(Artifact.user_id == user_id)
        
        return query.first()

    def get_artifacts(
        self,
        user_id: int,
        agent_type: Optional[str] = None,
        file_type: Optional[str] = None,
        task_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Artifact], int]:
        """
        Get a list of artifacts with optional filtering and pagination.
        
        Args:
            user_id: User ID to filter artifacts
            agent_type: Optional agent type filter
            file_type: Optional file type filter (pdf, docx, png, etc)
            task_id: Optional task ID filter
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of artifacts, total count)
        """
        # Build base query
        query = self.db.query(Artifact).filter(Artifact.user_id == user_id)
        
        # Apply filters
        if agent_type is not None:
            query = query.filter(Artifact.agent_type == agent_type)
        
        if file_type is not None:
            query = query.filter(Artifact.file_type == file_type)
        
        if task_id is not None:
            query = query.filter(Artifact.task_id == task_id)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering (most recent first)
        artifacts = query.order_by(desc(Artifact.created_at)).offset(skip).limit(limit).all()
        
        return artifacts, total
    
    def delete_artifact(self, artifact_id: int, user_id: int) -> bool:
        """
        Delete an artifact record from the database.
        Note: This does not delete the physical file, use delete_artifact_with_file for that.
        
        Args:
            artifact_id: Database ID of the artifact
            user_id: User ID (for authorization)
            
        Returns:
            True if artifact was deleted, False if not found
        """
        artifact = self.get_artifact_by_id(artifact_id, user_id)
        
        if artifact is None:
            return False
        
        self.db.delete(artifact)
        self.db.commit()
        
        return True
    
    def delete_artifact_with_file(
        self, 
        artifact_id: int, 
        user_id: int,
        storage_base_path: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Delete an artifact record and its associated physical file.
        
        Args:
            artifact_id: Database ID of the artifact
            user_id: User ID (for authorization)
            storage_base_path: Optional base path for file storage (defaults to current directory)
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        artifact = self.get_artifact_by_id(artifact_id, user_id)
        
        if artifact is None:
            return False, "Artifact not found"
        
        # Try to delete physical file
        file_deleted = False
        error_message = None
        
        try:
            file_path = artifact.file_path
            
            # If storage_base_path is provided and file_path is relative, join them
            if storage_base_path and not os.path.isabs(file_path):
                file_path = os.path.join(storage_base_path, file_path)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                file_deleted = True
            else:
                error_message = f"Physical file not found at {file_path}"
        except Exception as e:
            error_message = f"Failed to delete physical file: {str(e)}"
        
        # Delete database record regardless of file deletion success
        self.db.delete(artifact)
        self.db.commit()
        
        return True, error_message
    
    def get_artifacts_by_task(
        self, 
        task_id: int, 
        user_id: int
    ) -> List[Artifact]:
        """
        Get all artifacts associated with a specific task.
        
        Args:
            task_id: Task ID to filter by
            user_id: User ID (for authorization)
            
        Returns:
            List of artifacts for the task
        """
        return self.db.query(Artifact).filter(
            and_(
                Artifact.task_id == task_id,
                Artifact.user_id == user_id
            )
        ).order_by(desc(Artifact.created_at)).all()
    
    def get_artifacts_by_agent(
        self,
        user_id: int,
        agent_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Artifact], int]:
        """
        Get artifacts for a specific agent (convenience method).
        
        Args:
            user_id: User ID to filter artifacts
            agent_type: Agent type to filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of artifacts, total count)
        """
        return self.get_artifacts(
            user_id=user_id,
            agent_type=agent_type,
            skip=skip,
            limit=limit
        )
    
    def count_artifacts_by_type(
        self,
        user_id: int,
        agent_type: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Count artifacts by file type for a user.
        
        Args:
            user_id: User ID to filter artifacts
            agent_type: Optional agent type filter
            
        Returns:
            Dictionary mapping file type to count
        """
        query = self.db.query(Artifact).filter(Artifact.user_id == user_id)
        
        if agent_type is not None:
            query = query.filter(Artifact.agent_type == agent_type)
        
        artifacts = query.all()
        
        counts: Dict[str, int] = {}
        for artifact in artifacts:
            file_type = artifact.file_type
            counts[file_type] = counts.get(file_type, 0) + 1
        
        return counts
    
    def get_total_storage_size(
        self,
        user_id: int,
        agent_type: Optional[str] = None
    ) -> int:
        """
        Calculate total storage size used by a user's artifacts.
        
        Args:
            user_id: User ID to filter artifacts
            agent_type: Optional agent type filter
            
        Returns:
            Total size in bytes
        """
        query = self.db.query(Artifact).filter(Artifact.user_id == user_id)
        
        if agent_type is not None:
            query = query.filter(Artifact.agent_type == agent_type)
        
        artifacts = query.all()
        
        return sum(artifact.file_size for artifact in artifacts)
    
    def search_artifacts(
        self,
        user_id: int,
        search_term: str,
        agent_type: Optional[str] = None,
        file_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Artifact], int]:
        """
        Search artifacts by file name.
        
        Args:
            user_id: User ID to filter artifacts
            search_term: Search term to match against file names
            agent_type: Optional agent type filter
            file_type: Optional file type filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of artifacts, total count)
        """
        query = self.db.query(Artifact).filter(
            and_(
                Artifact.user_id == user_id,
                Artifact.file_name.ilike(f"%{search_term}%")
            )
        )
        
        if agent_type is not None:
            query = query.filter(Artifact.agent_type == agent_type)
        
        if file_type is not None:
            query = query.filter(Artifact.file_type == file_type)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        artifacts = query.order_by(desc(Artifact.created_at)).offset(skip).limit(limit).all()
        
        return artifacts, total
    
    def get_recent_artifacts(
        self,
        user_id: int,
        limit: int = 10,
        agent_type: Optional[str] = None
    ) -> List[Artifact]:
        """
        Get the most recent artifacts for a user.
        
        Args:
            user_id: User ID to filter artifacts
            limit: Maximum number of artifacts to return
            agent_type: Optional agent type filter
            
        Returns:
            List of recent artifacts
        """
        query = self.db.query(Artifact).filter(Artifact.user_id == user_id)
        
        if agent_type is not None:
            query = query.filter(Artifact.agent_type == agent_type)
        
        return query.order_by(desc(Artifact.created_at)).limit(limit).all()
    
    def verify_file_exists(self, artifact_id: int, user_id: int) -> tuple[bool, Optional[str]]:
        """
        Verify that the physical file for an artifact exists.
        
        Args:
            artifact_id: Database ID of the artifact
            user_id: User ID (for authorization)
            
        Returns:
            Tuple of (exists: bool, file_path: Optional[str])
        """
        artifact = self.get_artifact_by_id(artifact_id, user_id)
        
        if artifact is None:
            return False, None
        
        file_path = artifact.file_path
        exists = os.path.exists(file_path)
        
        return exists, file_path if exists else None
    
    def bulk_delete_artifacts(
        self,
        artifact_ids: List[int],
        user_id: int,
        delete_files: bool = False,
        storage_base_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete multiple artifacts at once.
        
        Args:
            artifact_ids: List of artifact database IDs to delete
            user_id: User ID (for authorization)
            delete_files: Whether to also delete physical files
            storage_base_path: Optional base path for file storage
            
        Returns:
            Dictionary with deletion results
        """
        results = {
            "deleted_count": 0,
            "failed_count": 0,
            "errors": []
        }
        
        for artifact_id in artifact_ids:
            try:
                if delete_files:
                    success, error = self.delete_artifact_with_file(
                        artifact_id, user_id, storage_base_path
                    )
                    if success:
                        results["deleted_count"] += 1
                        if error:
                            results["errors"].append({
                                "artifact_id": artifact_id,
                                "error": error
                            })
                    else:
                        results["failed_count"] += 1
                        results["errors"].append({
                            "artifact_id": artifact_id,
                            "error": error or "Unknown error"
                        })
                else:
                    success = self.delete_artifact(artifact_id, user_id)
                    if success:
                        results["deleted_count"] += 1
                    else:
                        results["failed_count"] += 1
                        results["errors"].append({
                            "artifact_id": artifact_id,
                            "error": "Artifact not found"
                        })
            except Exception as e:
                results["failed_count"] += 1
                results["errors"].append({
                    "artifact_id": artifact_id,
                    "error": str(e)
                })
        
        return results
