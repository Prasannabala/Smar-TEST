"""
Requirement document model.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Requirement:
    """
    Represents a parsed requirement document.
    """
    filename: str
    content: str
    file_type: str = ""
    word_count: int = 0
    page_count: int = 1

    # Extracted sections (if identifiable)
    title: str = ""
    summary: str = ""
    functional_requirements: List[str] = field(default_factory=list)
    non_functional_requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.word_count:
            self.word_count = len(self.content.split())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'filename': self.filename,
            'content': self.content,
            'file_type': self.file_type,
            'word_count': self.word_count,
            'page_count': self.page_count,
            'title': self.title,
            'summary': self.summary,
            'functional_requirements': self.functional_requirements,
            'non_functional_requirements': self.non_functional_requirements,
            'constraints': self.constraints,
            'assumptions': self.assumptions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Requirement':
        return cls(**data)

    def get_display_name(self) -> str:
        """Get a clean display name from filename."""
        # Remove extension and clean up
        name = self.filename
        for ext in ['.txt', '.pdf', '.docx', '.doc']:
            name = name.replace(ext, '')
        return name.replace('_', ' ').replace('-', ' ').title()

    def get_content_preview(self, max_chars: int = 500) -> str:
        """Get a preview of the content."""
        if len(self.content) <= max_chars:
            return self.content
        return self.content[:max_chars] + "..."

    def get_stats(self) -> Dict[str, Any]:
        """Get document statistics."""
        return {
            'filename': self.filename,
            'file_type': self.file_type,
            'word_count': self.word_count,
            'page_count': self.page_count,
            'char_count': len(self.content),
            'line_count': len(self.content.split('\n')),
        }
