"""
Tests for Artifact Schemas
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.artifact import (
    ArtifactCreate,
    ArtifactResponse,
    ArtifactListResponse,
)


class TestArtifactCreate:
    """Tests for ArtifactCreate schema."""
    
    def test_valid_artifact_create_minimal(self):
        """Test that valid minimal artifact creation data is accepted."""
        artifact = ArtifactCreate(
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/storage/reports/report.pdf",
            file_size=1024
        )
        assert artifact.agent_type == "finance"
        assert artifact.file_name == "report.pdf"
        assert artifact.file_type == "pdf"
        assert artifact.file_path == "/storage/reports/report.pdf"
        assert artifact.file_size == 1024
        assert artifact.task_id is None
        assert artifact.mime_type is None
        assert artifact.metadata is None
    
    def test_valid_artifact_create_full(self):
        """Test that valid full artifact creation data is accepted."""
        artifact = ArtifactCreate(
            task_id=123,
            agent_type="data_analyst",
            file_name="analysis.docx",
            file_type="docx",
            file_path="/storage/documents/analysis.docx",
            file_size=2048,
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            metadata={"pages": 10, "author": "Data Analyst"}
        )
        assert artifact.task_id == 123
        assert artifact.agent_type == "data_analyst"
        assert artifact.file_name == "analysis.docx"
        assert artifact.file_type == "docx"
        assert artifact.file_path == "/storage/documents/analysis.docx"
        assert artifact.file_size == 2048
        assert artifact.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert artifact.metadata == {"pages": 10, "author": "Data Analyst"}
    
    def test_missing_agent_type(self):
        """Test that missing agent_type is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                file_name="report.pdf",
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=1024
            )
    
    def test_missing_file_name(self):
        """Test that missing file_name is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=1024
            )
    
    def test_missing_file_type(self):
        """Test that missing file_type is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_path="/storage/report.pdf",
                file_size=1024
            )
    
    def test_missing_file_path(self):
        """Test that missing file_path is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="pdf",
                file_size=1024
            )
    
    def test_missing_file_size(self):
        """Test that missing file_size is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="pdf",
                file_path="/storage/report.pdf"
            )
    
    def test_empty_agent_type(self):
        """Test that empty agent_type is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="",
                file_name="report.pdf",
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=1024
            )
    
    def test_empty_file_name(self):
        """Test that empty file_name is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="",
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=1024
            )
    
    def test_empty_file_type(self):
        """Test that empty file_type is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="",
                file_path="/storage/report.pdf",
                file_size=1024
            )
    
    def test_empty_file_path(self):
        """Test that empty file_path is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="pdf",
                file_path="",
                file_size=1024
            )
    
    def test_zero_file_size(self):
        """Test that zero file_size is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=0
            )
    
    def test_negative_file_size(self):
        """Test that negative file_size is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=-1
            )
    
    def test_agent_type_max_length(self):
        """Test that agent_type longer than 50 characters is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="x" * 51,
                file_name="report.pdf",
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=1024
            )
    
    def test_agent_type_exactly_50_characters(self):
        """Test that agent_type with exactly 50 characters is rejected (must be valid agent type)."""
        with pytest.raises(ValidationError) as exc_info:
            ArtifactCreate(
                agent_type="x" * 50,
                file_name="report.pdf",
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=1024
            )
        assert "Invalid agent type" in str(exc_info.value)
    
    def test_file_name_max_length(self):
        """Test that file_name longer than 255 characters is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="x" * 256,
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=1024
            )
    
    def test_file_name_exactly_255_characters(self):
        """Test that file_name with exactly 255 characters is accepted."""
        artifact = ArtifactCreate(
            agent_type="finance",
            file_name="x" * 255,
            file_type="pdf",
            file_path="/storage/report.pdf",
            file_size=1024
        )
        assert len(artifact.file_name) == 255
    
    def test_file_type_max_length(self):
        """Test that file_type longer than 50 characters is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="x" * 51,
                file_path="/storage/report.pdf",
                file_size=1024
            )
    
    def test_file_path_max_length(self):
        """Test that file_path longer than 500 characters is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="pdf",
                file_path="x" * 501,
                file_size=1024
            )
    
    def test_file_path_exactly_500_characters(self):
        """Test that file_path with exactly 500 characters is accepted."""
        artifact = ArtifactCreate(
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="x" * 500,
            file_size=1024
        )
        assert len(artifact.file_path) == 500
    
    def test_mime_type_max_length(self):
        """Test that mime_type longer than 100 characters is rejected."""
        with pytest.raises(ValidationError):
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=1024,
                mime_type="x" * 101
            )
    
    def test_mime_type_exactly_100_characters(self):
        """Test that mime_type with exactly 100 characters is rejected (must be valid MIME format)."""
        with pytest.raises(ValidationError) as exc_info:
            ArtifactCreate(
                agent_type="finance",
                file_name="report.pdf",
                file_type="pdf",
                file_path="/storage/report.pdf",
                file_size=1024,
                mime_type="x" * 100
            )
        assert "Invalid MIME type format" in str(exc_info.value)
    
    def test_metadata_dict(self):
        """Test that metadata accepts dictionary."""
        artifact = ArtifactCreate(
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/storage/report.pdf",
            file_size=1024,
            metadata={"key": "value", "nested": {"data": 123}}
        )
        assert artifact.metadata == {"key": "value", "nested": {"data": 123}}
    
    def test_various_file_types(self):
        """Test that various file types are accepted."""
        file_types = ["pdf", "docx", "png", "svg", "csv", "xlsx", "html", "json"]
        for file_type in file_types:
            artifact = ArtifactCreate(
                agent_type="finance",
                file_name=f"file.{file_type}",
                file_type=file_type,
                file_path=f"/storage/file.{file_type}",
                file_size=1024
            )
            assert artifact.file_type == file_type
    
    def test_large_file_size(self):
        """Test that file sizes over 100MB are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ArtifactCreate(
                agent_type="finance",
                file_name="large_file.pdf",
                file_type="pdf",
                file_path="/storage/large_file.pdf",
                file_size=1073741824  # 1 GB
            )
        assert "less than or equal to 100000000" in str(exc_info.value)


class TestArtifactResponse:
    """Tests for ArtifactResponse schema."""
    
    def test_valid_artifact_response_minimal(self):
        """Test that valid minimal artifact response is accepted."""
        artifact = ArtifactResponse(
            id=1,
            artifact_id="artifact_123",
            task_id=None,
            user_id=1,
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/storage/report.pdf",
            file_size=1024,
            mime_type=None,
            metadata=None,
            created_at=datetime.now()
        )
        assert artifact.id == 1
        assert artifact.artifact_id == "artifact_123"
        assert artifact.task_id is None
        assert artifact.user_id == 1
        assert artifact.agent_type == "finance"
        assert artifact.file_name == "report.pdf"
        assert artifact.file_type == "pdf"
        assert artifact.file_path == "/storage/report.pdf"
        assert artifact.file_size == 1024
        assert artifact.mime_type is None
        assert artifact.metadata is None
    
    def test_valid_artifact_response_full(self):
        """Test that valid full artifact response is accepted."""
        now = datetime.now()
        artifact = ArtifactResponse(
            id=1,
            artifact_id="artifact_123",
            task_id=456,
            user_id=1,
            agent_type="data_analyst",
            file_name="analysis.docx",
            file_type="docx",
            file_path="/storage/analysis.docx",
            file_size=2048,
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            metadata={"pages": 10, "author": "Data Analyst"},
            created_at=now
        )
        assert artifact.task_id == 456
        assert artifact.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert artifact.metadata == {"pages": 10, "author": "Data Analyst"}
        assert artifact.created_at == now
    
    def test_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        with pytest.raises(ValidationError):
            ArtifactResponse(
                id=1,
                artifact_id="artifact_123"
            )
    
    def test_from_attributes_config(self):
        """Test that from_attributes is enabled for SQLAlchemy model conversion."""
        assert ArtifactResponse.model_config.get('from_attributes') is True


class TestArtifactListResponse:
    """Tests for ArtifactListResponse schema."""
    
    def test_valid_artifact_list_response(self):
        """Test that valid artifact list response is accepted."""
        now = datetime.now()
        artifact1 = ArtifactResponse(
            id=1,
            artifact_id="artifact_1",
            task_id=None,
            user_id=1,
            agent_type="finance",
            file_name="report.pdf",
            file_type="pdf",
            file_path="/storage/report.pdf",
            file_size=1024,
            mime_type="application/pdf",
            metadata=None,
            created_at=now
        )
        
        artifact_list = ArtifactListResponse(
            artifacts=[artifact1],
            total=1,
            page=1,
            page_size=10
        )
        assert len(artifact_list.artifacts) == 1
        assert artifact_list.total == 1
        assert artifact_list.page == 1
        assert artifact_list.page_size == 10
    
    def test_empty_artifact_list(self):
        """Test that empty artifact list is accepted."""
        artifact_list = ArtifactListResponse(
            artifacts=[],
            total=0,
            page=1,
            page_size=10
        )
        assert len(artifact_list.artifacts) == 0
        assert artifact_list.total == 0
    
    def test_multiple_artifacts(self):
        """Test that multiple artifacts in list are accepted."""
        now = datetime.now()
        artifacts = [
            ArtifactResponse(
                id=i,
                artifact_id=f"artifact_{i}",
                task_id=None,
                user_id=1,
                agent_type="finance",
                file_name=f"report_{i}.pdf",
                file_type="pdf",
                file_path=f"/storage/report_{i}.pdf",
                file_size=1024 * i,
                mime_type="application/pdf",
                metadata=None,
                created_at=now
            )
            for i in range(1, 6)
        ]
        
        artifact_list = ArtifactListResponse(
            artifacts=artifacts,
            total=5,
            page=1,
            page_size=10
        )
        assert len(artifact_list.artifacts) == 5
        assert artifact_list.total == 5
