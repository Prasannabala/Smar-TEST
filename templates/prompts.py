"""
Prompt templates for test case generation.
Optimized for local LLM models (faster response times).
"""

class PromptTemplates:
    """
    Collection of prompt templates for different generation tasks.
    """

    # System prompt - concise version for faster processing
    SYSTEM_PROMPT = """You are an expert QA Engineer. Generate comprehensive test cases in valid JSON format.
Always include: positive tests, negative tests, edge cases, and boundary tests.
Assign priority (High/Medium/Low) based on business impact."""

    # Manual test case generation prompt - optimized for speed
    MANUAL_TEST_GENERATION = """Generate manual test cases for these requirements:

{requirements}

{client_context}

Return ONLY valid JSON in this exact format:
{{
  "test_cases": [
    {{
      "test_id": "TC_001",
      "test_name": "Brief descriptive name",
      "description": "What this test verifies",
      "preconditions": ["condition1", "condition2"],
      "test_steps": [
        {{"step_number": 1, "action": "Do something", "test_data": "data", "expected_result": "Result"}}
      ],
      "expected_results": ["Final outcome 1", "Final outcome 2"],
      "priority": "High",
      "category": "Functional",
      "tags": ["tag1", "tag2"]
    }}
  ]
}}

Generate 5-10 test cases covering:
{additional_instructions}

Return ONLY the JSON, no other text."""

    # Gherkin generation prompt
    GHERKIN_GENERATION = """Convert these test cases to Gherkin format:

{manual_tests}

Requirements: {requirements_summary}

Return ONLY valid JSON:
{{
  "feature_files": [
    {{
      "filename": "feature_name.feature",
      "feature_name": "Feature Name",
      "content": "Feature: Name\\n  Scenario: Test\\n    Given...\\n    When...\\n    Then...",
      "scenario_count": 3,
      "related_test_ids": ["TC_001"]
    }}
  ]
}}

Return ONLY the JSON, no other text."""

    # Selenium generation prompt
    SELENIUM_GENERATION = """Generate Selenium Python tests for:

{manual_tests}

Return ONLY valid JSON:
{{
  "scripts": [
    {{
      "filename": "test_feature.py",
      "content": "import pytest\\nfrom selenium import webdriver\\n\\nclass TestFeature:\\n    def test_case(self):\\n        pass",
      "related_test_ids": ["TC_001"],
      "description": "Feature tests"
    }}
  ]
}}

Use pytest, explicit waits, Page Object Model. Return ONLY JSON."""

    # Playwright generation prompt
    PLAYWRIGHT_GENERATION = """Generate Playwright JavaScript tests for:

{manual_tests}

Return ONLY valid JSON:
{{
  "scripts": [
    {{
      "filename": "feature.spec.js",
      "content": "const {{ test, expect }} = require('@playwright/test');\\n\\ntest('test name', async ({{ page }}) => {{\\n  // test code\\n}});",
      "related_test_ids": ["TC_001"],
      "description": "Feature tests"
    }}
  ]
}}

Use @playwright/test, async/await, proper locators. Return ONLY JSON."""

    # Enhancement prompt
    ENHANCE_TESTS = """Add missing test cases to this list:

{current_tests}

Requirements: {requirements}

Add ONLY new tests not already covered. Return JSON:
{{
  "additional_tests": [
    {{"test_id": "TC_NEW", "test_name": "...", "description": "...", "preconditions": [], "test_steps": [], "expected_results": [], "priority": "Medium", "category": "Edge Case", "tags": []}}
  ]
}}

Return ONLY JSON."""

    @classmethod
    def get_manual_test_prompt(cls, requirements: str, client_context: str = "",
                                include_edge_cases: bool = True,
                                include_negative: bool = True,
                                include_boundary: bool = True) -> str:
        """Build the manual test generation prompt with options."""
        instructions = []
        instructions.append("- Positive/functional tests")
        if include_negative:
            instructions.append("- Negative tests (invalid inputs, errors)")
        if include_edge_cases:
            instructions.append("- Edge cases")
        if include_boundary:
            instructions.append("- Boundary value tests")

        additional = "\n".join(instructions)

        context = ""
        if client_context and client_context.strip():
            context = f"\nClient context:\n{client_context[:1000]}"  # Limit context size

        # Limit requirements to prevent token overflow
        req_text = requirements[:3000] if len(requirements) > 3000 else requirements

        return cls.MANUAL_TEST_GENERATION.format(
            requirements=req_text,
            client_context=context,
            additional_instructions=additional
        )

    @classmethod
    def get_gherkin_prompt(cls, manual_tests: str, requirements_summary: str,
                           client_context: str = "") -> str:
        """Build the Gherkin generation prompt."""
        # Limit input sizes
        tests = manual_tests[:2000] if len(manual_tests) > 2000 else manual_tests
        summary = requirements_summary[:500] if len(requirements_summary) > 500 else requirements_summary

        return cls.GHERKIN_GENERATION.format(
            manual_tests=tests,
            requirements_summary=summary
        )

    @classmethod
    def get_selenium_prompt(cls, manual_tests: str, requirements_summary: str,
                            client_context: str = "") -> str:
        """Build the Selenium generation prompt."""
        tests = manual_tests[:2000] if len(manual_tests) > 2000 else manual_tests

        return cls.SELENIUM_GENERATION.format(
            manual_tests=tests,
            requirements_summary=requirements_summary[:500]
        )

    @classmethod
    def get_playwright_prompt(cls, manual_tests: str, requirements_summary: str,
                              client_context: str = "") -> str:
        """Build the Playwright generation prompt."""
        tests = manual_tests[:2000] if len(manual_tests) > 2000 else manual_tests

        return cls.PLAYWRIGHT_GENERATION.format(
            manual_tests=tests,
            requirements_summary=requirements_summary[:500]
        )

    @classmethod
    def get_enhancement_prompt(cls, current_tests: str, requirements: str,
                               client_context: str = "") -> str:
        """Build the test enhancement prompt."""
        tests = current_tests[:1500] if len(current_tests) > 1500 else current_tests
        reqs = requirements[:1000] if len(requirements) > 1000 else requirements

        return cls.ENHANCE_TESTS.format(
            current_tests=tests,
            requirements=reqs
        )
