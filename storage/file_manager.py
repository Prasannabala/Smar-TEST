"""
File management utilities for exports and client data.
"""
import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO

from config.settings import CLIENTS_DIR, EXPORTS_DIR


class FileManager:
    """
    Manages file operations for client data and exports.
    """

    def __init__(self):
        self.clients_dir = CLIENTS_DIR
        self.exports_dir = EXPORTS_DIR

    # Client JSON file operations
    def save_client_json(self, client_id: str, data: Dict[str, Any]) -> Path:
        """Save client data to JSON file."""
        file_path = self.clients_dir / f"{client_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return file_path

    def load_client_json(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Load client data from JSON file."""
        file_path = self.clients_dir / f"{client_id}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def delete_client_json(self, client_id: str) -> bool:
        """Delete client JSON file."""
        file_path = self.clients_dir / f"{client_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    # Export file operations
    def generate_export_filename(self, client_name: str, requirement_name: str,
                                  test_type: str, extension: str) -> str:
        """
        Generate auto-named export filename.

        Format: {client_name}_{requirement_name}_{test_type}_{YYYYMMDD_HHMMSS}.{ext}
        """
        # Clean names for filename
        client_clean = self._sanitize_filename(client_name)
        req_clean = self._sanitize_filename(requirement_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return f"{client_clean}_{req_clean}_{test_type}_{timestamp}.{extension}"

    def save_export(self, filename: str, content: bytes) -> Path:
        """Save export file."""
        file_path = self.exports_dir / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        return file_path

    def save_export_text(self, filename: str, content: str) -> Path:
        """Save text export file."""
        file_path = self.exports_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    def get_export_path(self, filename: str) -> Path:
        """Get full path for an export file."""
        return self.exports_dir / filename

    def list_exports(self, pattern: str = "*") -> List[Path]:
        """List export files matching pattern."""
        return list(self.exports_dir.glob(pattern))

    def delete_export(self, filename: str) -> bool:
        """Delete an export file."""
        file_path = self.exports_dir / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def create_zip_bundle(self, files: List[Path], zip_name: str) -> Path:
        """
        Create a ZIP bundle of multiple files.

        Args:
            files: List of file paths to include
            zip_name: Name for the ZIP file

        Returns:
            Path to created ZIP file
        """
        zip_path = self.exports_dir / zip_name
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                if file_path.exists():
                    zipf.write(file_path, file_path.name)

        return zip_path

    def cleanup_old_exports(self, days: int = 30) -> int:
        """
        Delete export files older than specified days.

        Args:
            days: Number of days to keep files

        Returns:
            Number of files deleted
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted = 0

        for file_path in self.exports_dir.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff:
                file_path.unlink()
                deleted += 1

        return deleted

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize a string for use in filename."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        result = name
        for char in invalid_chars:
            result = result.replace(char, '')

        # Replace spaces with underscores
        result = result.replace(' ', '_')

        # Remove leading/trailing dots and spaces
        result = result.strip('. ')

        # Truncate if too long
        if len(result) > 50:
            result = result[:50]

        return result or "unnamed"

    def get_file_size(self, file_path: Path) -> str:
        """Get human-readable file size."""
        if not file_path.exists():
            return "0 B"

        size = file_path.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


# Singleton instance
_file_manager: Optional[FileManager] = None


def get_file_manager() -> FileManager:
    """Get the global file manager instance."""
    global _file_manager
    if _file_manager is None:
        _file_manager = FileManager()
    return _file_manager
