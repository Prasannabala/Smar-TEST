"""
Reusable UI components for the Streamlit application.
"""
import streamlit as st
from typing import List, Dict, Any, Optional, Callable
from models.test_case import ManualTestCase, TestSuite
from models.client_context import ClientContext
from ui.styles import COLORS, get_priority_badge, get_connection_status


class UIComponents:
    """
    Collection of reusable UI components.
    """

    @staticmethod
    def page_header(title: str, subtitle: str = ""):
        """Render a page header."""
        st.markdown(f"# {title}")
        if subtitle:
            st.markdown(f"*{subtitle}*")
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    @staticmethod
    def section_header(title: str, icon: str = ""):
        """Render a section header with optional icon."""
        display_title = f"{icon} {title}" if icon else title
        st.markdown(f"### {display_title}")

    @staticmethod
    def card(content_func: Callable, title: str = ""):
        """Render content in a card container."""
        with st.container():
            if title:
                st.markdown(f"<div class='card-header'>{title}</div>", unsafe_allow_html=True)
            content_func()

    @staticmethod
    def metric_row(metrics: List[Dict[str, Any]]):
        """Render a row of metric cards."""
        cols = st.columns(len(metrics))
        for col, metric in zip(cols, metrics):
            with col:
                st.metric(
                    label=metric.get('label', ''),
                    value=metric.get('value', 0),
                    delta=metric.get('delta', None)
                )

    @staticmethod
    def progress_bar_with_text(progress: float, text: str):
        """Render a progress bar with status text."""
        st.progress(progress)
        st.caption(text)

    @staticmethod
    def test_case_preview(test: ManualTestCase, expanded: bool = False):
        """Render a test case preview card."""
        with st.expander(f"{test.test_id}: {test.test_name}", expanded=expanded):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**Category:** {test.category}")
            with col2:
                st.markdown(f"**Priority:** {test.priority}")
            with col3:
                st.markdown(f"**Status:** {test.status}")

            st.markdown("**Description:**")
            st.write(test.description)

            if test.preconditions:
                st.markdown("**Preconditions:**")
                for pre in test.preconditions:
                    st.markdown(f"- {pre}")

            st.markdown("**Test Steps:**")
            for step in test.test_steps:
                st.markdown(f"{step.step_number}. {step.action}")
                if step.test_data:
                    st.caption(f"   Data: {step.test_data}")
                if step.expected_result:
                    st.caption(f"   Expected: {step.expected_result}")

            if test.expected_results:
                st.markdown("**Expected Results:**")
                for i, result in enumerate(test.expected_results, 1):
                    st.markdown(f"{i}. {result}")

    @staticmethod
    def test_suite_summary(suite: TestSuite):
        """Render a test suite summary."""
        summary = suite.get_summary()

        cols = st.columns(4)
        with cols[0]:
            st.metric("Manual Tests", summary['manual_tests'])
        with cols[1]:
            st.metric("Gherkin Scenarios", summary['gherkin_scenarios'])
        with cols[2]:
            st.metric("Selenium Tests", summary['selenium_tests'])
        with cols[3]:
            st.metric("Playwright Tests", summary['playwright_tests'])

    @staticmethod
    def client_selector(clients: List[ClientContext], key: str = "client_select") -> Optional[str]:
        """Render a client selector dropdown."""
        if not clients:
            st.info("No clients configured. Create a client first.")
            return None

        client_options = {c.name: c.id for c in clients}
        selected_name = st.selectbox(
            "Select Client",
            options=list(client_options.keys()),
            key=key
        )
        return client_options.get(selected_name)

    @staticmethod
    def rule_editor(rules: List[str], rule_type: str, key_prefix: str) -> List[str]:
        """
        Render an editable list of rules.

        Args:
            rules: Current list of rules
            rule_type: Type of rules (for display)
            key_prefix: Unique key prefix for Streamlit widgets

        Returns:
            Updated list of rules
        """
        st.markdown(f"**{rule_type}:**")

        updated_rules = []
        for i, rule in enumerate(rules):
            col1, col2 = st.columns([10, 1])
            with col1:
                updated = st.text_input(
                    f"Rule {i+1}",
                    value=rule,
                    key=f"{key_prefix}_{i}",
                    label_visibility="collapsed"
                )
                if updated.strip():
                    updated_rules.append(updated.strip())
            with col2:
                if st.button("X", key=f"{key_prefix}_del_{i}", help="Remove"):
                    pass  # Rule won't be added to updated_rules

        # Add new rule
        new_rule = st.text_input(
            "Add new rule",
            key=f"{key_prefix}_new",
            placeholder=f"Enter new {rule_type.lower()}..."
        )
        if new_rule.strip():
            updated_rules.append(new_rule.strip())

        return updated_rules

    @staticmethod
    def file_uploader_with_preview(
        label: str,
        accepted_types: List[str],
        key: str,
        help_text: str = ""
    ):
        """
        Render a file uploader with preview.

        Args:
            label: Upload label
            accepted_types: List of accepted file extensions
            key: Unique key
            help_text: Help text to display

        Returns:
            Uploaded file object or None
        """
        uploaded = st.file_uploader(
            label,
            type=accepted_types,
            key=key,
            help=help_text
        )

        if uploaded:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"Uploaded: {uploaded.name}")
            with col2:
                size = uploaded.size / 1024  # KB
                st.caption(f"{size:.1f} KB")

        return uploaded

    @staticmethod
    def llm_status_indicator(is_connected: bool, provider: str, model: str):
        """Render LLM connection status."""
        if is_connected:
            st.success(f"Connected to {provider} ({model})")
        else:
            st.error(f"Not connected to {provider}")

    @staticmethod
    def generation_options():
        """Render test generation options checkboxes."""
        st.markdown("**Test Types to Generate:**")

        col1, col2 = st.columns(2)
        with col1:
            manual = st.checkbox("Manual Test Cases", value=True, disabled=True,
                                help="Manual tests are always generated")
            gherkin = st.checkbox("Gherkin (BDD)", value=False,
                                 help="Generate Gherkin feature files")
        with col2:
            selenium = st.checkbox("Selenium (Python)", value=False,
                                  help="Generate Selenium test scripts")
            playwright = st.checkbox("Playwright (JavaScript)", value=False,
                                    help="Generate Playwright test specs")

        st.markdown("**Generation Options:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            edge_cases = st.checkbox("Include edge cases", value=True)
        with col2:
            negative = st.checkbox("Include negative tests", value=True)
        with col3:
            boundary = st.checkbox("Include boundary tests", value=True)

        return {
            'gherkin': gherkin,
            'selenium': selenium,
            'playwright': playwright,
            'edge_cases': edge_cases,
            'negative': negative,
            'boundary': boundary
        }

    @staticmethod
    def export_buttons(suite: TestSuite, export_handler) -> None:
        """Render export buttons for a test suite."""
        st.markdown("**Export Options:**")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("Download Excel", use_container_width=True):
                content, filename = export_handler.export_to_excel(suite)
                st.download_button(
                    "Save Excel",
                    data=content,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_excel"
                )

        with col2:
            if st.button("Download CSV", use_container_width=True):
                content, filename = export_handler.export_to_csv(suite)
                st.download_button(
                    "Save CSV",
                    data=content,
                    file_name=filename,
                    mime="text/csv",
                    key="dl_csv"
                )

        with col3:
            if st.button("Download Markdown", use_container_width=True):
                content, filename = export_handler.export_to_markdown(suite)
                st.download_button(
                    "Save Markdown",
                    data=content,
                    file_name=filename,
                    mime="text/markdown",
                    key="dl_md"
                )

        with col4:
            if st.button("Download All (ZIP)", use_container_width=True):
                content, filename = export_handler.export_all_as_zip(suite)
                st.download_button(
                    "Save ZIP",
                    data=content,
                    file_name=filename,
                    mime="application/zip",
                    key="dl_zip"
                )

    @staticmethod
    def empty_state(message: str, icon: str = ""):
        """Render an empty state message."""
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem; color: {COLORS['text_muted']};">
            <div style="font-size: 2rem; margin-bottom: 1rem;">{icon}</div>
            <div>{message}</div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def confirmation_dialog(message: str, key: str) -> bool:
        """Render a confirmation dialog."""
        st.warning(message)
        col1, col2 = st.columns(2)
        with col1:
            confirm = st.button("Confirm", key=f"{key}_confirm", type="primary")
        with col2:
            cancel = st.button("Cancel", key=f"{key}_cancel")
        return confirm and not cancel
