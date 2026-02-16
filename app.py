"""
Smar-Test - Smart Test Case Generation
A professional AI-powered tool for generating comprehensive test cases from requirements.
"""
import streamlit as st
from datetime import datetime
from typing import Optional

# Configure page - must be first Streamlit command
st.set_page_config(
    page_title="Smar-Test | AI Test Case Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules after page config
from config.settings import get_settings, save_settings, Settings
from config.llm_config import LLMProvider, llm_config
from core.llm_adapter import get_llm_adapter, OllamaAdapter
from core.document_parser import DocumentParser
from core.test_generator import TestGenerator, GenerationProgress
from core.export_handler import get_export_handler
from models.client_context import ClientContext, get_client_manager
from models.requirement import Requirement
from models.test_case import TestSuite
from storage.database import get_database
from ui.styles import apply_custom_styles, COLORS, get_brand_badge, get_brand_header, get_author_footer
from ui.components import UIComponents


# Apply custom styles
st.markdown(apply_custom_styles(), unsafe_allow_html=True)

# Chrome-compatible layout fixes
st.markdown("""
<style>
    /* Force sidebar visibility */
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        width: 280px !important;
        min-width: 280px !important;
        background: #f8fafc !important;
        transition: all 0.3s ease !important;
    }

    section[data-testid="stSidebar"] > div {
        background: #f8fafc !important;
    }

    /* Style collapse button for accessibility */
    button[kind="header"] {
        color: #6366f1 !important;
        font-weight: 600 !important;
    }

    button[kind="header"]:hover {
        background: rgba(99, 102, 241, 0.1) !important;
    }

    /* Hide sidebar when user toggles */
    .sidebar-hidden section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Dropdown improvements for Chrome */
    .stSelectbox > div > div {
        min-height: 2.75rem !important;
    }

    [data-baseweb="select"] {
        border-radius: 8px !important;
    }

    /* Make dropdown options more readable */
    [role="option"] {
        white-space: normal !important;
        word-wrap: break-word !important;
        padding: 0.875rem 1rem !important;
        line-height: 1.5 !important;
        min-height: 3rem !important;
    }

    [role="listbox"] {
        max-width: 500px !important;
    }

    /* Info box styling */
    .element-container .stAlert {
        padding: 0.75rem 1rem !important;
        font-size: 0.875rem !important;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'current_page': 'generate',
        'selected_client_id': None,
        'test_suite': None,
        'generation_progress': None,
        'requirement': None,
        'llm_connected': False,
        'settings_saved': False,
        'sidebar_visible': True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def check_llm_connection() -> bool:
    """Check if LLM is available and update session state."""
    try:
        settings = get_settings()
        if settings.llm_provider == LLMProvider.OLLAMA.value:
            adapter = OllamaAdapter(settings.ollama_base_url, settings.ollama_model)
            connected = adapter.is_available()
        else:
            adapter = get_llm_adapter()
            connected = adapter.is_available()
        st.session_state.llm_connected = connected
        return connected
    except Exception:
        st.session_state.llm_connected = False
        return False


def render_sidebar():
    """Render the sidebar with navigation and LLM settings."""
    with st.sidebar:
        # Clean logo with proper Chrome rendering and gold icon
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 0.5rem;">
            <div style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 0;
                letter-spacing: -0.02em;
                line-height: 1.2;
            ">
                <span style="color: #f59e0b;">⚡</span>
                <span style="color: #6366f1;">Smart-Options</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Navigation buttons with professional icons
        pages = {
            'generate': '🚀 Generate Tests',
            'clients': '💼 Client Setup',
            'history': '📋 History',
            'settings': '⚙️ LLM Settings',
            'help': '📖 How to Use'
        }

        for page_key, page_name in pages.items():
            if st.button(
                page_name,
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_key else "secondary"
            ):
                st.session_state.current_page = page_key
                st.rerun()

        st.divider()

        # Inference Engine status
        settings = get_settings()
        is_connected = check_llm_connection()

        if is_connected:
            st.caption(f"✅ Using · {settings.llm_provider.title()}")
        else:
            st.caption(f"❌ Not Connected · {settings.llm_provider.title()}")

        # Toggle button for sidebar visibility
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👁️ Show", use_container_width=True, type="secondary", key="show_sidebar"):
                st.session_state.sidebar_visible = True
                st.rerun()

        with col2:
            if st.button("🙈 Hide", use_container_width=True, type="secondary", key="hide_sidebar"):
                st.session_state.sidebar_visible = False
                st.rerun()


def render_generate_page():
    """Render the main test generation page."""
    # Show brand header on home page
    st.markdown(get_brand_header(), unsafe_allow_html=True)

    st.markdown("### Test Case Generator")
    st.caption("Generate comprehensive test cases from your requirements")
    st.markdown("---")

    # Check LLM connection
    if not st.session_state.llm_connected:
        st.warning("LLM is not connected. Please configure LLM settings first.")
        if st.button("Go to LLM Settings"):
            st.session_state.current_page = 'settings'
            st.rerun()
        return

    # Client selection
    col1, col2 = st.columns([4, 1])
    with col1:
        manager = get_client_manager()
        clients = manager.get_all()

        if clients:
            client_names = ["-- No Client --"] + [c.name for c in clients]

            # Find current selection
            current_selection = "-- No Client --"
            if st.session_state.selected_client_id:
                current_client = next((c for c in clients if c.id == st.session_state.selected_client_id), None)
                if current_client and current_client.name in client_names:
                    current_selection = current_client.name

            selected_name = st.selectbox(
                "Select Client Context (Optional)",
                client_names,
                index=client_names.index(current_selection) if current_selection in client_names else 0,
                help="Choose a client to apply specific testing rules and context"
            )

            if selected_name != "-- No Client --":
                selected_client = next((c for c in clients if c.name == selected_name), None)
                st.session_state.selected_client_id = selected_client.id if selected_client else None
                if selected_client:
                    st.caption(f"📋 {selected_client.get_rules_summary()}")
            else:
                st.session_state.selected_client_id = None
        else:
            st.info("💡 No clients configured. Create one to apply specific testing rules.")
            st.session_state.selected_client_id = None

    with col2:
        if st.button("➕ New Client", use_container_width=True):
            st.session_state.current_page = 'clients'
            st.rerun()

    st.markdown("---")

    # Requirements upload
    st.markdown("### Requirements Document")

    uploaded_file = st.file_uploader(
        "Upload requirements document",
        type=['txt', 'pdf', 'docx'],
        help="Supported formats: TXT, PDF, DOCX"
    )

    if uploaded_file:
        try:
            # Parse document
            parsed = DocumentParser.parse(uploaded_file, uploaded_file.name)
            st.session_state.requirement = Requirement(
                filename=parsed.filename,
                content=parsed.content,
                file_type=parsed.file_type,
                word_count=parsed.word_count,
                page_count=parsed.page_count
            )

            # Show document info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File", parsed.filename)
            with col2:
                st.metric("Words", f"{parsed.word_count:,}")
            with col3:
                st.metric("Pages", parsed.page_count)

            # Preview
            with st.expander("Document Preview", expanded=False):
                st.text(parsed.content[:2000] + ("..." if len(parsed.content) > 2000 else ""))

        except Exception as e:
            st.error(f"Failed to parse document: {e}")
            st.session_state.requirement = None

    st.markdown("---")

    # Generation options
    st.markdown("### Test Generation Options")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Test Types:**")
        st.checkbox("Manual Test Cases", value=True, disabled=True, key="opt_manual",
                   help="Manual tests are always generated (required)")
        generate_gherkin = st.checkbox("Gherkin (BDD Feature Files)", value=False, key="opt_gherkin")
        generate_selenium = st.checkbox("Selenium (Python)", value=False, key="opt_selenium")
        generate_playwright = st.checkbox("Playwright (JavaScript)", value=False, key="opt_playwright")

    with col2:
        st.markdown("**Include:**")
        include_edge = st.checkbox("Include Edge Cases", value=True, key="opt_edge")
        include_negative = st.checkbox("Include Negative Tests", value=True, key="opt_negative")
        include_boundary = st.checkbox("Include Boundary Tests", value=True, key="opt_boundary")

    st.markdown("---")

    # Generate button
    can_generate = st.session_state.requirement is not None and st.session_state.llm_connected

    if st.button("Generate Test Cases", type="primary", disabled=not can_generate, use_container_width=True):
        generate_tests(
            generate_gherkin=generate_gherkin,
            generate_selenium=generate_selenium,
            generate_playwright=generate_playwright,
            include_edge=include_edge,
            include_negative=include_negative,
            include_boundary=include_boundary
        )

    if not can_generate:
        if not st.session_state.requirement:
            st.caption("Upload a requirements document to generate tests")
        elif not st.session_state.llm_connected:
            st.caption("Connect to an LLM to generate tests")

    # Display results
    if st.session_state.test_suite:
        render_test_results()


def generate_tests(generate_gherkin: bool, generate_selenium: bool, generate_playwright: bool,
                   include_edge: bool, include_negative: bool, include_boundary: bool):
    """Run test generation with progress tracking."""
    requirement = st.session_state.requirement
    client_context = None

    if st.session_state.selected_client_id:
        manager = get_client_manager()
        client_context = manager.get(st.session_state.selected_client_id)

    # Progress containers
    progress_container = st.empty()
    status_container = st.empty()
    detail_container = st.empty()

    # Stage color mapping for the dynamic progress bar
    stage_colors = {
        "manual":     {"color": "#4CAF50", "bg": "#C8E6C9", "label": "📋 Manual Tests",     "icon": "📋"},
        "gherkin":    {"color": "#2196F3", "bg": "#BBDEFB", "label": "🥒 Gherkin BDD",      "icon": "🥒"},
        "selenium":   {"color": "#FF9800", "bg": "#FFE0B2", "label": "🐍 Selenium Scripts",  "icon": "🐍"},
        "playwright": {"color": "#9C27B0", "bg": "#E1BEE7", "label": "🎭 Playwright Specs",  "icon": "🎭"},
        "complete":   {"color": "#00C853", "bg": "#B9F6CA", "label": "🎉 Complete!",         "icon": "🎉"},
        "error":      {"color": "#F44336", "bg": "#FFCDD2", "label": "❌ Error",              "icon": "❌"},
    }

    def update_progress(progress: GenerationProgress):
        stage_info = stage_colors.get(progress.stage, stage_colors["manual"])
        pct = max(0, min(100, int(progress.progress * 100)))
        bar_color = stage_info["color"]
        bg_color = stage_info["bg"]
        stage_label = stage_info["label"]

        progress_container.markdown(f"""
        <div style="margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.75rem; font-weight: 600; color: {bar_color};
                         background: {bg_color}; padding: 2px 10px; border-radius: 10px;">
                {stage_label}
            </span>
            <span style="font-size: 0.75rem; color: #888; font-weight: 500;">{pct}%</span>
        </div>
        <div style="width: 100%; background: #e0e0e0; border-radius: 8px; height: 18px;
                    overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.12);">
            <div style="width: {pct}%; height: 100%; border-radius: 8px;
                        background: linear-gradient(90deg, {bar_color}CC, {bar_color});
                        transition: width 0.4s ease, background 0.4s ease;
                        box-shadow: 0 0 8px {bar_color}66;">
            </div>
        </div>
        <div style="margin-top: 4px; font-size: 0.8rem; color: #555;">
            {progress.message}
        </div>
        """, unsafe_allow_html=True)

        if progress.error:
            status_container.error(f"Error: {progress.error}")

    try:
        detail_container.info("🔧 Initializing test generation engine and connecting to LLM...")

        generator = TestGenerator()

        detail_container.info(f"📄 Starting generation from: **{requirement.filename}**")

        # Generate tests
        suite = generator.generate_test_suite(
            requirement=requirement,
            client_context=client_context,
            generate_gherkin=generate_gherkin,
            generate_selenium=generate_selenium,
            generate_playwright=generate_playwright,
            include_edge_cases=include_edge,
            include_negative=include_negative,
            include_boundary=include_boundary,
            progress_callback=update_progress
        )

        st.session_state.test_suite = suite

        # Record in history
        db = get_database()
        test_types = ['manual']
        if generate_gherkin:
            test_types.append('gherkin')
        if generate_selenium:
            test_types.append('selenium')
        if generate_playwright:
            test_types.append('playwright')

        db.add_generation_record(
            client_id=st.session_state.selected_client_id,
            requirement_filename=requirement.filename,
            test_count=suite.get_total_count(),
            test_types=test_types
        )

        progress_container.empty()
        detail_container.empty()

        # Show detailed success summary
        summary_parts = [f"**{len(suite.manual_tests)}** manual test cases"]
        warnings = []

        if generate_gherkin:
            if suite.gherkin_scripts:
                summary_parts.append(f"**{len(suite.gherkin_scripts)}** Gherkin feature files")
            else:
                warnings.append("⚠️ **Gherkin:** LLM response could not be parsed into feature files. The model may not have returned valid JSON. Try regenerating or check the model.")

        if generate_selenium:
            if suite.selenium_scripts:
                summary_parts.append(f"**{len(suite.selenium_scripts)}** Selenium scripts")
            else:
                warnings.append("⚠️ **Selenium:** CodeLlama response could not be parsed. Ensure `codellama` is installed (`ollama pull codellama:7b`) and try again.")

        if generate_playwright:
            if suite.playwright_scripts:
                summary_parts.append(f"**{len(suite.playwright_scripts)}** Playwright specs")
            else:
                warnings.append("⚠️ **Playwright:** CodeLlama response could not be parsed. Ensure `codellama` is installed (`ollama pull codellama:7b`) and try again.")

        status_container.success(f"✅ Generated {', '.join(summary_parts)}")

        if warnings:
            for warning in warnings:
                st.warning(warning)

    except Exception as e:
        progress_container.empty()
        detail_container.empty()
        status_container.error(f"❌ Generation failed: {str(e)}")
        st.caption("💡 **Tip:** If this is a timeout, try increasing the timeout in LLM Settings, or use a smaller/faster model.")


def render_test_results():
    """Render generated test results."""
    suite = st.session_state.test_suite

    st.markdown("---")
    st.markdown("## Generated Test Cases")

    # Summary metrics
    summary = suite.get_summary()
    cols = st.columns(4)
    with cols[0]:
        st.metric("Manual Tests", summary['manual_tests'])
    with cols[1]:
        st.metric("Gherkin", summary['gherkin_scenarios'])
    with cols[2]:
        st.metric("Selenium", summary['selenium_tests'])
    with cols[3]:
        st.metric("Playwright", summary['playwright_tests'])

    st.markdown("---")

    # Tabs for different test types
    tabs = st.tabs(["Manual Tests", "Gherkin", "Selenium", "Playwright", "Export"])

    with tabs[0]:
        render_manual_tests(suite)

    with tabs[1]:
        render_automation_scripts(suite.gherkin_scripts, "Gherkin")

    with tabs[2]:
        render_automation_scripts(suite.selenium_scripts, "Selenium")

    with tabs[3]:
        render_automation_scripts(suite.playwright_scripts, "Playwright")

    with tabs[4]:
        render_export_options(suite)


def render_manual_tests(suite: TestSuite):
    """Render manual test cases."""
    if not suite.manual_tests:
        st.info("No manual tests generated.")
        return

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        priority_filter = st.multiselect(
            "Filter by Priority",
            options=["High", "Medium", "Low"],
            default=["High", "Medium", "Low"]
        )
    with col2:
        search = st.text_input("Search tests", placeholder="Search by name or description...")

    # Filter tests
    filtered_tests = [
        t for t in suite.manual_tests
        if t.priority in priority_filter and
        (not search or search.lower() in t.test_name.lower() or search.lower() in t.description.lower())
    ]

    st.caption(f"Showing {len(filtered_tests)} of {len(suite.manual_tests)} tests")

    # Display tests
    for test in filtered_tests:
        with st.expander(f"{test.test_id}: {test.test_name}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                priority_color = {"High": "red", "Medium": "orange", "Low": "green"}.get(test.priority, "gray")
                st.markdown(f"**Priority:** :{priority_color}[{test.priority}]")
            with col2:
                st.markdown(f"**Category:** {test.category}")
            with col3:
                st.markdown(f"**Status:** {test.status}")

            st.markdown(f"**Description:** {test.description}")

            if test.preconditions:
                st.markdown("**Preconditions:**")
                for pre in test.preconditions:
                    st.markdown(f"- {pre}")

            st.markdown("**Test Steps:**")
            for step in test.test_steps:
                st.markdown(f"**{step.step_number}.** {step.action}")
                if step.test_data:
                    st.caption(f"   Test Data: {step.test_data}")
                if step.expected_result:
                    st.caption(f"   Expected: {step.expected_result}")

            if test.expected_results:
                st.markdown("**Expected Results:**")
                for i, result in enumerate(test.expected_results, 1):
                    st.markdown(f"{i}. {result}")

            if test.tags:
                st.markdown(f"**Tags:** {', '.join(test.tags)}")


def render_automation_scripts(scripts, script_type: str):
    """Render automation scripts."""
    if not scripts:
        st.info(f"No {script_type} scripts generated. Enable {script_type} generation to create scripts.")
        return

    for script in scripts:
        with st.expander(f"{script.filename}"):
            st.code(script.content, language="python" if script_type == "Selenium" else
                   "gherkin" if script_type == "Gherkin" else "javascript")


def render_export_options(suite: TestSuite):
    """Render export options."""
    st.markdown("### Export Generated Tests")
    st.markdown("Download your test cases in various formats.")

    export_handler = get_export_handler()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Manual Tests:**")

        # Excel export
        try:
            excel_content, excel_filename = export_handler.export_to_excel(suite)
            st.download_button(
                "Download Excel (.xlsx)",
                data=excel_content,
                file_name=excel_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except ImportError:
            st.warning("Install openpyxl for Excel export: pip install openpyxl")

        # CSV export
        csv_content, csv_filename = export_handler.export_to_csv(suite)
        st.download_button(
            "Download CSV",
            data=csv_content,
            file_name=csv_filename,
            mime="text/csv",
            use_container_width=True
        )

        # Markdown export
        md_content, md_filename = export_handler.export_to_markdown(suite)
        st.download_button(
            "Download Markdown",
            data=md_content,
            file_name=md_filename,
            mime="text/markdown",
            use_container_width=True
        )

    with col2:
        st.markdown("**All Files (ZIP):**")

        try:
            zip_content, zip_filename = export_handler.export_all_as_zip(suite)
            st.download_button(
                "Download All as ZIP",
                data=zip_content,
                file_name=zip_filename,
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
            st.caption("Includes manual tests, Gherkin, Selenium, and Playwright files")
        except Exception as e:
            st.error(f"Failed to create ZIP: {e}")


def render_clients_page():
    """Render the client setup page."""
    # Show brand header
    st.markdown(get_brand_header(), unsafe_allow_html=True)

    st.markdown("### Client Configuration")
    st.caption("Set up client-specific context for more accurate test generation")
    st.markdown("---")

    # Initialize client page session state
    if 'client_save_message' not in st.session_state:
        st.session_state.client_save_message = None
    if 'client_save_details' not in st.session_state:
        st.session_state.client_save_details = None
    if 'select_client_after_save' not in st.session_state:
        st.session_state.select_client_after_save = None

    manager = get_client_manager()
    clients = manager.get_all()

    # Show persistent save message (survives rerun)
    if st.session_state.client_save_message:
        st.success(st.session_state.client_save_message)
        if st.session_state.client_save_details:
            st.info(st.session_state.client_save_details)
        # Clear after displaying
        st.session_state.client_save_message = None
        st.session_state.client_save_details = None

    # Client list and selection
    col1, col2 = st.columns([3, 1])
    with col1:
        if clients:
            client_names = [c.name for c in clients]
            options_list = ["-- Create New --"] + client_names

            # Auto-select the client that was just saved/created
            default_index = 0
            if st.session_state.select_client_after_save:
                saved_name = st.session_state.select_client_after_save
                if saved_name in options_list:
                    default_index = options_list.index(saved_name)
                st.session_state.select_client_after_save = None

            selected_name = st.selectbox("Select Client", options_list, index=default_index)
        else:
            selected_name = "-- Create New --"
            st.info("No clients configured yet. Create your first client below.")

    with col2:
        if selected_name != "-- Create New --":
            if st.button("Delete Client", type="secondary"):
                selected_client = next((c for c in clients if c.name == selected_name), None)
                if selected_client:
                    # Clear cached form widget keys for the deleted client
                    del_suffix = selected_client.id
                    for widget_key in [
                        f"name_{del_suffix}", f"project_name_{del_suffix}",
                        f"test_env_{del_suffix}", f"tech_stack_{del_suffix}",
                        f"proj_desc_{del_suffix}", f"nav_rules_{del_suffix}",
                        f"thumb_rules_{del_suffix}", f"business_rules_{del_suffix}",
                        f"best_practices_{del_suffix}"
                    ]:
                        st.session_state.pop(widget_key, None)
                    st.session_state.pop('last_client_form_key', None)

                    manager.delete(selected_client.id)
                    st.session_state.client_save_message = f"🗑️ Deleted client: {selected_name}"
                    st.rerun()

    st.markdown("---")

    # Edit form
    if selected_name == "-- Create New --":
        st.markdown("### Create New Client")
        editing_client = None
    else:
        st.markdown(f"### Edit Client: {selected_name}")
        editing_client = next((c for c in clients if c.name == selected_name), None)

    # Use dynamic form key based on selected client to force widget reset
    # This ensures form fields refresh properly when switching clients
    form_key_suffix = editing_client.id if editing_client else "new"

    # Clear stale widget keys when the client selection changes
    if 'last_client_form_key' not in st.session_state:
        st.session_state.last_client_form_key = form_key_suffix
    if st.session_state.last_client_form_key != form_key_suffix:
        # Client changed — remove old widget keys so fresh values load
        old_suffix = st.session_state.last_client_form_key
        for old_key in [
            f"name_{old_suffix}", f"project_name_{old_suffix}",
            f"test_env_{old_suffix}", f"tech_stack_{old_suffix}",
            f"proj_desc_{old_suffix}", f"nav_rules_{old_suffix}",
            f"thumb_rules_{old_suffix}", f"business_rules_{old_suffix}",
            f"best_practices_{old_suffix}"
        ]:
            st.session_state.pop(old_key, None)
        st.session_state.last_client_form_key = form_key_suffix

    with st.form(f"client_form_{form_key_suffix}"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Client Name *", value=editing_client.name if editing_client else "",
                                placeholder="e.g., Client A",
                                key=f"name_{form_key_suffix}")
            project_name = st.text_input("Project Name",
                                        value=editing_client.project_name if editing_client else "",
                                        placeholder="e.g., E-Commerce Platform",
                                        key=f"project_name_{form_key_suffix}")

        with col2:
            test_environment = st.text_input("Test Environment",
                                            value=editing_client.test_environment if editing_client else "",
                                            placeholder="e.g., Chrome, Firefox, Edge",
                                            key=f"test_env_{form_key_suffix}")
            tech_stack = st.text_input("Tech Stack (comma-separated)",
                                      value=", ".join(editing_client.tech_stack) if editing_client else "",
                                      placeholder="e.g., React, Node.js, PostgreSQL",
                                      key=f"tech_stack_{form_key_suffix}")

        project_description = st.text_area("Project Description",
                                          value=editing_client.project_description if editing_client else "",
                                          placeholder="Brief description of the project...",
                                          height=100,
                                          key=f"proj_desc_{form_key_suffix}")

        st.markdown("---")

        # Rules sections
        st.markdown("### Navigation Rules")
        st.caption("Define application navigation paths and flows")
        navigation_rules = st.text_area(
            "Navigation Rules (one per line)",
            value="\n".join(editing_client.navigation_rules) if editing_client else "",
            placeholder="e.g., Login -> Dashboard -> Settings\nDashboard -> Reports -> Export",
            height=100,
            key=f"nav_rules_{form_key_suffix}"
        )

        st.markdown("### Thumb Rules")
        st.caption("Testing conventions and standards for this client")
        thumb_rules = st.text_area(
            "Thumb Rules (one per line)",
            value="\n".join(editing_client.thumb_rules) if editing_client else "",
            placeholder="e.g., All forms must validate before submit\nSession timeout after 30 mins",
            height=100,
            key=f"thumb_rules_{form_key_suffix}"
        )

        st.markdown("### Business Rules")
        st.caption("Domain-specific business rules and logic")
        business_rules = st.text_area(
            "Business Rules (one per line)",
            value="\n".join(editing_client.business_rules) if editing_client else "",
            placeholder="e.g., Orders over $100 get free shipping\nMaximum 5 items per cart",
            height=100,
            key=f"business_rules_{form_key_suffix}"
        )

        st.markdown("### Best Practices")
        st.caption("Client-specific testing best practices")
        best_practices = st.text_area(
            "Best Practices (one per line)",
            value="\n".join(editing_client.best_practices) if editing_client else "",
            placeholder="e.g., Always test with multiple user roles\nVerify email notifications",
            height=100,
            key=f"best_practices_{form_key_suffix}"
        )

        submitted = st.form_submit_button("Save Client", type="primary", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Client name is required")
            else:
                # Parse rules from text areas
                nav_rules_list = [r.strip() for r in navigation_rules.split("\n") if r.strip()]
                thumb_rules_list = [r.strip() for r in thumb_rules.split("\n") if r.strip()]
                biz_rules_list = [r.strip() for r in business_rules.split("\n") if r.strip()]
                practices_list = [r.strip() for r in best_practices.split("\n") if r.strip()]

                client_data = {
                    'name': name.strip(),
                    'project_name': project_name.strip(),
                    'project_description': project_description.strip(),
                    'tech_stack': [t.strip() for t in tech_stack.split(",") if t.strip()],
                    'test_environment': test_environment.strip(),
                    'navigation_rules': nav_rules_list,
                    'thumb_rules': thumb_rules_list,
                    'business_rules': biz_rules_list,
                    'best_practices': practices_list,
                }

                try:
                    if editing_client:
                        saved_client = manager.update(editing_client.id, client_data)
                        action = "Updated"
                    else:
                        saved_client = manager.create(client_data)
                        action = "Created"

                    # Build detailed save confirmation
                    total_rules = len(nav_rules_list) + len(thumb_rules_list) + len(biz_rules_list) + len(practices_list)
                    details_parts = []
                    if nav_rules_list:
                        details_parts.append(f"**{len(nav_rules_list)}** navigation rules")
                    if thumb_rules_list:
                        details_parts.append(f"**{len(thumb_rules_list)}** thumb rules")
                    if biz_rules_list:
                        details_parts.append(f"**{len(biz_rules_list)}** business rules")
                    if practices_list:
                        details_parts.append(f"**{len(practices_list)}** best practices")

                    save_msg = f"✅ {action} client: **{name.strip()}**"
                    if details_parts:
                        save_details = f"📋 Saved {total_rules} rules: {', '.join(details_parts)}"
                    else:
                        save_details = "📋 No rules configured for this client."

                    # Store in session state so it survives rerun
                    st.session_state.client_save_message = save_msg
                    st.session_state.client_save_details = save_details
                    st.session_state.select_client_after_save = name.strip()

                    # Clear cached form widget keys so fresh values load from DB
                    for widget_key in [
                        f"name_{form_key_suffix}", f"project_name_{form_key_suffix}",
                        f"test_env_{form_key_suffix}", f"tech_stack_{form_key_suffix}",
                        f"proj_desc_{form_key_suffix}", f"nav_rules_{form_key_suffix}",
                        f"thumb_rules_{form_key_suffix}", f"business_rules_{form_key_suffix}",
                        f"best_practices_{form_key_suffix}"
                    ]:
                        st.session_state.pop(widget_key, None)

                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to save client: {e}")
                    st.caption("Please check the error above and try again.")

    # Document upload section (outside form)
    if editing_client:
        st.markdown("---")
        st.markdown("### Context Documents")
        st.caption("Upload additional context documents for this client")

        uploaded_doc = st.file_uploader(
            "Upload document",
            type=['txt', 'pdf', 'docx'],
            key="client_doc_upload"
        )

        if uploaded_doc:
            try:
                parsed = DocumentParser.parse(uploaded_doc, uploaded_doc.name)
                manager.add_document(
                    editing_client.id,
                    parsed.filename,
                    parsed.content,
                    parsed.file_type
                )
                st.success(f"Uploaded: {parsed.filename}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to upload document: {e}")

        # Show existing documents
        if editing_client.documents:
            st.markdown("**Uploaded Documents:**")
            for doc in editing_client.documents:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"{doc['filename']} ({doc['file_type']})")
                with col2:
                    if st.button("Remove", key=f"del_doc_{doc['id']}"):
                        manager.remove_document(doc['id'])
                        st.rerun()


def render_history_page():
    """Render the generation history page."""
    # Show brand header
    st.markdown(get_brand_header(), unsafe_allow_html=True)

    st.markdown("### Generation History")
    st.caption("View past test generation runs")
    st.markdown("---")

    # Initialize history page session state
    if 'history_clear_message' not in st.session_state:
        st.session_state.history_clear_message = None
    if 'history_confirm_clear' not in st.session_state:
        st.session_state.history_confirm_clear = False

    # Show clear message if exists
    if st.session_state.history_clear_message:
        st.success(st.session_state.history_clear_message)
        st.session_state.history_clear_message = None

    db = get_database()
    history = db.get_generation_history(limit=50)

    if not history:
        st.info("No generation history yet. Generate some tests to see them here.")
        return

    # Header row with record count and clear button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"Showing {len(history)} generation record(s)")
    with col2:
        if not st.session_state.history_confirm_clear:
            if st.button("🗑️ Clear History", use_container_width=True, type="secondary"):
                st.session_state.history_confirm_clear = True
                st.rerun()
        else:
            st.warning("Are you sure?")
            confirm_col1, confirm_col2 = st.columns(2)
            with confirm_col1:
                if st.button("Yes, clear all", use_container_width=True, type="primary"):
                    deleted_count = db.clear_generation_history()
                    st.session_state.history_confirm_clear = False
                    st.session_state.history_clear_message = f"🗑️ Cleared {deleted_count} history record(s)"
                    st.rerun()
            with confirm_col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.history_confirm_clear = False
                    st.rerun()

    st.markdown("---")

    for record in history:
        with st.expander(f"📄 {record['requirement_filename']} — {record['generated_at'][:10]}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tests Generated", record['test_count'])
            with col2:
                st.write(f"**Types:** {', '.join(record['test_types'])}")
            with col3:
                st.write(f"**Date:** {record['generated_at'][:19]}")


def render_help_page():
    """Render the help/how-to-use page."""
    # Show brand header
    st.markdown(get_brand_header(), unsafe_allow_html=True)

    st.markdown("### How to Use Smar-Test")
    st.caption("A comprehensive guide to generating AI-powered test cases")
    st.markdown("---")

    # Quick Start Guide
    st.markdown("## 🚀 Quick Start Guide")

    st.markdown("""
    Follow these simple steps to generate comprehensive test cases:

    ### Step 1: Configure Your LLM Provider

    1. Navigate to **⚙️ LLM Settings** in the sidebar
    2. Choose your preferred provider:
       - **Ollama** - Free, runs locally (no API needed)
       - **HuggingFace** - Access 1000+ models via cloud
       - **OpenAI** - GPT-3.5/GPT-4 models
       - **Groq** - Ultra-fast inference
       - **Anthropic** - Claude models
    3. Enter your API credentials (if required)
    4. Click **Save Settings**
    5. Verify the green "✓ Connected" status appears

    ### Step 2: Create Client Context (Optional but Recommended)

    1. Click **👥 Client Setup** in the sidebar
    2. Fill in the client information:
       - **Client Name**: Your project or client name
       - **Project Name**: Specific project being tested
       - **Tech Stack**: Technologies used (React, Node.js, etc.)
       - **Test Environment**: Browsers/platforms to test on
    3. Add your testing rules:
       - **Navigation Rules**: Application flow paths
       - **Thumb Rules**: Testing conventions
       - **Business Rules**: Domain-specific logic
       - **Best Practices**: Client-specific standards
    4. Click **Save Client**

    ### Step 3: Generate Test Cases

    1. Click **📝 Generate Tests** in the sidebar
    2. Select your client from the dropdown (or skip for generic tests)
    3. Upload your requirements document (TXT, PDF, or DOCX)
    4. Choose test types to generate:
       - ✓ **Manual Test Cases** (always included)
       - ☐ **Gherkin (BDD)** - Cucumber-style scenarios
       - ☐ **Selenium** - Python automation scripts
       - ☐ **Playwright** - JavaScript/TypeScript tests
    5. Select options:
       - ✓ **Include Edge Cases**
       - ✓ **Include Negative Tests**
       - ✓ **Include Boundary Tests**
    6. Click **Generate Test Cases**
    7. Wait for generation to complete (progress bar will show status)

    ### Step 4: Review and Export

    1. Browse generated tests in different tabs:
       - **Manual Tests** - Detailed test cases with steps
       - **Gherkin** - BDD feature files
       - **Selenium** - Python automation code
       - **Playwright** - JavaScript test specs
    2. Filter and search tests as needed
    3. Go to **Export** tab
    4. Download in your preferred format:
       - Excel (.xlsx)
       - CSV
       - Markdown
       - ZIP (all files together)
    """)

    st.markdown("---")

    # Features Overview
    st.markdown("## ✨ Key Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🎯 Smart Test Generation
        - AI-powered analysis of requirements
        - Context-aware test case creation
        - Automatic edge case detection
        - Negative and boundary testing

        ### 🌐 Multiple Formats
        - Manual test cases with detailed steps
        - Gherkin BDD scenarios
        - Selenium automation scripts
        - Playwright test specs
        """)

    with col2:
        st.markdown("""
        ### 🔧 Flexible LLM Support
        - Local models (Ollama, vLLM)
        - Cloud APIs (OpenAI, Anthropic)
        - HuggingFace (1000+ models)
        - Groq (ultra-fast inference)

        ### 📊 Client Management
        - Save client-specific rules
        - Reusable test contexts
        - Project documentation
        - Navigation flow tracking
        """)

    st.markdown("---")

    # Tips and Best Practices
    st.markdown("## 💡 Tips & Best Practices")

    with st.expander("📝 Writing Good Requirements", expanded=False):
        st.markdown("""
        **For Best Results:**
        - Be specific and detailed in your requirements
        - Include functional and non-functional requirements
        - Mention edge cases and error scenarios
        - Specify expected behaviors clearly
        - Add business rules and constraints

        **Example Good Requirement:**
        ```
        Feature: User Login
        - Users must enter email and password
        - Email must be valid format
        - Password minimum 8 characters
        - Max 3 failed attempts before lockout
        - Session timeout after 30 minutes
        - Show error messages for invalid credentials
        ```
        """)

    with st.expander("🎯 Choosing the Right LLM", expanded=False):
        st.markdown("""
        **For Speed:** Groq, Ollama (local)

        **For Quality:** Claude (Anthropic), GPT-4 (OpenAI)

        **For Cost:** HuggingFace (many free models), Ollama (free local)

        **For Privacy:** Ollama, vLLM (runs completely local)

        **Recommended Models:**
        - **Ollama:** `qwen2.5:7b`, `mistral:latest`
        - **HuggingFace:** `Qwen/Qwen2.5-7B-Instruct`, `meta-llama/Llama-3.1-8B-Instruct`
        - **OpenAI:** `gpt-4o-mini` (cost-effective), `gpt-4o` (best quality)
        - **Anthropic:** `claude-3-5-sonnet-20241022`
        """)

    with st.expander("⚡ Optimizing Generation Speed", expanded=False):
        st.markdown("""
        **Faster Generation:**
        - Use smaller, focused requirements documents
        - Generate one test type at a time
        - Use faster models (Groq, local Ollama)
        - Disable unnecessary test types

        **Better Quality (Slower):**
        - Use larger models (GPT-4, Claude)
        - Include all test types
        - Enable all testing options
        - Add detailed client context
        """)

    with st.expander("🔒 Security & Privacy", expanded=False):
        st.markdown("""
        **Protecting Sensitive Data:**
        - Use local models (Ollama/vLLM) for confidential requirements
        - API keys are stored locally only (never shared)
        - Requirements are not logged or stored permanently
        - Generated tests are saved locally in database

        **API Key Safety:**
        - Never share your API keys
        - Use environment variables for production
        - Regenerate keys if compromised
        - Use read-only tokens when possible
        """)

    st.markdown("---")

    # Troubleshooting
    st.markdown("## 🔧 Troubleshooting")

    st.markdown("""
    ### Common Issues and Solutions

    **Problem:** LLM shows "Not Connected"
    - **Solution:** Check your API key is correct
    - **Solution:** For Ollama, ensure service is running (`ollama serve`)
    - **Solution:** Check internet connection for cloud APIs

    **Problem:** Generation takes too long or times out
    - **Solution:** Increase timeout in LLM Settings
    - **Solution:** Use a faster model
    - **Solution:** Split large requirements into smaller documents
    - **Solution:** Try generating test types separately

    **Problem:** Generated tests are not relevant
    - **Solution:** Add more detailed requirements
    - **Solution:** Create and use client context with specific rules
    - **Solution:** Try a different LLM model
    - **Solution:** Include more business context in requirements

    **Problem:** Selenium/Playwright scripts not generated
    - **Solution:** Ensure CodeLlama is installed for Ollama (`ollama pull codellama:7b`)
    - **Solution:** Check the model supports code generation
    - **Solution:** Try generating again (LLM responses can vary)

    **Problem:** Cannot upload requirements file
    - **Solution:** Ensure file is TXT, PDF, or DOCX format
    - **Solution:** Check file is not corrupted
    - **Solution:** Try converting to plain text format
    """)

    st.markdown("---")

    # Quick Reference Card
    st.markdown("## 🎯 Quick Reference")

    st.info("""
    **Keyboard Shortcuts:**
    - Navigate pages using sidebar buttons
    - Use browser refresh to reload application

    **File Formats Supported:**
    - Requirements: TXT, PDF, DOCX
    - Export: Excel, CSV, Markdown, ZIP

    **Test Types Available:**
    - Manual Test Cases (detailed steps)
    - Gherkin/Cucumber (BDD scenarios)
    - Selenium (Python automation)
    - Playwright (JavaScript/TypeScript)

    **Maximum Limits:**
    - Requirements file: No hard limit (recommended < 50 pages)
    - Test cases per generation: Depends on LLM and requirements
    - Client contexts: Unlimited
    - Generation history: Unlimited (stored locally)
    """)


def render_settings_page():
    """Render the LLM settings page."""
    # Show brand header
    st.markdown(get_brand_header(), unsafe_allow_html=True)

    st.markdown("### LLM Configuration")
    st.caption("Configure your language model provider")
    st.markdown("---")

    settings = get_settings()

    # Provider selection
    st.markdown("### Provider")

    provider_options = {
        LLMProvider.OLLAMA.value: "Ollama (Local)",
        LLMProvider.HUGGINGFACE.value: "Hugging Face",
        LLMProvider.OPENAI.value: "OpenAI",
        LLMProvider.GROQ.value: "Groq",
        LLMProvider.ANTHROPIC.value: "Anthropic",
    }

    selected_provider = st.radio(
        "Select LLM Provider",
        options=list(provider_options.keys()),
        format_func=lambda x: provider_options[x],
        index=list(provider_options.keys()).index(settings.llm_provider),
        horizontal=True
    )

    st.markdown("---")

    # Provider-specific settings
    if selected_provider == LLMProvider.OLLAMA.value:
        st.markdown("### Ollama Settings")

        ollama_url = st.text_input(
            "Base URL",
            value=settings.ollama_base_url,
            placeholder="http://localhost:11434"
        )

        # Fetch available models (for manual test case generation only)
        st.caption("Select the model for manual test case generation")
        col1, col2 = st.columns([3, 1])
        with col1:
            try:
                adapter = OllamaAdapter(ollama_url)
                available_models = adapter.get_models()
                if available_models:
                    # Filter out code models - they are auto-used for Selenium/Playwright
                    selectable_models = [m for m in available_models if 'codellama' not in m.lower() and 'code-llama' not in m.lower()]
                    if not selectable_models:
                        selectable_models = available_models  # Fallback if all models are code models
                    ollama_model = st.selectbox(
                        "Model (for test case generation)",
                        options=selectable_models,
                        index=selectable_models.index(settings.ollama_model) if settings.ollama_model in selectable_models else 0
                    )
                else:
                    ollama_model = st.text_input("Model", value=settings.ollama_model)
                    st.caption("Could not fetch models. Enter model name manually.")
            except Exception:
                available_models = []
                ollama_model = st.text_input("Model", value=settings.ollama_model)
                st.caption("Ollama not reachable. Enter model name manually.")

        with col2:
            if st.button("Test Connection"):
                try:
                    adapter = OllamaAdapter(ollama_url, ollama_model)
                    if adapter.is_available():
                        st.success("Connected!")
                    else:
                        st.error("Model not available")
                except Exception as e:
                    st.error(f"Failed: {e}")

        # Code generation model (for Selenium/Playwright) - auto-configured, not user-selectable
        st.markdown("---")
        st.markdown("**Code Generation Model** (for Selenium/Playwright)")
        st.info(
            "CodeLlama is automatically used for Selenium and Playwright script generation. "
            "This model is optimized for code generation and is not selectable — it is applied "
            "automatically when generating automation scripts."
        )

        # Auto-detect codellama from available models
        use_code_model = True
        ollama_code_model = getattr(settings, 'ollama_code_model', 'codellama:7b')

        try:
            if available_models:
                # Find the best code model automatically
                code_models = [m for m in available_models if 'codellama' in m.lower() or 'code-llama' in m.lower()]
                if code_models:
                    # Use the first available codellama model if current one is not installed
                    if ollama_code_model not in code_models:
                        ollama_code_model = code_models[0]
                    st.success(f"Code model: **{ollama_code_model}** (auto-detected)")
                else:
                    st.warning(
                        f"CodeLlama not found in installed models. Using **{ollama_code_model}** as configured. "
                        "For best results, install CodeLlama: `ollama pull codellama:7b`"
                    )
            else:
                st.caption(f"Code model: {ollama_code_model} (could not verify — Ollama not reachable)")
        except Exception:
            st.caption(f"Code model: {ollama_code_model}")

        st.markdown("---")

        # Timeout setting for local models
        ollama_timeout = st.slider(
            "Request Timeout (seconds)",
            min_value=60,
            max_value=1800,
            value=getattr(settings, 'ollama_timeout', 600),
            step=60,
            help="Increase this if generation times out. Local models can be slow on CPU."
        )
        st.caption(f"Current: {ollama_timeout // 60} minutes. Increase for complex requirements or slower hardware.")

    elif selected_provider == LLMProvider.HUGGINGFACE.value:
        st.markdown("### Hugging Face Inference Providers")
        st.caption("Access 1000+ models via HuggingFace's unified API — no local GPU required")

        hf_use_api = st.checkbox(
            "Use Inference API (cloud — recommended)",
            value=settings.hf_use_api
        )

        if hf_use_api:
            hf_api_token = st.text_input(
                "API Token",
                value=settings.hf_api_token,
                type="password",
                placeholder="hf_...",
                help="Get a token at https://huggingface.co/settings/tokens — select 'Make calls to Inference Providers' permission"
            )

            # Model selection with suggested models
            suggested_models = [
                "meta-llama/Llama-3.1-8B-Instruct",
                "meta-llama/Llama-3.3-70B-Instruct",
                "Qwen/Qwen2.5-7B-Instruct",
                "Qwen/Qwen2.5-Coder-32B-Instruct",
                "mistralai/Mistral-7B-Instruct-v0.2",
                "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                "HuggingFaceTB/SmolLM3-3B",
                "meta-llama/Llama-3.2-3B-Instruct",
            ]

            # Show dropdown with popular models + custom option
            model_options = suggested_models + ["-- Custom Model ID --"]
            current_model = settings.hf_model_id

            if current_model in suggested_models:
                default_index = suggested_models.index(current_model)
            else:
                default_index = len(model_options) - 1  # Custom

            selected_model = st.selectbox(
                "Model",
                model_options,
                index=default_index,
                help="Popular models available via HF Inference Providers. Auto-routes to the fastest available provider."
            )

            if selected_model == "-- Custom Model ID --":
                hf_model_id = st.text_input(
                    "Custom Model ID",
                    value=current_model if current_model not in suggested_models else "",
                    placeholder="org/model-name",
                    help="Enter any model from https://huggingface.co/models?inference_provider=all"
                )
            else:
                hf_model_id = selected_model

            st.info(
                "💡 **How it works:** Your request is routed through HuggingFace to the fastest available provider "
                "(Featherless AI, Together, Fireworks, SambaNova, etc.). Billed to your HF account at standard rates. "
                "HF PRO users get $2/month free credits."
            )
        else:
            hf_api_token = settings.hf_api_token
            hf_model_id = st.text_input(
                "Model ID",
                value=settings.hf_model_id,
                placeholder="mistralai/Mistral-7B-Instruct-v0.2"
            )
            st.info("⚠️ Local mode requires `transformers` and `torch` installed, plus sufficient GPU/RAM.")

    elif selected_provider == LLMProvider.OPENAI.value:
        st.markdown("### OpenAI Settings")

        openai_api_key = st.text_input(
            "API Key",
            value=settings.openai_api_key,
            type="password",
            placeholder="sk-..."
        )

        openai_model = st.selectbox(
            "Model",
            options=llm_config.AVAILABLE_MODELS[LLMProvider.OPENAI.value],
            index=llm_config.AVAILABLE_MODELS[LLMProvider.OPENAI.value].index(settings.openai_model)
            if settings.openai_model in llm_config.AVAILABLE_MODELS[LLMProvider.OPENAI.value] else 0
        )

    elif selected_provider == LLMProvider.GROQ.value:
        st.markdown("### Groq Settings")

        groq_api_key = st.text_input(
            "API Key",
            value=settings.groq_api_key,
            type="password",
            placeholder="gsk_..."
        )

        groq_model = st.selectbox(
            "Model",
            options=llm_config.AVAILABLE_MODELS[LLMProvider.GROQ.value],
            index=llm_config.AVAILABLE_MODELS[LLMProvider.GROQ.value].index(settings.groq_model)
            if settings.groq_model in llm_config.AVAILABLE_MODELS[LLMProvider.GROQ.value] else 0
        )

    elif selected_provider == LLMProvider.ANTHROPIC.value:
        st.markdown("### Anthropic Settings")

        anthropic_api_key = st.text_input(
            "API Key",
            value=settings.anthropic_api_key,
            type="password",
            placeholder="sk-ant-..."
        )

        anthropic_model = st.selectbox(
            "Model",
            options=llm_config.AVAILABLE_MODELS[LLMProvider.ANTHROPIC.value],
            index=llm_config.AVAILABLE_MODELS[LLMProvider.ANTHROPIC.value].index(settings.anthropic_model)
            if settings.anthropic_model in llm_config.AVAILABLE_MODELS[LLMProvider.ANTHROPIC.value] else 0
        )

    st.markdown("---")

    # Save button
    if st.button("Save Settings", type="primary", use_container_width=True):
        # Update settings based on provider
        settings.llm_provider = selected_provider

        if selected_provider == LLMProvider.OLLAMA.value:
            settings.ollama_base_url = ollama_url
            settings.ollama_model = ollama_model
            settings.ollama_timeout = ollama_timeout
            settings.ollama_code_model = ollama_code_model
            settings.use_code_model_for_scripts = True  # Always enabled - CodeLlama auto-used for scripts

        elif selected_provider == LLMProvider.HUGGINGFACE.value:
            settings.hf_model_id = hf_model_id
            settings.hf_use_api = hf_use_api
            settings.hf_api_token = hf_api_token

        elif selected_provider == LLMProvider.OPENAI.value:
            settings.openai_api_key = openai_api_key
            settings.openai_model = openai_model

        elif selected_provider == LLMProvider.GROQ.value:
            settings.groq_api_key = groq_api_key
            settings.groq_model = groq_model

        elif selected_provider == LLMProvider.ANTHROPIC.value:
            settings.anthropic_api_key = anthropic_api_key
            settings.anthropic_model = anthropic_model

        save_settings(settings)
        st.success("Settings saved!")
        st.session_state.settings_saved = True
        st.rerun()


def main():
    """Main application entry point."""
    init_session_state()

    # Apply sidebar visibility toggle
    if not st.session_state.sidebar_visible:
        st.markdown('<div class="sidebar-hidden">', unsafe_allow_html=True)

    render_sidebar()

    # Show floating button to unhide sidebar when hidden
    if not st.session_state.sidebar_visible:
        st.markdown("""
        <div style="
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 999;
        ">
            <button onclick="location.reload()" style="
                background: #6366f1;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
            ">
                👁️ Show Settings
            </button>
        </div>
        """, unsafe_allow_html=True)

    # Route to appropriate page
    page = st.session_state.current_page

    if page == 'generate':
        render_generate_page()
    elif page == 'clients':
        render_clients_page()
    elif page == 'history':
        render_history_page()
    elif page == 'settings':
        render_settings_page()
    elif page == 'help':
        render_help_page()

    if not st.session_state.sidebar_visible:
        st.markdown('</div>', unsafe_allow_html=True)

    # Author footer on every page
    st.markdown(get_author_footer(), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
