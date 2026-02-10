"""
Tests for LLM prompt templates (templates/prompts.py).
"""
import pytest

from templates.prompts import PromptTemplates


class TestPromptTemplates:
    """Tests for prompt template generation."""

    def test_manual_test_prompt_basic(self):
        prompt = PromptTemplates.get_manual_test_prompt(
            requirements="Users must log in with email and password"
        )
        assert "Users must log in" in prompt
        assert "test_cases" in prompt
        assert "JSON" in prompt

    def test_manual_test_prompt_with_all_options(self):
        prompt = PromptTemplates.get_manual_test_prompt(
            requirements="Feature requirements text",
            client_context="Acme Corp portal context",
            include_edge_cases=True,
            include_negative=True,
            include_boundary=True
        )
        assert "Edge cases" in prompt
        assert "Negative tests" in prompt
        assert "Boundary value" in prompt
        assert "Acme Corp" in prompt

    def test_manual_test_prompt_without_options(self):
        prompt = PromptTemplates.get_manual_test_prompt(
            requirements="Requirements",
            include_edge_cases=False,
            include_negative=False,
            include_boundary=False
        )
        assert "Positive/functional" in prompt
        assert "Edge cases" not in prompt

    def test_manual_test_prompt_truncates_long_requirements(self):
        long_req = "x" * 5000
        prompt = PromptTemplates.get_manual_test_prompt(requirements=long_req)
        # Should truncate to 3000 chars
        assert len(prompt) < len(long_req) + 1000

    def test_manual_test_prompt_truncates_context(self):
        long_context = "y" * 2000
        prompt = PromptTemplates.get_manual_test_prompt(
            requirements="Short req", client_context=long_context
        )
        # Context is truncated to ~1000 chars (plus prefix "Client context:\n")
        assert prompt.count("y") <= 1010
        assert prompt.count("y") < 2000  # Definitely truncated from original

    def test_gherkin_prompt(self):
        prompt = PromptTemplates.get_gherkin_prompt(
            manual_tests='[{"test_id": "TC_001"}]',
            requirements_summary="Login feature"
        )
        assert "Gherkin" in prompt
        assert "feature_files" in prompt
        assert "Scenario" in prompt

    def test_selenium_prompt(self):
        prompt = PromptTemplates.get_selenium_prompt(
            manual_tests='[{"test_id": "TC_001"}]',
            requirements_summary="Login"
        )
        assert "Selenium" in prompt
        assert "scripts" in prompt
        assert "pytest" in prompt

    def test_playwright_prompt(self):
        prompt = PromptTemplates.get_playwright_prompt(
            manual_tests='[{"test_id": "TC_001"}]',
            requirements_summary="Login"
        )
        assert "Playwright" in prompt
        assert "scripts" in prompt
        assert "@playwright/test" in prompt

    def test_enhancement_prompt(self):
        prompt = PromptTemplates.get_enhancement_prompt(
            current_tests='[{"test_id": "TC_001"}]',
            requirements="New feature requirements"
        )
        assert "additional_tests" in prompt
        assert "not already covered" in prompt

    def test_system_prompt_exists(self):
        assert len(PromptTemplates.SYSTEM_PROMPT) > 0
        assert "QA" in PromptTemplates.SYSTEM_PROMPT

    def test_all_prompts_request_json(self):
        """Every prompt template should ask for JSON output."""
        assert "JSON" in PromptTemplates.MANUAL_TEST_GENERATION
        assert "JSON" in PromptTemplates.GHERKIN_GENERATION
        assert "JSON" in PromptTemplates.SELENIUM_GENERATION
        assert "JSON" in PromptTemplates.PLAYWRIGHT_GENERATION
        assert "JSON" in PromptTemplates.ENHANCE_TESTS
