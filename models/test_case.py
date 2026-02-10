"""
Test case data models for manual tests and automation scripts.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum


class Priority(Enum):
    """Test case priority levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TestStatus(Enum):
    """Test case execution status."""
    NEW = "New"
    IN_PROGRESS = "In Progress"
    PASSED = "Passed"
    FAILED = "Failed"
    BLOCKED = "Blocked"
    SKIPPED = "Skipped"


class TestCategory(Enum):
    """Test case categories."""
    FUNCTIONAL = "Functional"
    UI = "UI"
    INTEGRATION = "Integration"
    REGRESSION = "Regression"
    SMOKE = "Smoke"
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    USABILITY = "Usability"
    EDGE_CASE = "Edge Case"
    NEGATIVE = "Negative"
    BOUNDARY = "Boundary"


@dataclass
class TestStep:
    """
    Represents a single test step.
    """
    step_number: int
    action: str
    test_data: str = ""
    expected_result: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestStep':
        return cls(**data)

    def to_text(self) -> str:
        """Format step as readable text."""
        text = f"Step {self.step_number}: {self.action}"
        if self.test_data:
            text += f"\n   Test Data: {self.test_data}"
        if self.expected_result:
            text += f"\n   Expected: {self.expected_result}"
        return text


@dataclass
class ManualTestCase:
    """
    Represents a manual test case with full details.
    """
    test_id: str
    test_name: str
    description: str
    preconditions: List[str] = field(default_factory=list)
    test_steps: List[TestStep] = field(default_factory=list)
    expected_results: List[str] = field(default_factory=list)
    priority: str = Priority.MEDIUM.value
    category: str = TestCategory.FUNCTIONAL.value
    status: str = TestStatus.NEW.value
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['test_steps'] = [step.to_dict() if isinstance(step, TestStep) else step
                              for step in self.test_steps]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ManualTestCase':
        """Create from dictionary."""
        steps_data = data.pop('test_steps', [])
        test_steps = []
        for step in steps_data:
            if isinstance(step, dict):
                test_steps.append(TestStep.from_dict(step))
            else:
                test_steps.append(step)
        data['test_steps'] = test_steps
        return cls(**data)

    def to_text(self) -> str:
        """Format test case as readable text."""
        lines = [
            f"{'='*60}",
            f"TEST CASE: {self.test_id}",
            f"{'='*60}",
            f"TEST NAME: {self.test_name}",
            f"",
            f"DESCRIPTION:",
            f"  {self.description}",
            f"",
            f"PRIORITY: {self.priority}",
            f"CATEGORY: {self.category}",
            f"STATUS: {self.status}",
        ]

        if self.tags:
            lines.append(f"TAGS: {', '.join(self.tags)}")

        lines.append("")
        lines.append("PRECONDITIONS:")
        for pre in self.preconditions:
            lines.append(f"  - {pre}")

        lines.append("")
        lines.append("TEST STEPS:")
        for step in self.test_steps:
            lines.append(f"  {step.to_text()}")

        lines.append("")
        lines.append("EXPECTED RESULTS:")
        for i, result in enumerate(self.expected_results, 1):
            lines.append(f"  {i}. {result}")

        if self.notes:
            lines.append("")
            lines.append(f"NOTES: {self.notes}")

        lines.append(f"{'='*60}")

        return '\n'.join(lines)

    def get_steps_text(self) -> str:
        """Get all steps as formatted text for export."""
        return '\n'.join([
            f"{s.step_number}. {s.action}" + (f" [Data: {s.test_data}]" if s.test_data else "")
            for s in self.test_steps
        ])

    def get_expected_results_text(self) -> str:
        """Get all expected results as formatted text for export."""
        return '\n'.join([f"{i+1}. {r}" for i, r in enumerate(self.expected_results)])

    def get_preconditions_text(self) -> str:
        """Get preconditions as formatted text for export."""
        return '\n'.join([f"- {p}" for p in self.preconditions])


@dataclass
class AutomationScript:
    """
    Represents an automation script (Gherkin, Selenium, Playwright).
    """
    script_type: str  # "gherkin", "selenium", "playwright"
    filename: str
    content: str
    related_test_ids: List[str] = field(default_factory=list)
    feature_name: str = ""
    scenario_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationScript':
        return cls(**data)

    def get_extension(self) -> str:
        """Get file extension for this script type."""
        extensions = {
            "gherkin": "feature",
            "selenium": "py",
            "playwright": "spec.js"
        }
        return extensions.get(self.script_type, "txt")


@dataclass
class TestSuite:
    """
    Collection of test cases and automation scripts.
    """
    name: str
    description: str = ""
    manual_tests: List[ManualTestCase] = field(default_factory=list)
    gherkin_scripts: List[AutomationScript] = field(default_factory=list)
    selenium_scripts: List[AutomationScript] = field(default_factory=list)
    playwright_scripts: List[AutomationScript] = field(default_factory=list)

    # Metadata
    client_name: str = ""
    requirement_source: str = ""
    generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'manual_tests': [t.to_dict() for t in self.manual_tests],
            'gherkin_scripts': [s.to_dict() for s in self.gherkin_scripts],
            'selenium_scripts': [s.to_dict() for s in self.selenium_scripts],
            'playwright_scripts': [s.to_dict() for s in self.playwright_scripts],
            'client_name': self.client_name,
            'requirement_source': self.requirement_source,
            'generated_at': self.generated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestSuite':
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            manual_tests=[ManualTestCase.from_dict(t) for t in data.get('manual_tests', [])],
            gherkin_scripts=[AutomationScript.from_dict(s) for s in data.get('gherkin_scripts', [])],
            selenium_scripts=[AutomationScript.from_dict(s) for s in data.get('selenium_scripts', [])],
            playwright_scripts=[AutomationScript.from_dict(s) for s in data.get('playwright_scripts', [])],
            client_name=data.get('client_name', ''),
            requirement_source=data.get('requirement_source', ''),
            generated_at=data.get('generated_at', ''),
        )

    def get_summary(self) -> Dict[str, int]:
        """Get count summary of all test types."""
        return {
            'manual_tests': len(self.manual_tests),
            'gherkin_scenarios': sum(s.scenario_count for s in self.gherkin_scripts),
            'selenium_tests': len(self.selenium_scripts),
            'playwright_tests': len(self.playwright_scripts),
        }

    def get_total_count(self) -> int:
        """Get total number of tests."""
        summary = self.get_summary()
        return sum(summary.values())
