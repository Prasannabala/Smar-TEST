"""
SQLite database operations for persistent storage.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from config.settings import DB_PATH


class Database:
    """SQLite database manager for application data."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Clients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    project_name TEXT,
                    project_description TEXT,
                    tech_stack TEXT,
                    test_environment TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # Client rules table (navigation, thumb, business rules)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS client_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    rule_content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                )
            ''')

            # Client documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS client_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    content TEXT NOT NULL,
                    file_type TEXT,
                    uploaded_at TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                )
            ''')

            # Test generation history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT,
                    requirement_filename TEXT,
                    test_count INTEGER,
                    test_types TEXT,
                    generated_at TEXT NOT NULL,
                    export_path TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
                )
            ''')

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    # Client operations
    def create_client(self, client_data: Dict[str, Any]) -> str:
        """Create a new client."""
        now = datetime.now().isoformat()
        client_id = client_data.get('id') or self._generate_id()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clients (id, name, project_name, project_description,
                                   tech_stack, test_environment, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                client_id,
                client_data['name'],
                client_data.get('project_name', ''),
                client_data.get('project_description', ''),
                json.dumps(client_data.get('tech_stack', [])),
                client_data.get('test_environment', ''),
                now,
                now
            ))
            conn.commit()

        return client_id

    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
            row = cursor.fetchone()

            if row:
                client = dict(row)
                client['tech_stack'] = json.loads(client['tech_stack'] or '[]')
                client['rules'] = self.get_client_rules(client_id)
                client['documents'] = self.get_client_documents(client_id)
                return client

        return None

    def get_client_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get client by name."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM clients WHERE name = ?', (name,))
            row = cursor.fetchone()
            if row:
                return self.get_client(row['id'])
        return None

    def get_all_clients(self) -> List[Dict[str, Any]]:
        """Get all clients."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients ORDER BY name')
            rows = cursor.fetchall()

            clients = []
            for row in rows:
                client = dict(row)
                client['tech_stack'] = json.loads(client['tech_stack'] or '[]')
                clients.append(client)

            return clients

    def update_client(self, client_id: str, client_data: Dict[str, Any]) -> bool:
        """Update client data."""
        now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE clients
                SET name = ?, project_name = ?, project_description = ?,
                    tech_stack = ?, test_environment = ?, updated_at = ?
                WHERE id = ?
            ''', (
                client_data['name'],
                client_data.get('project_name', ''),
                client_data.get('project_description', ''),
                json.dumps(client_data.get('tech_stack', [])),
                client_data.get('test_environment', ''),
                now,
                client_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_client(self, client_id: str) -> bool:
        """Delete a client and all related data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
            conn.commit()
            return cursor.rowcount > 0

    # Rules operations
    def add_client_rule(self, client_id: str, rule_type: str, rule_content: str) -> int:
        """Add a rule to a client."""
        now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO client_rules (client_id, rule_type, rule_content, created_at)
                VALUES (?, ?, ?, ?)
            ''', (client_id, rule_type, rule_content, now))
            conn.commit()
            return cursor.lastrowid

    def get_client_rules(self, client_id: str, rule_type: Optional[str] = None) -> Dict[str, List[str]]:
        """Get client rules organized by type."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if rule_type:
                cursor.execute(
                    'SELECT rule_type, rule_content FROM client_rules WHERE client_id = ? AND rule_type = ?',
                    (client_id, rule_type)
                )
            else:
                cursor.execute(
                    'SELECT rule_type, rule_content FROM client_rules WHERE client_id = ?',
                    (client_id,)
                )

            rules = {'navigation': [], 'thumb': [], 'business': [], 'best_practices': []}
            for row in cursor.fetchall():
                rule_type = row['rule_type']
                if rule_type in rules:
                    rules[rule_type].append(row['rule_content'])
                else:
                    rules[rule_type] = [row['rule_content']]

            return rules

    def delete_client_rules(self, client_id: str, rule_type: Optional[str] = None) -> int:
        """Delete client rules."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if rule_type:
                cursor.execute(
                    'DELETE FROM client_rules WHERE client_id = ? AND rule_type = ?',
                    (client_id, rule_type)
                )
            else:
                cursor.execute('DELETE FROM client_rules WHERE client_id = ?', (client_id,))

            conn.commit()
            return cursor.rowcount

    def update_client_rules(self, client_id: str, rule_type: str, rules: List[str]) -> None:
        """Replace all rules of a type for a client."""
        self.delete_client_rules(client_id, rule_type)
        for rule in rules:
            if rule.strip():
                self.add_client_rule(client_id, rule_type, rule.strip())

    # Document operations
    def add_client_document(self, client_id: str, filename: str, content: str, file_type: str) -> int:
        """Add a document to a client."""
        now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO client_documents (client_id, filename, content, file_type, uploaded_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (client_id, filename, content, file_type, now))
            conn.commit()
            return cursor.lastrowid

    def get_client_documents(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a client."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, filename, content, file_type, uploaded_at FROM client_documents WHERE client_id = ?',
                (client_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete_client_document(self, document_id: int) -> bool:
        """Delete a client document."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM client_documents WHERE id = ?', (document_id,))
            conn.commit()
            return cursor.rowcount > 0

    # Generation history
    def add_generation_record(self, client_id: Optional[str], requirement_filename: str,
                              test_count: int, test_types: List[str], export_path: Optional[str] = None) -> int:
        """Record a test generation."""
        now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO generation_history (client_id, requirement_filename, test_count,
                                               test_types, generated_at, export_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (client_id, requirement_filename, test_count, json.dumps(test_types), now, export_path))
            conn.commit()
            return cursor.lastrowid

    def get_generation_history(self, client_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get generation history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if client_id:
                cursor.execute('''
                    SELECT * FROM generation_history
                    WHERE client_id = ?
                    ORDER BY generated_at DESC LIMIT ?
                ''', (client_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM generation_history
                    ORDER BY generated_at DESC LIMIT ?
                ''', (limit,))

            records = []
            for row in cursor.fetchall():
                record = dict(row)
                record['test_types'] = json.loads(record['test_types'] or '[]')
                records.append(record)

            return records

    def clear_generation_history(self) -> int:
        """Clear all generation history records. Returns number of records deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM generation_history')
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID."""
        import uuid
        return str(uuid.uuid4())[:8]


# Singleton instance
_database: Optional[Database] = None


def get_database() -> Database:
    """Get the global database instance."""
    global _database
    if _database is None:
        _database = Database()
    return _database
