# services/version_strategies.py
import difflib
import json
from models.document import DocumentVersion

class VersionStrategy:
    """Interface for version strategies"""
    def create_version(self, document, user_id, previous_version=None):
        """Create a version from a document"""
        pass
    
    def restore_version(self, document, version_content, version_type, base_version=None):
        """Restore a document from a version"""
        pass


class FullSnapshotStrategy(VersionStrategy):
    """Strategy for full snapshot versioning"""
    
    def create_version(self, document, user_id, previous_version=None):
        """Create a full snapshot version from document"""
        version = DocumentVersion(
            document_id=document.id,
            content_type="full",
            content=document.content,
            created_by=user_id
        )
        return version
    
    def restore_version(self, document, version_content, version_type, base_version=None):
        """Restore document from full snapshot"""
        if version_type != "full":
            raise ValueError("Expected full snapshot version")
        
        document.content = version_content
        return document


class DiffStrategy(VersionStrategy):
    """Strategy for diff-based versioning"""
    
    def create_version(self, document, user_id, previous_version=None):
        """Create a diff version from document"""
        if previous_version is None:
            # If no previous version, create a full snapshot
            return FullSnapshotStrategy().create_version(document, user_id)
        
        previous_content = previous_version["content"]
        current_content = document.content
        
        # Create a unified diff
        diff = difflib.unified_diff(
            previous_content.splitlines(keepends=True),
            current_content.splitlines(keepends=True),
            n=3
        )
        
        version = DocumentVersion(
            document_id=document.id,
            content_type="diff",
            content=''.join(diff),
            base_version_id=previous_version["id"],
            created_by=user_id
        )
        
        return version
    
    def restore_version(self, document, version_content, version_type, base_version=None):
        """Restore document from diff"""
        if version_type != "diff":
            raise ValueError("Expected diff version")
        
        if not base_version:
            raise ValueError("Base version required for diff restoration")
            
        # Apply the diff to the base version
        base_content = base_version["content"]
        patched_content = []
      
        lines = base_content.splitlines()
        
        for line in version_content.splitlines():
            if line.startswith('+') and not line.startswith('+++'):
                patched_content.append(line[1:])
            elif line.startswith('-') or line.startswith('---'):
                continue
            elif not line.startswith('@'):
                patched_content.append(line)
        
        document.content = '\n'.join(patched_content)
        return document