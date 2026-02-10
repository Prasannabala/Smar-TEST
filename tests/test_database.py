"""
Tests for the SQLite database layer (storage/database.py).
All tests use a temporary database — no production data is touched.
"""
import json
import pytest

from storage.database import Database


class TestDatabaseInit:
    """Tests for database initialization."""

    def test_creates_tables(self, temp_db):
        """All four tables should be created on init."""
        with temp_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row["name"] for row in cursor.fetchall()}

        assert "clients" in tables
        assert "client_rules" in tables
        assert "client_documents" in tables
        assert "generation_history" in tables

    def test_foreign_keys_enabled(self, temp_db):
        """PRAGMA foreign_keys should be ON."""
        with temp_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()
            assert result[0] == 1


class TestClientOperations:
    """Tests for client CRUD operations."""

    def test_create_client(self, temp_db):
        client_id = temp_db.create_client({
            "name": "Acme Corp",
            "project_name": "Portal",
            "project_description": "Customer portal",
            "tech_stack": ["React", "Python"],
            "test_environment": "Chrome"
        })
        assert client_id is not None
        assert len(client_id) > 0

    def test_get_client(self, temp_db):
        client_id = temp_db.create_client({
            "name": "Test Corp",
            "project_name": "TestApp"
        })
        client = temp_db.get_client(client_id)
        assert client is not None
        assert client["name"] == "Test Corp"
        assert client["project_name"] == "TestApp"

    def test_get_client_not_found(self, temp_db):
        client = temp_db.get_client("nonexistent")
        assert client is None

    def test_get_client_by_name(self, temp_db):
        temp_db.create_client({"name": "FindMe Corp"})
        client = temp_db.get_client_by_name("FindMe Corp")
        assert client is not None
        assert client["name"] == "FindMe Corp"

    def test_get_all_clients(self, temp_db):
        temp_db.create_client({"name": "Client A"})
        temp_db.create_client({"name": "Client B"})
        clients = temp_db.get_all_clients()
        assert len(clients) == 2

    def test_update_client(self, temp_db):
        client_id = temp_db.create_client({"name": "Old Name"})
        updated = temp_db.update_client(client_id, {
            "name": "New Name",
            "project_name": "Updated Project"
        })
        assert updated is True
        client = temp_db.get_client(client_id)
        assert client["name"] == "New Name"

    def test_delete_client(self, temp_db):
        client_id = temp_db.create_client({"name": "ToDelete"})
        deleted = temp_db.delete_client(client_id)
        assert deleted is True
        assert temp_db.get_client(client_id) is None

    def test_unique_client_name(self, temp_db):
        temp_db.create_client({"name": "Unique Corp"})
        with pytest.raises(Exception):
            temp_db.create_client({"name": "Unique Corp"})

    def test_tech_stack_stored_as_json(self, temp_db):
        client_id = temp_db.create_client({
            "name": "Tech Corp",
            "tech_stack": ["React", "Node.js", "PostgreSQL"]
        })
        client = temp_db.get_client(client_id)
        assert isinstance(client["tech_stack"], list)
        assert "React" in client["tech_stack"]


class TestClientRules:
    """Tests for client rules operations."""

    def test_add_and_get_rules(self, temp_db):
        client_id = temp_db.create_client({"name": "Rules Corp"})
        temp_db.add_client_rule(client_id, "navigation", "Start from home page")
        temp_db.add_client_rule(client_id, "navigation", "Use breadcrumbs")
        temp_db.add_client_rule(client_id, "business", "Verify email first")

        rules = temp_db.get_client_rules(client_id)
        assert len(rules["navigation"]) == 2
        assert len(rules["business"]) == 1
        assert "Start from home page" in rules["navigation"]

    def test_get_rules_by_type(self, temp_db):
        client_id = temp_db.create_client({"name": "TypedRules Corp"})
        temp_db.add_client_rule(client_id, "thumb", "Test on mobile")
        temp_db.add_client_rule(client_id, "business", "Max 5 attempts")

        rules = temp_db.get_client_rules(client_id, rule_type="thumb")
        assert len(rules["thumb"]) == 1

    def test_update_rules_replaces(self, temp_db):
        client_id = temp_db.create_client({"name": "Replace Corp"})
        temp_db.add_client_rule(client_id, "navigation", "Old rule 1")
        temp_db.add_client_rule(client_id, "navigation", "Old rule 2")

        temp_db.update_client_rules(client_id, "navigation", ["New rule A", "New rule B", "New rule C"])

        rules = temp_db.get_client_rules(client_id)
        assert len(rules["navigation"]) == 3
        assert "New rule A" in rules["navigation"]
        assert "Old rule 1" not in rules["navigation"]

    def test_delete_rules(self, temp_db):
        client_id = temp_db.create_client({"name": "DelRules Corp"})
        temp_db.add_client_rule(client_id, "navigation", "Rule 1")
        temp_db.add_client_rule(client_id, "business", "Rule 2")

        count = temp_db.delete_client_rules(client_id, rule_type="navigation")
        assert count == 1

        rules = temp_db.get_client_rules(client_id)
        assert len(rules["navigation"]) == 0
        assert len(rules["business"]) == 1

    def test_cascade_delete_with_client(self, temp_db):
        client_id = temp_db.create_client({"name": "Cascade Corp"})
        temp_db.add_client_rule(client_id, "navigation", "Rule 1")
        temp_db.add_client_rule(client_id, "thumb", "Rule 2")

        temp_db.delete_client(client_id)

        # Rules should be cascade deleted
        rules = temp_db.get_client_rules(client_id)
        total = sum(len(v) for v in rules.values())
        assert total == 0


class TestGenerationHistory:
    """Tests for generation history operations."""

    def test_add_record(self, temp_db):
        record_id = temp_db.add_generation_record(
            client_id=None,
            requirement_filename="requirements.txt",
            test_count=10,
            test_types=["manual", "gherkin"]
        )
        assert record_id is not None
        assert record_id > 0

    def test_get_history(self, temp_db):
        temp_db.add_generation_record(None, "file1.txt", 5, ["manual"])
        temp_db.add_generation_record(None, "file2.pdf", 8, ["manual", "selenium"])

        history = temp_db.get_generation_history()
        assert len(history) == 2
        # Most recent first
        assert history[0]["requirement_filename"] == "file2.pdf"

    def test_history_test_types_as_list(self, temp_db):
        temp_db.add_generation_record(None, "test.txt", 3, ["manual", "gherkin", "playwright"])
        history = temp_db.get_generation_history()
        assert isinstance(history[0]["test_types"], list)
        assert "gherkin" in history[0]["test_types"]

    def test_history_limit(self, temp_db):
        for i in range(10):
            temp_db.add_generation_record(None, f"file{i}.txt", i, ["manual"])

        history = temp_db.get_generation_history(limit=3)
        assert len(history) == 3

    def test_history_filter_by_client(self, temp_db):
        cid = temp_db.create_client({"name": "HistClient"})
        temp_db.add_generation_record(cid, "client_file.txt", 5, ["manual"])
        temp_db.add_generation_record(None, "other_file.txt", 3, ["manual"])

        client_history = temp_db.get_generation_history(client_id=cid)
        assert len(client_history) == 1
        assert client_history[0]["requirement_filename"] == "client_file.txt"

    def test_clear_history(self, temp_db):
        temp_db.add_generation_record(None, "f1.txt", 5, ["manual"])
        temp_db.add_generation_record(None, "f2.txt", 3, ["manual"])

        deleted = temp_db.clear_generation_history()
        assert deleted == 2

        history = temp_db.get_generation_history()
        assert len(history) == 0


class TestClientDocuments:
    """Tests for client document operations."""

    def test_add_document(self, temp_db):
        client_id = temp_db.create_client({"name": "DocCorp"})
        doc_id = temp_db.add_client_document(
            client_id, "requirements.pdf", "Sample content", "pdf"
        )
        assert doc_id > 0

    def test_get_documents(self, temp_db):
        client_id = temp_db.create_client({"name": "DocCorp2"})
        temp_db.add_client_document(client_id, "doc1.txt", "Content 1", "txt")
        temp_db.add_client_document(client_id, "doc2.pdf", "Content 2", "pdf")

        docs = temp_db.get_client_documents(client_id)
        assert len(docs) == 2

    def test_delete_document(self, temp_db):
        client_id = temp_db.create_client({"name": "DocDel"})
        doc_id = temp_db.add_client_document(client_id, "test.txt", "Content", "txt")

        deleted = temp_db.delete_client_document(doc_id)
        assert deleted is True

        docs = temp_db.get_client_documents(client_id)
        assert len(docs) == 0
