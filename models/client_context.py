"""
Client context data model and management.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any

from storage.database import get_database, Database
from storage.file_manager import get_file_manager, FileManager


@dataclass
class ClientContext:
    """
    Represents a client project context with all associated rules and documents.
    """
    id: str = ""
    name: str = ""
    project_name: str = ""
    project_description: str = ""
    tech_stack: List[str] = field(default_factory=list)
    test_environment: str = ""
    created_at: str = ""
    updated_at: str = ""

    # Rules
    navigation_rules: List[str] = field(default_factory=list)
    thumb_rules: List[str] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)

    # Uploaded documents
    documents: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientContext':
        """Create from dictionary."""
        # Handle rules from database format
        rules = data.pop('rules', {})
        if rules:
            data['navigation_rules'] = rules.get('navigation', [])
            data['thumb_rules'] = rules.get('thumb', [])
            data['business_rules'] = rules.get('business', [])
            data['best_practices'] = rules.get('best_practices', [])

        # Filter to only valid fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        return cls(**filtered_data)

    def get_context_text(self) -> str:
        """
        Get formatted context text for LLM prompts.
        Combines all rules and relevant document content.
        """
        sections = []

        # Project info
        if self.project_name or self.project_description:
            sections.append(f"## Project: {self.project_name}")
            if self.project_description:
                sections.append(self.project_description)

        # Tech stack
        if self.tech_stack:
            sections.append(f"\n## Technology Stack\n{', '.join(self.tech_stack)}")

        # Test environment
        if self.test_environment:
            sections.append(f"\n## Test Environment\n{self.test_environment}")

        # Navigation rules
        if self.navigation_rules:
            sections.append("\n## Navigation Rules")
            for rule in self.navigation_rules:
                sections.append(f"- {rule}")

        # Thumb rules
        if self.thumb_rules:
            sections.append("\n## Thumb Rules (Testing Conventions)")
            for rule in self.thumb_rules:
                sections.append(f"- {rule}")

        # Business rules
        if self.business_rules:
            sections.append("\n## Business Rules")
            for rule in self.business_rules:
                sections.append(f"- {rule}")

        # Best practices
        if self.best_practices:
            sections.append("\n## Best Practices")
            for practice in self.best_practices:
                sections.append(f"- {practice}")

        # Document summaries
        if self.documents:
            sections.append("\n## Reference Documents")
            for doc in self.documents[:5]:  # Limit to 5 docs
                content_preview = doc.get('content', '')[:500]
                sections.append(f"\n### {doc.get('filename', 'Document')}")
                sections.append(content_preview + "..." if len(doc.get('content', '')) > 500 else content_preview)

        return '\n'.join(sections)

    def get_rules_summary(self) -> str:
        """Get a brief summary of all rules."""
        summary = []
        if self.navigation_rules:
            summary.append(f"Navigation: {len(self.navigation_rules)} rules")
        if self.thumb_rules:
            summary.append(f"Thumb Rules: {len(self.thumb_rules)} rules")
        if self.business_rules:
            summary.append(f"Business: {len(self.business_rules)} rules")
        if self.best_practices:
            summary.append(f"Best Practices: {len(self.best_practices)} items")
        if self.documents:
            summary.append(f"Documents: {len(self.documents)} files")

        return " | ".join(summary) if summary else "No rules configured"


class ClientContextManager:
    """
    Manager for client context CRUD operations.
    """

    def __init__(self):
        self.db: Database = get_database()
        self.file_manager: FileManager = get_file_manager()

    def create(self, client_data: Dict[str, Any]) -> ClientContext:
        """
        Create a new client context.

        Args:
            client_data: Dictionary with client information

        Returns:
            Created ClientContext
        """
        # Create in database
        client_id = self.db.create_client(client_data)

        # Add rules if provided
        for rule in client_data.get('navigation_rules', []):
            if rule.strip():
                self.db.add_client_rule(client_id, 'navigation', rule.strip())

        for rule in client_data.get('thumb_rules', []):
            if rule.strip():
                self.db.add_client_rule(client_id, 'thumb', rule.strip())

        for rule in client_data.get('business_rules', []):
            if rule.strip():
                self.db.add_client_rule(client_id, 'business', rule.strip())

        for practice in client_data.get('best_practices', []):
            if practice.strip():
                self.db.add_client_rule(client_id, 'best_practices', practice.strip())

        return self.get(client_id)

    def get(self, client_id: str) -> Optional[ClientContext]:
        """
        Get client context by ID.

        Args:
            client_id: Client ID

        Returns:
            ClientContext or None if not found
        """
        data = self.db.get_client(client_id)
        if data:
            return ClientContext.from_dict(data)
        return None

    def get_by_name(self, name: str) -> Optional[ClientContext]:
        """
        Get client context by name.

        Args:
            name: Client name

        Returns:
            ClientContext or None if not found
        """
        data = self.db.get_client_by_name(name)
        if data:
            return ClientContext.from_dict(data)
        return None

    def get_all(self) -> List[ClientContext]:
        """
        Get all client contexts.

        Returns:
            List of ClientContext objects
        """
        clients_data = self.db.get_all_clients()
        contexts = []
        for data in clients_data:
            # Get full data including rules
            full_data = self.db.get_client(data['id'])
            if full_data:
                contexts.append(ClientContext.from_dict(full_data))
        return contexts

    def update(self, client_id: str, client_data: Dict[str, Any]) -> Optional[ClientContext]:
        """
        Update client context.

        Args:
            client_id: Client ID to update
            client_data: Updated data

        Returns:
            Updated ClientContext or None if not found
        """
        # Update basic info
        if not self.db.update_client(client_id, client_data):
            return None

        # Update rules
        if 'navigation_rules' in client_data:
            self.db.update_client_rules(client_id, 'navigation', client_data['navigation_rules'])

        if 'thumb_rules' in client_data:
            self.db.update_client_rules(client_id, 'thumb', client_data['thumb_rules'])

        if 'business_rules' in client_data:
            self.db.update_client_rules(client_id, 'business', client_data['business_rules'])

        if 'best_practices' in client_data:
            self.db.update_client_rules(client_id, 'best_practices', client_data['best_practices'])

        return self.get(client_id)

    def delete(self, client_id: str) -> bool:
        """
        Delete client context.

        Args:
            client_id: Client ID to delete

        Returns:
            True if deleted, False otherwise
        """
        # Delete JSON file if exists
        self.file_manager.delete_client_json(client_id)

        # Delete from database (cascade will remove rules and documents)
        return self.db.delete_client(client_id)

    def add_document(self, client_id: str, filename: str, content: str, file_type: str) -> int:
        """
        Add a document to client context.

        Args:
            client_id: Client ID
            filename: Document filename
            content: Document text content
            file_type: File type (txt, pdf, docx)

        Returns:
            Document ID
        """
        return self.db.add_client_document(client_id, filename, content, file_type)

    def remove_document(self, document_id: int) -> bool:
        """
        Remove a document from client context.

        Args:
            document_id: Document ID to remove

        Returns:
            True if removed, False otherwise
        """
        return self.db.delete_client_document(document_id)

    def get_client_names(self) -> List[str]:
        """Get list of all client names."""
        return [c['name'] for c in self.db.get_all_clients()]


# Factory function
def get_client_manager() -> ClientContextManager:
    """Get client context manager instance."""
    return ClientContextManager()
