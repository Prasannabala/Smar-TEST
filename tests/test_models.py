"""
Tests for data models: TestStep, ManualTestCase, AutomationScript, TestSuite, Requirement.
"""
import json
import pytest

from models.test_case import (
    TestStep, ManualTestCase, AutomationScript, TestSuite,
    Priority, TestStatus, TestCategory
)
from models.requirement import Requirement


# ──────────────────────────────────────────────
# TestStep
# ──────────────────────────────────────────────

class TestTestStep:
    """Tests for the TestStep dataclass."""

    def test_create_step(self, sample_test_step):
        assert sample_test_step.step_number == 1
        assert "login" in sample_test_step.action.lower()
        assert sample_test_step.test_data != ""
        assert sample_test_step.expected_result != ""

    def test_step_to_dict(self, sample_test_step):
        d = sample_test_step.to_dict()
        assert isinstance(d, dict)
        assert d["step_number"] == 1
        assert "action" in d
        assert "test_data" in d
        assert "expected_result" in d

    def test_step_from_dict(self, sample_test_step):
        d = sample_test_step.to_dict()
        restored = TestStep.from_dict(d)
        assert restored.step_number == sample_test_step.step_number
        assert restored.action == sample_test_step.action

    def test_step_roundtrip(self, sample_test_step):
        """to_dict -> from_dict should produce identical object."""
        d = sample_test_step.to_dict()
        restored = TestStep.from_dict(d)
        assert restored.to_dict() == d

    def test_step_to_text(self, sample_test_step):
        text = sample_test_step.to_text()
        assert "Step 1" in text
        assert sample_test_step.action in text

    def test_step_defaults(self):
        step = TestStep(step_number=1, action="Click button")
        assert step.test_data == ""
        assert step.expected_result == ""


# ──────────────────────────────────────────────
# ManualTestCase
# ──────────────────────────────────────────────

class TestManualTestCase:
    """Tests for the ManualTestCase dataclass."""

    def test_create_test_case(self, sample_manual_test):
        assert sample_manual_test.test_id == "TC_001"
        assert sample_manual_test.priority == "High"
        assert len(sample_manual_test.test_steps) == 4
        assert len(sample_manual_test.tags) == 3

    def test_to_dict(self, sample_manual_test):
        d = sample_manual_test.to_dict()
        assert isinstance(d, dict)
        assert d["test_id"] == "TC_001"
        assert isinstance(d["test_steps"], list)
        assert isinstance(d["test_steps"][0], dict)

    def test_from_dict(self, sample_manual_test):
        d = sample_manual_test.to_dict()
        restored = ManualTestCase.from_dict(d)
        assert restored.test_id == sample_manual_test.test_id
        assert restored.test_name == sample_manual_test.test_name
        assert len(restored.test_steps) == len(sample_manual_test.test_steps)
        assert isinstance(restored.test_steps[0], TestStep)

    def test_roundtrip(self, sample_manual_test):
        d = sample_manual_test.to_dict()
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        restored = ManualTestCase.from_dict(parsed)
        assert restored.test_id == sample_manual_test.test_id
        assert len(restored.test_steps) == 4

    def test_to_text(self, sample_manual_test):
        text = sample_manual_test.to_text()
        assert "TC_001" in text
        assert "PRIORITY: High" in text
        assert "TEST STEPS:" in text

    def test_get_steps_text(self, sample_manual_test):
        text = sample_manual_test.get_steps_text()
        assert "1." in text
        assert "2." in text

    def test_get_expected_results_text(self, sample_manual_test):
        text = sample_manual_test.get_expected_results_text()
        assert "1." in text

    def test_get_preconditions_text(self, sample_manual_test):
        text = sample_manual_test.get_preconditions_text()
        assert "User account exists" in text

    def test_default_values(self):
        tc = ManualTestCase(test_id="TC_X", test_name="Test", description="Desc")
        assert tc.priority == Priority.MEDIUM.value
        assert tc.status == TestStatus.NEW.value
        assert tc.category == TestCategory.FUNCTIONAL.value
        assert tc.tags == []
        assert tc.preconditions == []


# ──────────────────────────────────────────────
# AutomationScript
# ──────────────────────────────────────────────

class TestAutomationScript:
    """Tests for the AutomationScript dataclass."""

    def test_gherkin_extension(self, sample_gherkin_script):
        assert sample_gherkin_script.get_extension() == "feature"

    def test_selenium_extension(self, sample_selenium_script):
        assert sample_selenium_script.get_extension() == "py"

    def test_playwright_extension(self, sample_playwright_script):
        assert sample_playwright_script.get_extension() == "spec.js"

    def test_to_dict_from_dict(self, sample_gherkin_script):
        d = sample_gherkin_script.to_dict()
        restored = AutomationScript.from_dict(d)
        assert restored.script_type == "gherkin"
        assert restored.filename == "login.feature"
        assert "Feature:" in restored.content

    def test_unknown_extension(self):
        script = AutomationScript(script_type="unknown", filename="test.txt", content="test")
        assert script.get_extension() == "txt"


# ──────────────────────────────────────────────
# TestSuite
# ──────────────────────────────────────────────

class TestTestSuite:
    """Tests for the TestSuite dataclass."""

    def test_create_suite(self, sample_test_suite):
        assert sample_test_suite.name == "Login Feature Tests"
        assert len(sample_test_suite.manual_tests) == 3
        assert len(sample_test_suite.gherkin_scripts) == 1
        assert len(sample_test_suite.selenium_scripts) == 1
        assert len(sample_test_suite.playwright_scripts) == 1

    def test_get_summary(self, sample_test_suite):
        summary = sample_test_suite.get_summary()
        assert summary["manual_tests"] == 3
        assert summary["selenium_tests"] == 1
        assert summary["playwright_tests"] == 1

    def test_get_total_count(self, sample_test_suite):
        total = sample_test_suite.get_total_count()
        assert total >= 3  # At least the manual tests

    def test_to_dict(self, sample_test_suite):
        d = sample_test_suite.to_dict()
        assert isinstance(d, dict)
        assert d["name"] == "Login Feature Tests"
        assert len(d["manual_tests"]) == 3
        assert isinstance(d["manual_tests"][0], dict)

    def test_from_dict(self, sample_test_suite):
        d = sample_test_suite.to_dict()
        restored = TestSuite.from_dict(d)
        assert restored.name == sample_test_suite.name
        assert len(restored.manual_tests) == 3
        assert isinstance(restored.manual_tests[0], ManualTestCase)
        assert isinstance(restored.manual_tests[0].test_steps[0], TestStep)

    def test_json_roundtrip(self, sample_test_suite):
        """Full JSON serialization roundtrip."""
        d = sample_test_suite.to_dict()
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        restored = TestSuite.from_dict(parsed)

        assert restored.name == sample_test_suite.name
        assert len(restored.manual_tests) == len(sample_test_suite.manual_tests)
        assert len(restored.gherkin_scripts) == len(sample_test_suite.gherkin_scripts)
        assert len(restored.selenium_scripts) == len(sample_test_suite.selenium_scripts)
        assert len(restored.playwright_scripts) == len(sample_test_suite.playwright_scripts)

    def test_empty_suite(self):
        suite = TestSuite(name="Empty")
        assert suite.get_total_count() == 0
        assert suite.get_summary() == {
            "manual_tests": 0,
            "gherkin_scenarios": 0,
            "selenium_tests": 0,
            "playwright_tests": 0,
        }


# ──────────────────────────────────────────────
# Requirement
# ──────────────────────────────────────────────

class TestRequirement:
    """Tests for the Requirement model."""

    def test_create_requirement(self, sample_requirement):
        assert sample_requirement.filename == "login_requirements.txt"
        assert sample_requirement.file_type == "txt"
        assert sample_requirement.word_count > 0

    def test_auto_word_count(self):
        req = Requirement(filename="test.txt", content="one two three four five")
        assert req.word_count == 5

    def test_to_dict(self, sample_requirement):
        d = sample_requirement.to_dict()
        assert isinstance(d, dict)
        assert d["filename"] == "login_requirements.txt"
        assert "content" in d

    def test_from_dict(self, sample_requirement):
        d = sample_requirement.to_dict()
        restored = Requirement.from_dict(d)
        assert restored.filename == sample_requirement.filename
        assert restored.content == sample_requirement.content

    def test_get_display_name(self):
        req = Requirement(filename="user_login_flow.pdf", content="test")
        assert req.get_display_name() == "User Login Flow"

    def test_get_content_preview_short(self):
        req = Requirement(filename="t.txt", content="short content")
        assert req.get_content_preview() == "short content"

    def test_get_content_preview_long(self):
        req = Requirement(filename="t.txt", content="x" * 1000)
        preview = req.get_content_preview(max_chars=100)
        assert len(preview) == 103  # 100 chars + "..."
        assert preview.endswith("...")

    def test_get_stats(self, sample_requirement):
        stats = sample_requirement.get_stats()
        assert stats["filename"] == "login_requirements.txt"
        assert stats["file_type"] == "txt"
        assert stats["word_count"] > 0
        assert stats["char_count"] > 0
        assert stats["line_count"] > 0


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class TestEnums:
    """Tests for model enums."""

    def test_priority_values(self):
        assert Priority.HIGH.value == "High"
        assert Priority.MEDIUM.value == "Medium"
        assert Priority.LOW.value == "Low"

    def test_status_values(self):
        assert TestStatus.NEW.value == "New"
        assert TestStatus.PASSED.value == "Passed"
        assert TestStatus.FAILED.value == "Failed"

    def test_category_values(self):
        assert TestCategory.FUNCTIONAL.value == "Functional"
        assert TestCategory.NEGATIVE.value == "Negative"
        assert TestCategory.EDGE_CASE.value == "Edge Case"
