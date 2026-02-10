"""
Shared pytest fixtures for the Test Case Generation Agent test suite.
"""
import os
import io
import json
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime

import pytest

# Ensure we can import application modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.test_case import (
    TestStep, ManualTestCase, AutomationScript, TestSuite,
    Priority, TestStatus, TestCategory
)
from models.requirement import Requirement
from models.client_context import ClientContext
from storage.database import Database
from config.settings import Settings


# ──────────────────────────────────────────────
# Test Data Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def sample_test_step():
    """A single test step."""
    return TestStep(
        step_number=1,
        action="Navigate to the login page",
        test_data="URL: https://example.com/login",
        expected_result="Login page loads successfully"
    )


@pytest.fixture
def sample_test_steps():
    """A list of test steps for a login test."""
    return [
        TestStep(1, "Open browser and navigate to login page", "URL: /login", "Login page displayed"),
        TestStep(2, "Enter valid username", "user: admin", "Username field populated"),
        TestStep(3, "Enter valid password", "pass: Admin@123", "Password field populated (masked)"),
        TestStep(4, "Click Login button", "", "User is logged in and redirected to dashboard"),
    ]


@pytest.fixture
def sample_manual_test(sample_test_steps):
    """A complete manual test case."""
    return ManualTestCase(
        test_id="TC_001",
        test_name="Verify successful login with valid credentials",
        description="Test that a user can log in with correct username and password",
        preconditions=["User account exists", "Application is accessible"],
        test_steps=sample_test_steps,
        expected_results=["User sees dashboard", "Welcome message displayed"],
        priority=Priority.HIGH.value,
        category=TestCategory.FUNCTIONAL.value,
        status=TestStatus.NEW.value,
        tags=["login", "authentication", "smoke"]
    )


@pytest.fixture
def sample_manual_tests(sample_test_steps):
    """Multiple manual test cases."""
    return [
        ManualTestCase(
            test_id="TC_001",
            test_name="Valid login",
            description="Login with valid credentials",
            preconditions=["User exists"],
            test_steps=sample_test_steps,
            expected_results=["Dashboard displayed"],
            priority="High",
            category="Functional",
            tags=["login", "smoke"]
        ),
        ManualTestCase(
            test_id="TC_002",
            test_name="Invalid login",
            description="Login with invalid credentials",
            preconditions=["User exists"],
            test_steps=[
                TestStep(1, "Navigate to login", "", "Page loads"),
                TestStep(2, "Enter wrong password", "pass: wrong", "Error shown"),
            ],
            expected_results=["Error message displayed"],
            priority="High",
            category="Negative",
            tags=["login", "negative"]
        ),
        ManualTestCase(
            test_id="TC_003",
            test_name="Empty fields validation",
            description="Submit login form with empty fields",
            preconditions=[],
            test_steps=[
                TestStep(1, "Navigate to login", "", "Page loads"),
                TestStep(2, "Click login without entering data", "", "Validation error"),
            ],
            expected_results=["Validation error for required fields"],
            priority="Medium",
            category="Boundary",
            tags=["login", "validation"]
        ),
    ]


@pytest.fixture
def sample_gherkin_script():
    """A sample Gherkin feature file."""
    return AutomationScript(
        script_type="gherkin",
        filename="login.feature",
        content=(
            "Feature: User Login\n"
            "  Scenario: Successful login\n"
            "    Given the user is on the login page\n"
            "    When they enter valid credentials\n"
            "    Then they should see the dashboard\n"
        ),
        related_test_ids=["TC_001"],
        feature_name="User Login",
        scenario_count=1
    )


@pytest.fixture
def sample_selenium_script():
    """A sample Selenium Python test script."""
    return AutomationScript(
        script_type="selenium",
        filename="test_login.py",
        content=(
            "import pytest\n"
            "from selenium import webdriver\n\n"
            "class TestLogin:\n"
            "    def test_valid_login(self, driver):\n"
            "        driver.get('/login')\n"
            "        assert 'Dashboard' in driver.title\n"
        ),
        related_test_ids=["TC_001"],
        feature_name="Login Tests",
        scenario_count=1
    )


@pytest.fixture
def sample_playwright_script():
    """A sample Playwright JavaScript test spec."""
    return AutomationScript(
        script_type="playwright",
        filename="login.spec.js",
        content=(
            "const { test, expect } = require('@playwright/test');\n\n"
            "test('valid login', async ({ page }) => {\n"
            "  await page.goto('/login');\n"
            "  await expect(page).toHaveTitle(/Dashboard/);\n"
            "});\n"
        ),
        related_test_ids=["TC_001"],
        feature_name="Login Tests",
        scenario_count=1
    )


@pytest.fixture
def sample_test_suite(sample_manual_tests, sample_gherkin_script, sample_selenium_script, sample_playwright_script):
    """A complete test suite with all artifact types."""
    return TestSuite(
        name="Login Feature Tests",
        description="Test suite for login functionality",
        manual_tests=sample_manual_tests,
        gherkin_scripts=[sample_gherkin_script],
        selenium_scripts=[sample_selenium_script],
        playwright_scripts=[sample_playwright_script],
        client_name="Acme Corp",
        requirement_source="login_requirements.txt",
        generated_at=datetime.now().isoformat()
    )


@pytest.fixture
def sample_requirement():
    """A sample requirement document."""
    return Requirement(
        filename="login_requirements.txt",
        content=(
            "Login Feature Requirements\n\n"
            "1. Users must be able to log in with email and password\n"
            "2. Invalid credentials should show an error message\n"
            "3. Password must be at least 8 characters\n"
            "4. Account locks after 5 failed attempts\n"
            "5. Session expires after 30 minutes of inactivity\n"
        ),
        file_type="txt",
        word_count=42,
        page_count=1
    )


@pytest.fixture
def sample_client_context():
    """A sample client context."""
    return ClientContext(
        id="client001",
        name="Acme Corp",
        project_name="Acme Portal",
        project_description="Customer-facing web portal",
        tech_stack=["React", "Python", "PostgreSQL"],
        test_environment="Chrome 120, Windows 11",
        navigation_rules=["Always start from home page", "Use breadcrumbs for navigation"],
        thumb_rules=["Test on both desktop and mobile", "Include accessibility checks"],
        business_rules=["Users must verify email before access", "Premium users have extended session"],
        best_practices=["Follow AAA pattern in tests", "Use meaningful test names"]
    )


# ──────────────────────────────────────────────
# Database Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_app.db"
    db = Database(db_path=db_path)
    return db


# ──────────────────────────────────────────────
# Settings Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def default_settings():
    """Default application settings."""
    return Settings()


# ──────────────────────────────────────────────
# File Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def sample_txt_file():
    """A sample text file as bytes."""
    content = b"Login Feature Requirements\n\nUsers must be able to log in with email and password.\n"
    return io.BytesIO(content)


@pytest.fixture
def sample_txt_path(tmp_path):
    """A sample text file on disk."""
    file_path = tmp_path / "requirements.txt"
    file_path.write_text(
        "Login Feature Requirements\n\n"
        "1. Users must log in with email and password\n"
        "2. Invalid credentials show an error\n"
    )
    return file_path
