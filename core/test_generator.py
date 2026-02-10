"""
Test Generation Engine - Core logic for generating test cases.
"""
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Generator, Callable
from dataclasses import dataclass

from core.llm_adapter import LLMAdapter, get_llm_adapter, get_code_llm_adapter
from models.test_case import ManualTestCase, TestStep, AutomationScript, TestSuite
from models.client_context import ClientContext
from models.requirement import Requirement
from templates.prompts import PromptTemplates
from config.settings import get_settings


@dataclass
class GenerationProgress:
    """Tracks generation progress."""
    stage: str
    progress: float  # 0.0 to 1.0
    message: str
    completed: bool = False
    error: Optional[str] = None


class TestGenerator:
    """
    Main test generation engine that orchestrates the entire process.
    Uses the main model for manual tests and Gherkin,
    and CodeLlama for Selenium/Playwright code generation.
    """

    def __init__(self, llm_adapter: Optional[LLMAdapter] = None):
        self.llm = llm_adapter or get_llm_adapter()
        self.code_llm = get_code_llm_adapter()  # Specialized for code generation
        self.settings = get_settings()

    def generate_test_suite(
        self,
        requirement: Requirement,
        client_context: Optional[ClientContext] = None,
        generate_gherkin: bool = False,
        generate_selenium: bool = False,
        generate_playwright: bool = False,
        include_edge_cases: bool = True,
        include_negative: bool = True,
        include_boundary: bool = True,
        progress_callback: Optional[Callable[[GenerationProgress], None]] = None
    ) -> TestSuite:
        """
        Generate a complete test suite from requirements.

        Args:
            requirement: Parsed requirement document
            client_context: Optional client context for customization
            generate_gherkin: Whether to generate Gherkin scripts
            generate_selenium: Whether to generate Selenium scripts
            generate_playwright: Whether to generate Playwright scripts
            include_edge_cases: Include edge case tests
            include_negative: Include negative tests
            include_boundary: Include boundary tests
            progress_callback: Callback function for progress updates

        Returns:
            TestSuite with all generated tests
        """
        def report_progress(stage: str, progress: float, message: str):
            if progress_callback:
                progress_callback(GenerationProgress(stage, progress, message))

        # Initialize test suite
        suite = TestSuite(
            name=requirement.get_display_name(),
            description=f"Test suite generated from {requirement.filename}",
            client_name=client_context.name if client_context else "",
            requirement_source=requirement.filename,
            generated_at=datetime.now().isoformat()
        )

        # Get client context text
        context_text = client_context.get_context_text() if client_context else ""

        # Calculate total steps for accurate progress tracking
        total_steps = 1  # Manual tests (always)
        if generate_gherkin:
            total_steps += 1
        if generate_selenium:
            total_steps += 1
        if generate_playwright:
            total_steps += 1
        current_step = 0

        def step_progress(step_name: str, sub_stage: str, sub_progress: float):
            """Calculate overall progress based on current step and sub-progress."""
            base = current_step / total_steps
            step_size = 1.0 / total_steps
            overall = base + (step_size * sub_progress)
            report_progress(step_name, min(overall, 0.99), sub_stage)

        try:
            # ── Stage 1: Generate Manual Test Cases (Always) ──
            step_progress("manual", f"📄 Reading requirements document: {requirement.filename}...", 0.0)

            step_progress("manual", "🔍 Analyzing requirements and identifying test scenarios...", 0.15)

            step_progress("manual", f"🤖 Sending to LLM ({self.settings.ollama_model if hasattr(self.settings, 'ollama_model') else 'model'}) for manual test case generation...", 0.25)

            manual_tests = self._generate_manual_tests(
                requirement.content,
                context_text,
                include_edge_cases,
                include_negative,
                include_boundary
            )
            suite.manual_tests = manual_tests

            step_progress("manual", f"✅ Generated {len(manual_tests)} manual test cases — parsing results...", 0.9)

            if not manual_tests:
                step_progress("manual", "⚠️ Warning: No manual tests were parsed from LLM response. Check model output.", 1.0)

            current_step = 1

            # Prepare manual tests summary for automation generation
            manual_tests_json = json.dumps([t.to_dict() for t in manual_tests[:10]], indent=2)
            requirements_summary = requirement.content[:2000]
            tests_count_info = f"(based on {len(manual_tests)} manual tests)"

            # ── Stage 2: Generate Gherkin (if requested) ──
            if generate_gherkin:
                step_progress("gherkin", f"📝 Preparing Gherkin BDD feature file generation {tests_count_info}...", 0.0)

                step_progress("gherkin", f"🤖 Sending to LLM for Gherkin conversion — converting manual tests to Given/When/Then format...", 0.2)

                gherkin_scripts = self._generate_gherkin(
                    manual_tests_json,
                    requirements_summary,
                    context_text
                )
                suite.gherkin_scripts = gherkin_scripts

                if gherkin_scripts:
                    total_scenarios = sum(s.scenario_count for s in gherkin_scripts)
                    step_progress("gherkin", f"✅ Generated {len(gherkin_scripts)} Gherkin feature file(s) with {total_scenarios} scenarios", 0.95)
                else:
                    step_progress("gherkin", "⚠️ Gherkin generation returned empty — LLM response could not be parsed into feature files", 0.95)

                current_step += 1

            # ── Stage 3: Generate Selenium (if requested) ──
            if generate_selenium:
                code_model_name = getattr(self.settings, 'ollama_code_model', 'codellama:7b')
                step_progress("selenium", f"🐍 Preparing Selenium Python script generation {tests_count_info}...", 0.0)

                step_progress("selenium", f"🤖 Sending to CodeLlama ({code_model_name}) — generating pytest + Selenium scripts with Page Object Model...", 0.2)

                selenium_scripts = self._generate_selenium(
                    manual_tests_json,
                    requirements_summary,
                    context_text
                )
                suite.selenium_scripts = selenium_scripts

                if selenium_scripts:
                    step_progress("selenium", f"✅ Generated {len(selenium_scripts)} Selenium Python test script(s)", 0.95)
                else:
                    step_progress("selenium", "⚠️ Selenium generation returned empty — CodeLlama response could not be parsed", 0.95)

                current_step += 1

            # ── Stage 4: Generate Playwright (if requested) ──
            if generate_playwright:
                code_model_name = getattr(self.settings, 'ollama_code_model', 'codellama:7b')
                step_progress("playwright", f"🎭 Preparing Playwright JavaScript test generation {tests_count_info}...", 0.0)

                step_progress("playwright", f"🤖 Sending to CodeLlama ({code_model_name}) — generating @playwright/test specs with async/await...", 0.2)

                playwright_scripts = self._generate_playwright(
                    manual_tests_json,
                    requirements_summary,
                    context_text
                )
                suite.playwright_scripts = playwright_scripts

                if playwright_scripts:
                    step_progress("playwright", f"✅ Generated {len(playwright_scripts)} Playwright test spec(s)", 0.95)
                else:
                    step_progress("playwright", "⚠️ Playwright generation returned empty — CodeLlama response could not be parsed", 0.95)

                current_step += 1

            # ── Final Summary ──
            total_items = len(suite.manual_tests)
            summary_parts = [f"{total_items} manual tests"]
            if generate_gherkin:
                summary_parts.append(f"{len(suite.gherkin_scripts)} Gherkin files")
            if generate_selenium:
                summary_parts.append(f"{len(suite.selenium_scripts)} Selenium scripts")
            if generate_playwright:
                summary_parts.append(f"{len(suite.playwright_scripts)} Playwright specs")

            report_progress("complete", 1.0, f"🎉 Complete! Generated {', '.join(summary_parts)}")

        except Exception as e:
            if progress_callback:
                progress_callback(GenerationProgress(
                    "error", 0, "Generation failed", completed=True, error=str(e)
                ))
            raise

        return suite

    def _generate_manual_tests(
        self,
        requirements: str,
        client_context: str,
        include_edge_cases: bool,
        include_negative: bool,
        include_boundary: bool
    ) -> List[ManualTestCase]:
        """Generate manual test cases from requirements."""
        prompt = PromptTemplates.get_manual_test_prompt(
            requirements=requirements,
            client_context=client_context,
            include_edge_cases=include_edge_cases,
            include_negative=include_negative,
            include_boundary=include_boundary
        )

        response = self.llm.generate(prompt, PromptTemplates.SYSTEM_PROMPT)
        return self._parse_manual_tests(response)

    def _generate_gherkin(
        self,
        manual_tests: str,
        requirements_summary: str,
        client_context: str
    ) -> List[AutomationScript]:
        """Generate Gherkin feature files."""
        prompt = PromptTemplates.get_gherkin_prompt(
            manual_tests=manual_tests,
            requirements_summary=requirements_summary,
            client_context=client_context
        )

        response = self.llm.generate(prompt, PromptTemplates.SYSTEM_PROMPT)
        return self._parse_gherkin_scripts(response)

    def _generate_selenium(
        self,
        manual_tests: str,
        requirements_summary: str,
        client_context: str
    ) -> List[AutomationScript]:
        """Generate Selenium Python scripts using CodeLlama if available."""
        prompt = PromptTemplates.get_selenium_prompt(
            manual_tests=manual_tests,
            requirements_summary=requirements_summary,
            client_context=client_context
        )

        # Use code-optimized model for Selenium generation
        response = self.code_llm.generate(prompt, PromptTemplates.SYSTEM_PROMPT)
        return self._parse_automation_scripts(response, "selenium")

    def _generate_playwright(
        self,
        manual_tests: str,
        requirements_summary: str,
        client_context: str
    ) -> List[AutomationScript]:
        """Generate Playwright JavaScript scripts using CodeLlama if available."""
        prompt = PromptTemplates.get_playwright_prompt(
            manual_tests=manual_tests,
            requirements_summary=requirements_summary,
            client_context=client_context
        )

        # Use code-optimized model for Playwright generation
        response = self.code_llm.generate(prompt, PromptTemplates.SYSTEM_PROMPT)
        return self._parse_automation_scripts(response, "playwright")

    def _parse_manual_tests(self, response: str) -> List[ManualTestCase]:
        """Parse LLM response into ManualTestCase objects."""
        tests = []

        try:
            # Try to extract JSON from response
            json_data = self._extract_json(response)

            if json_data and 'test_cases' in json_data:
                for tc_data in json_data['test_cases']:
                    try:
                        # Parse test steps
                        steps = []
                        for step_data in tc_data.get('test_steps', []):
                            steps.append(TestStep(
                                step_number=step_data.get('step_number', len(steps) + 1),
                                action=step_data.get('action', ''),
                                test_data=step_data.get('test_data', ''),
                                expected_result=step_data.get('expected_result', '')
                            ))

                        test = ManualTestCase(
                            test_id=tc_data.get('test_id', f'TC_{len(tests)+1:03d}'),
                            test_name=tc_data.get('test_name', 'Unnamed Test'),
                            description=tc_data.get('description', ''),
                            preconditions=tc_data.get('preconditions', []),
                            test_steps=steps,
                            expected_results=tc_data.get('expected_results', []),
                            priority=tc_data.get('priority', 'Medium'),
                            category=tc_data.get('category', 'Functional'),
                            tags=tc_data.get('tags', [])
                        )
                        tests.append(test)
                    except Exception as e:
                        print(f"Warning: Failed to parse test case: {e}")
                        continue

        except Exception as e:
            print(f"Warning: Failed to parse JSON response: {e}")
            # Fall back to creating a basic test case
            tests.append(ManualTestCase(
                test_id="TC_001",
                test_name="Manual Review Required",
                description="The LLM response could not be parsed. Please review the raw output.",
                preconditions=["Review LLM output"],
                test_steps=[TestStep(1, "Review raw LLM response", "", "")],
                expected_results=["Test cases extracted manually"],
                priority="High",
                category="Functional"
            ))

        return tests

    def _parse_gherkin_scripts(self, response: str) -> List[AutomationScript]:
        """Parse LLM response into Gherkin AutomationScript objects."""
        scripts = []

        try:
            json_data = self._extract_json(response)

            if json_data and 'feature_files' in json_data:
                for ff_data in json_data['feature_files']:
                    content = ff_data.get('content', '')
                    if content:  # Only add if there's actual content
                        script = AutomationScript(
                            script_type="gherkin",
                            filename=ff_data.get('filename', 'feature.feature'),
                            content=content,
                            related_test_ids=ff_data.get('related_test_ids', []),
                            feature_name=ff_data.get('feature_name', ''),
                            scenario_count=ff_data.get('scenario_count', 0)
                        )
                        scripts.append(script)
            elif json_data and 'scripts' in json_data:
                # Some models return gherkin under 'scripts' key instead
                for script_data in json_data['scripts']:
                    content = script_data.get('content', '')
                    if content:
                        script = AutomationScript(
                            script_type="gherkin",
                            filename=script_data.get('filename', 'feature.feature'),
                            content=content,
                            related_test_ids=script_data.get('related_test_ids', []),
                            feature_name=script_data.get('feature_name', script_data.get('description', '')),
                            scenario_count=script_data.get('scenario_count', 0)
                        )
                        scripts.append(script)

        except Exception as e:
            print(f"Warning: Failed to parse Gherkin JSON response: {e}")

        # Fallback: extract raw Gherkin feature content from response
        if not scripts:
            scripts = self._extract_raw_gherkin(response)

        return scripts

    def _extract_raw_gherkin(self, response: str) -> List[AutomationScript]:
        """Fallback: extract Gherkin feature blocks directly from raw LLM response text."""
        scripts = []
        # Look for Feature: blocks in the raw response
        feature_pattern = re.compile(
            r'(Feature:.*?)(?=\nFeature:|\Z)',
            re.DOTALL
        )
        matches = feature_pattern.findall(response)

        for i, match in enumerate(matches):
            content = match.strip()
            if content and 'Scenario' in content:
                # Extract feature name
                feature_name_match = re.match(r'Feature:\s*(.+)', content)
                feature_name = feature_name_match.group(1).strip() if feature_name_match else f"Feature {i+1}"
                # Count scenarios
                scenario_count = len(re.findall(r'Scenario(?:\s+Outline)?:', content))

                filename = re.sub(r'[^a-zA-Z0-9_]', '_', feature_name.lower())[:50] + '.feature'
                scripts.append(AutomationScript(
                    script_type="gherkin",
                    filename=filename,
                    content=content,
                    related_test_ids=[],
                    feature_name=feature_name,
                    scenario_count=scenario_count
                ))

        return scripts

    def _parse_automation_scripts(self, response: str, script_type: str) -> List[AutomationScript]:
        """Parse LLM response into AutomationScript objects."""
        scripts = []

        try:
            json_data = self._extract_json(response)

            if json_data and 'scripts' in json_data:
                for script_data in json_data['scripts']:
                    content = script_data.get('content', '')
                    if content:  # Only add if there's actual content
                        script = AutomationScript(
                            script_type=script_type,
                            filename=script_data.get('filename', f'test.{script_type}'),
                            content=content,
                            related_test_ids=script_data.get('related_test_ids', []),
                            feature_name=script_data.get('description', '')
                        )
                        scripts.append(script)
            elif json_data and 'feature_files' in json_data:
                # Some models might use feature_files key for any script type
                for script_data in json_data['feature_files']:
                    content = script_data.get('content', '')
                    if content:
                        script = AutomationScript(
                            script_type=script_type,
                            filename=script_data.get('filename', f'test.{script_type}'),
                            content=content,
                            related_test_ids=script_data.get('related_test_ids', []),
                            feature_name=script_data.get('description', script_data.get('feature_name', ''))
                        )
                        scripts.append(script)

        except Exception as e:
            print(f"Warning: Failed to parse {script_type} JSON response: {e}")

        # Fallback: extract raw code blocks from response
        if not scripts:
            scripts = self._extract_raw_code_blocks(response, script_type)

        return scripts

    def _extract_raw_code_blocks(self, response: str, script_type: str) -> List[AutomationScript]:
        """Fallback: extract code blocks from raw LLM response when JSON parsing fails."""
        scripts = []

        # Determine language hints for code block detection
        if script_type == "selenium":
            lang_hints = ['python', 'py']
            file_ext = '.py'
            code_indicators = ['import', 'def test_', 'class Test', 'selenium', 'webdriver']
        else:  # playwright
            lang_hints = ['javascript', 'js', 'typescript', 'ts']
            file_ext = '.spec.js'
            code_indicators = ['test(', 'expect(', 'page.', 'playwright', 'require(', 'import ']

        # Extract code from markdown code blocks
        code_block_pattern = re.compile(
            r'```(?:' + '|'.join(lang_hints) + r')?\s*\n(.*?)```',
            re.DOTALL | re.IGNORECASE
        )
        matches = code_block_pattern.findall(response)

        for i, code in enumerate(matches):
            code = code.strip()
            # Verify it looks like actual test code
            if code and any(indicator in code for indicator in code_indicators):
                scripts.append(AutomationScript(
                    script_type=script_type,
                    filename=f'test_generated_{i+1}{file_ext}',
                    content=code,
                    related_test_ids=[],
                    feature_name=f"Generated {script_type.capitalize()} test {i+1}"
                ))

        return scripts

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from text that may contain other content."""
        # Try to find JSON block in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON object
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Try parsing the entire response
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        return None

    def enhance_tests(
        self,
        current_tests: List[ManualTestCase],
        requirement: Requirement,
        client_context: Optional[ClientContext] = None
    ) -> List[ManualTestCase]:
        """
        Enhance existing tests by adding missing edge cases and scenarios.

        Args:
            current_tests: Existing test cases
            requirement: Original requirement
            client_context: Optional client context

        Returns:
            List of additional test cases to add
        """
        current_tests_json = json.dumps([t.to_dict() for t in current_tests], indent=2)
        context_text = client_context.get_context_text() if client_context else ""

        prompt = PromptTemplates.get_enhancement_prompt(
            current_tests=current_tests_json,
            requirements=requirement.content,
            client_context=context_text
        )

        response = self.llm.generate(prompt, PromptTemplates.SYSTEM_PROMPT)

        try:
            json_data = self._extract_json(response)
            if json_data and 'additional_tests' in json_data:
                additional = []
                start_id = len(current_tests) + 1
                for i, tc_data in enumerate(json_data['additional_tests']):
                    tc_data['test_id'] = f'TC_{start_id + i:03d}'
                    steps = []
                    for step_data in tc_data.get('test_steps', []):
                        steps.append(TestStep(
                            step_number=step_data.get('step_number', len(steps) + 1),
                            action=step_data.get('action', ''),
                            test_data=step_data.get('test_data', ''),
                            expected_result=step_data.get('expected_result', '')
                        ))
                    tc_data['test_steps'] = steps
                    additional.append(ManualTestCase.from_dict(tc_data))
                return additional
        except Exception as e:
            print(f"Warning: Failed to parse enhancement response: {e}")

        return []


# Factory function
def get_test_generator(llm_adapter: Optional[LLMAdapter] = None) -> TestGenerator:
    """Get a test generator instance."""
    return TestGenerator(llm_adapter)
