"""
Settings Manager for Smar-Test - Handles auto-load/save from ~/.smar-test/
Provides persistent storage for user settings and client configurations.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import asdict


class SettingsManager:
    """
    Manages settings persistence using user's home directory.

    Folder structure:
    ~/.smar-test/
    ├── settings.json          (LLM provider config)
    ├── clients/
    │   ├── client_1.json
    │   ├── client_2.json
    │   └── ...
    └── exports/               (Downloaded files)
    """

    def __init__(self):
        """Initialize settings manager and create folders if needed."""
        self.settings_dir = Path.home() / ".smar-test"
        self.settings_file = self.settings_dir / "settings.json"
        self.clients_dir = self.settings_dir / "clients"
        self.exports_dir = self.settings_dir / "exports"

        # Auto-create folders
        self._ensure_folders()

    def get_settings_path(self) -> str:
        """Get the full path to settings.json as a string."""
        return str(self.settings_file)

    def _ensure_folders(self) -> None:
        """Create necessary folders if they don't exist."""
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        self.clients_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from ~/.smar-test/settings.json
        Returns empty dict if file doesn't exist (first run).
        """
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load settings: {e}")
                return {}
        return {}

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save settings to ~/.smar-test/settings.json

        Args:
            settings: Settings dictionary to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Don't save sensitive data like API keys
            safe_settings = {k: v for k, v in settings.items()
                           if not k.endswith('_key') and not k.endswith('_token')}

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(safe_settings, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Warning: Could not save settings: {e}")
            return False

    def load_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific client configuration.

        Args:
            client_id: Client identifier

        Returns:
            Client data dict or None if not found
        """
        client_file = self.clients_dir / f"{client_id}.json"
        if client_file.exists():
            try:
                with open(client_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load client {client_id}: {e}")
                return None
        return None

    def save_client(self, client_id: str, client_data: Dict[str, Any]) -> bool:
        """
        Save a client configuration.

        Args:
            client_id: Client identifier
            client_data: Client data to save

        Returns:
            True if successful, False otherwise
        """
        try:
            client_file = self.clients_dir / f"{client_id}.json"
            with open(client_file, 'w', encoding='utf-8') as f:
                json.dump(client_data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Warning: Could not save client {client_id}: {e}")
            return False

    def delete_client(self, client_id: str) -> bool:
        """
        Delete a client configuration file.

        Args:
            client_id: Client identifier

        Returns:
            True if successful, False otherwise
        """
        client_file = self.clients_dir / f"{client_id}.json"
        if client_file.exists():
            try:
                client_file.unlink()
                return True
            except IOError as e:
                print(f"Warning: Could not delete client {client_id}: {e}")
                return False
        return True

    def list_clients(self) -> list[str]:
        """
        List all saved client IDs.

        Returns:
            List of client IDs
        """
        if not self.clients_dir.exists():
            return []
        return [f.stem for f in self.clients_dir.glob("*.json")]

    def export_all_settings(self) -> Dict[str, Any]:
        """
        Export all settings and clients as a single JSON for backup/transfer.

        Returns:
            Dictionary with all settings and client data
        """
        export_data = {
            "settings": self.load_settings(),
            "clients": {}
        }

        for client_id in self.list_clients():
            client_data = self.load_client(client_id)
            if client_data:
                export_data["clients"][client_id] = client_data

        return export_data

    def import_all_settings(self, import_data: Dict[str, Any]) -> bool:
        """
        Import all settings and clients from a backup file.

        Args:
            import_data: Dictionary with settings and client data

        Returns:
            True if successful, False otherwise
        """
        try:
            # Import settings
            if "settings" in import_data:
                self.save_settings(import_data["settings"])

            # Import clients
            if "clients" in import_data:
                for client_id, client_data in import_data["clients"].items():
                    self.save_client(client_id, client_data)

            return True
        except Exception as e:
            print(f"Warning: Could not import settings: {e}")
            return False

    def get_settings_path(self) -> Path:
        """Get the path to settings directory."""
        return self.settings_dir

    def get_exports_path(self) -> Path:
        """Get the path to exports directory."""
        return self.exports_dir

    def get_clients_path(self) -> Path:
        """Get the path to clients directory."""
        return self.clients_dir
