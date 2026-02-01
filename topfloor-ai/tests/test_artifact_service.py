"""
Tests for Artifact Service
"""

import pytest
from sqlalchemy.orm import Session
from app.services.artifact_service import ArtifactService
from app.schemas.artifact import ArtifactCreate
from app.models.artifact import Artifact
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
import os
import tempfile


@pytest.fixture
def artifact_service(db_session: Session):
    """Create an ArtifactService instance."""
    return ArtifactService(db_session)


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user = User(email="test@example.com", password_hash="hashed_password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_task(db_session: Session, test_user: User):
    """Create a test task."""
    task = Task(
        task_id="task_123",
        user_id=test_user.id,
        agent_type="finance",
        title="Test Task",
        description="Test task description",
        task_type=TaskType.BACKGROUND,
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


class TestArtifactServiceCreate:
    """Tests for creating artifacts."""
    
    def test_create_artifact_minimal(self, artifact_service: ArtifactService, test_user: User):
        """Test creating an artifact with minimal data."""
        artifact_data = ArtifactCreate(
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/storage/report.pdf",
            file_size=1024
        )
        
        artifact = artifact_service.create_artifact(test_user.id, artifact_data)
        
        assert artifact.id is not None
        assert artifact.artifact_id.startswith("artifact_")
        assert artifact.user_id == test_user.id
        assert artifact.agent_type == "finance"
        assert artifact.file_name == "report.pdf"
        assert artifact.file_type == "pdf"
        assert artifact.file_path == "/storage/report.pdf"
        assert artifact.file_size == 1024
        assert artifact.task_id is None
        assert artifact.mime_type is None
        assert artifact.meta_data is None
        assert artifact.created_at is not None
    
    def test_create_artifact_full(
        self, 
        artifact_service: ArtifactService, 
        test_user: User,
        test_task: Task
    ):
        """Test creating an artifact with all data."""
        artifact_data = ArtifactCreate(
            task_id=test_task.id,
            agent_type="data_analyst",
            file_name="analysis.docx",
            file_type="docx",
            file_path="/storage/analysis.docx",
            file_size=2048,
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            metadata={"pages": 10, "author": "Data Analyst"}
        )
        
        artifact = artifact_service.create_artifact(test_user.id, artifact_data)
        
        assert artifact.task_id == test_task.id
        assert artifact.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert artifact.meta_data == {"pages": 10, "author": "Data Analyst"}
    
    def test_create_multiple_artifacts(self, artifact_service: ArtifactService, test_user: User):
        """Test creating multiple artifacts."""
        for i in range(3):
            artifact_data = ArtifactCreate(
                agent_type="finance",
                file_name=f"report_{i}.pdf",
                file_type="pdf",
                file_path=f"/storage/report_{i}.pdf",
                file_size=1024 * (i + 1)
            )
            artifact = artifact_service.create_artifact(test_user.id, artifact_data)
            assert artifact.id is not None
            assert artifact.file_name == f"report_{i}.pdf"


class TestArtifactServiceGet:
    """Tests for retrieving artifacts."""
    
    def test_get_artifact_by_id(self, artifact_service: ArtifactService, test_user: User):
        """Test getting an artifact by database ID."""
        artifact_data = ArtifactCreate(
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/storage/report.pdf",
            file_size=1024
        )
        created = artifact_service.create_artifact(test_user.id, artifact_data)
        
        retrieved = artifact_service.get_artifact_by_id(created.id, test_user.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.artifact_id == created.artifact_id
        assert retrieved.file_name == "report.pdf"
    
    def test_get_artifact_by_id_not_found(self, artifact_service: ArtifactService, test_user: User):
        """Test getting a non-existent artifact."""
        retrieved = artifact_service.get_artifact_by_id(99999, test_user.id)
        assert retrieved is None
    
    def test_get_artifact_by_id_wrong_user(
        self, 
        artifact_service: ArtifactService, 
        test_user: User,
        db_session: Session
    ):
        """Test that users cannot access other users' artifacts."""
        # Create another user
        other_user = User(email="other@example.com", password_hash="hashed")
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        # Create artifact for test_user
        artifact_data = ArtifactCreate(
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/storage/report.pdf",
            file_size=1024
        )
        created = artifact_service.create_artifact(test_user.id, artifact_data)
        
        # Try to get with other_user's ID
        retrieved = artifact_service.get_artifact_by_id(created.id, other_user.id)
        assert retrieved is None
    
    def test_get_artifact_by_artifact_id(self, artifact_service: ArtifactService, test_user: User):
        """Test getting an artifact by artifact_id string."""
        artifact_data = ArtifactCreate(
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/storage/report.pdf",
            file_size=1024
        )
        created = artifact_service.create_artifact(test_user.id, artifact_data)
        
        retrieved = artifact_service.get_artifact_by_artifact_id(created.artifact_id, test_user.id)
        
        assert retrieved is not None
        assert retrieved.artifact_id == created.artifact_id
        assert retrieved.file_name == "report.pdf"


class TestArtifactServiceList:
    """Tests for listing artifacts."""
    
    def test_get_artifacts_empty(self, artifact_service: ArtifactService, test_user: User):
        """Test getting artifacts when none exist."""
        artifacts, total = artifact_service.get_artifacts(test_user.id)
        assert len(artifacts) == 0
        assert total == 0
    
    def test_get_artifacts_pagination(self, artifact_service: ArtifactService, test_user: User):
        """Test pagination of artifacts."""
        # Create 5 artifacts
        for i in range(5):
            artifact_data = ArtifactCreate(
                agent_type="finance",
                file_name=f"report_{i}.pdf",
                file_type="pdf",
                file_path=f"/storage/report_{i}.pdf",
                file_size=1024
            )
            artifact_service.create_artifact(test_user.id, artifact_data)
        
        # Get first page (2 items)
        artifacts, total = artifact_service.get_artifacts(test_user.id, skip=0, limit=2)
        assert len(artifacts) == 2
        assert total == 5
        
        # Get second page (2 items)
        artifacts, total = artifact_service.get_artifacts(test_user.id, skip=2, limit=2)
        assert len(artifacts) == 2
        assert total == 5
        
        # Get third page (1 item)
        artifacts, total = artifact_service.get_artifacts(test_user.id, skip=4, limit=2)
        assert len(artifacts) == 1
        assert total == 5
    
    def test_get_artifacts_filter_by_agent_type(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test filtering artifacts by agent type."""
        # Create artifacts for different agents
        for agent in ["finance", "data_analyst", "researcher"]:
            artifact_data = ArtifactCreate(
                agent_type=agent,
                file_name=f"{agent}_report.pdf",
                file_type="pdf",
                file_path=f"/storage/{agent}_report.pdf",
                file_size=1024
            )
            artifact_service.create_artifact(test_user.id, artifact_data)
        
        # Filter by finance
        artifacts, total = artifact_service.get_artifacts(test_user.id, agent_type="finance")
        assert len(artifacts) == 1
        assert total == 1
        assert artifacts[0].agent_type == "finance"
    
    def test_get_artifacts_filter_by_file_type(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test filtering artifacts by file type."""
        # Create artifacts with different file types
        for file_type in ["pdf", "docx", "png"]:
            artifact_data = ArtifactCreate(
                agent_type="finance",
                file_name=f"file.{file_type}",
                file_type=file_type,
                file_path=f"/storage/file.{file_type}",
                file_size=1024
            )
            artifact_service.create_artifact(test_user.id, artifact_data)
        
        # Filter by pdf
        artifacts, total = artifact_service.get_artifacts(test_user.id, file_type="pdf")
        assert len(artifacts) == 1
        assert total == 1
        assert artifacts[0].file_type == "pdf"
    
    def test_get_artifacts_filter_by_task(
        self, 
        artifact_service: ArtifactService, 
        test_user: User,
        test_task: Task
    ):
        """Test filtering artifacts by task ID."""
        # Create artifact with task
        artifact_data = ArtifactCreate(
            task_id=test_task.id,
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/storage/report.pdf",
            file_size=1024
        )
        artifact_service.create_artifact(test_user.id, artifact_data)
        
        # Create artifact without task
        artifact_data2 = ArtifactCreate(
            agent_type="finance",
            file_name="other.pdf",
            file_type="pdf",
            file_path="/storage/other.pdf",
            file_size=1024
        )
        artifact_service.create_artifact(test_user.id, artifact_data2)
        
        # Filter by task
        artifacts, total = artifact_service.get_artifacts(test_user.id, task_id=test_task.id)
        assert len(artifacts) == 1
        assert total == 1
        assert artifacts[0].task_id == test_task.id


class TestArtifactServiceDelete:
    """Tests for deleting artifacts."""
    
    def test_delete_artifact(self, artifact_service: ArtifactService, test_user: User):
        """Test deleting an artifact."""
        artifact_data = ArtifactCreate(
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/storage/report.pdf",
            file_size=1024
        )
        created = artifact_service.create_artifact(test_user.id, artifact_data)
        
        # Delete artifact
        success = artifact_service.delete_artifact(created.id, test_user.id)
        assert success is True
        
        # Verify it's gone
        retrieved = artifact_service.get_artifact_by_id(created.id, test_user.id)
        assert retrieved is None
    
    def test_delete_artifact_not_found(self, artifact_service: ArtifactService, test_user: User):
        """Test deleting a non-existent artifact."""
        success = artifact_service.delete_artifact(99999, test_user.id)
        assert success is False
    
    def test_delete_artifact_with_file(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test deleting an artifact with its physical file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(b"test content")
            file_path = tmp_file.name
        
        try:
            # Create artifact
            artifact_data = ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="pdf",
                file_path=file_path,
                file_size=12
            )
            created = artifact_service.create_artifact(test_user.id, artifact_data)
            
            # Verify file exists
            assert os.path.exists(file_path)
            
            # Delete artifact with file
            success, error = artifact_service.delete_artifact_with_file(created.id, test_user.id)
            assert success is True
            assert error is None
            
            # Verify file is deleted
            assert not os.path.exists(file_path)
            
            # Verify artifact is deleted
            retrieved = artifact_service.get_artifact_by_id(created.id, test_user.id)
            assert retrieved is None
        finally:
            # Cleanup in case test fails
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_delete_artifact_with_missing_file(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test deleting an artifact when physical file doesn't exist."""
        artifact_data = ArtifactCreate(
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/nonexistent/report.pdf",
            file_size=1024
        )
        created = artifact_service.create_artifact(test_user.id, artifact_data)
        
        # Delete artifact with file (file doesn't exist)
        success, error = artifact_service.delete_artifact_with_file(created.id, test_user.id)
        assert success is True
        assert error is not None
        assert "not found" in error.lower()
        
        # Verify artifact is still deleted from database
        retrieved = artifact_service.get_artifact_by_id(created.id, test_user.id)
        assert retrieved is None


class TestArtifactServiceUtility:
    """Tests for utility methods."""
    
    def test_get_artifacts_by_task(
        self, 
        artifact_service: ArtifactService, 
        test_user: User,
        test_task: Task
    ):
        """Test getting all artifacts for a task."""
        # Create multiple artifacts for the task
        for i in range(3):
            artifact_data = ArtifactCreate(
                task_id=test_task.id,
                agent_type="finance",
                file_name=f"report_{i}.pdf",
                file_type="pdf",
                file_path=f"/storage/report_{i}.pdf",
                file_size=1024
            )
            artifact_service.create_artifact(test_user.id, artifact_data)
        
        artifacts = artifact_service.get_artifacts_by_task(test_task.id, test_user.id)
        assert len(artifacts) == 3
        for artifact in artifacts:
            assert artifact.task_id == test_task.id
    
    def test_get_artifacts_by_agent(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test getting artifacts for a specific agent."""
        # Create artifacts for finance agent
        for i in range(2):
            artifact_data = ArtifactCreate(
                agent_type="finance",
                file_name=f"report_{i}.pdf",
                file_type="pdf",
                file_path=f"/storage/report_{i}.pdf",
                file_size=1024
            )
            artifact_service.create_artifact(test_user.id, artifact_data)
        
        artifacts, total = artifact_service.get_artifacts_by_agent(test_user.id, "finance")
        assert len(artifacts) == 2
        assert total == 2
    
    def test_count_artifacts_by_type(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test counting artifacts by file type."""
        # Create artifacts with different types
        types_count = {"pdf": 3, "docx": 2, "png": 1}
        for file_type, count in types_count.items():
            for i in range(count):
                artifact_data = ArtifactCreate(
                    agent_type="finance",
                    file_name=f"file_{i}.{file_type}",
                    file_type=file_type,
                    file_path=f"/storage/file_{i}.{file_type}",
                    file_size=1024
                )
                artifact_service.create_artifact(test_user.id, artifact_data)
        
        counts = artifact_service.count_artifacts_by_type(test_user.id)
        assert counts["pdf"] == 3
        assert counts["docx"] == 2
        assert counts["png"] == 1
    
    def test_get_total_storage_size(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test calculating total storage size."""
        # Create artifacts with different sizes
        sizes = [1024, 2048, 4096]
        for i, size in enumerate(sizes):
            artifact_data = ArtifactCreate(
                agent_type="finance",
                file_name=f"file_{i}.pdf",
                file_type="pdf",
                file_path=f"/storage/file_{i}.pdf",
                file_size=size
            )
            artifact_service.create_artifact(test_user.id, artifact_data)
        
        total_size = artifact_service.get_total_storage_size(test_user.id)
        assert total_size == sum(sizes)
    
    def test_search_artifacts(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test searching artifacts by file name."""
        # Create artifacts with different names
        names = ["financial_report.pdf", "budget_analysis.docx", "market_report.pdf"]
        for name in names:
            file_type = name.split(".")[-1]
            artifact_data = ArtifactCreate(
                agent_type="finance",
                file_name=name,
                file_type=file_type,
                file_path=f"/storage/{name}",
                file_size=1024
            )
            artifact_service.create_artifact(test_user.id, artifact_data)
        
        # Search for "report"
        artifacts, total = artifact_service.search_artifacts(test_user.id, "report")
        assert len(artifacts) == 2
        assert total == 2
        
        # Search for "budget"
        artifacts, total = artifact_service.search_artifacts(test_user.id, "budget")
        assert len(artifacts) == 1
        assert total == 1
        assert artifacts[0].file_name == "budget_analysis.docx"
    
    def test_get_recent_artifacts(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test getting recent artifacts."""
        # Create 5 artifacts
        for i in range(5):
            artifact_data = ArtifactCreate(
                agent_type="finance",
                file_name=f"report_{i}.pdf",
                file_type="pdf",
                file_path=f"/storage/report_{i}.pdf",
                file_size=1024
            )
            artifact_service.create_artifact(test_user.id, artifact_data)
        
        # Get 3 most recent
        artifacts = artifact_service.get_recent_artifacts(test_user.id, limit=3)
        assert len(artifacts) == 3
        # Most recent should be report_4 (created last)
        assert artifacts[0].file_name == "report_4.pdf"
    
    def test_verify_file_exists(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test verifying if physical file exists."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(b"test content")
            file_path = tmp_file.name
        
        try:
            # Create artifact
            artifact_data = ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="pdf",
                file_path=file_path,
                file_size=12
            )
            created = artifact_service.create_artifact(test_user.id, artifact_data)
            
            # Verify file exists
            exists, path = artifact_service.verify_file_exists(created.id, test_user.id)
            assert exists is True
            assert path == file_path
            
            # Delete file
            os.remove(file_path)
            
            # Verify file doesn't exist
            exists, path = artifact_service.verify_file_exists(created.id, test_user.id)
            assert exists is False
            assert path is None
        finally:
            # Cleanup
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_bulk_delete_artifacts(
        self, 
        artifact_service: ArtifactService, 
        test_user: User
    ):
        """Test bulk deleting artifacts."""
        # Create 5 artifacts
        artifact_ids = []
        for i in range(5):
            artifact_data = ArtifactCreate(
                agent_type="finance",
                file_name=f"report_{i}.pdf",
                file_type="pdf",
                file_path=f"/storage/report_{i}.pdf",
                file_size=1024
            )
            created = artifact_service.create_artifact(test_user.id, artifact_data)
            artifact_ids.append(created.id)
        
        # Delete first 3
        results = artifact_service.bulk_delete_artifacts(
            artifact_ids[:3], 
            test_user.id, 
            delete_files=False
        )
        
        assert results["deleted_count"] == 3
        assert results["failed_count"] == 0
        
        # Verify they're deleted
        artifacts, total = artifact_service.get_artifacts(test_user.id)
        assert total == 2
