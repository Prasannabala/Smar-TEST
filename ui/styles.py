"""
Professional styling for Smar-Test application.
Modern, appealing, and professional design with gradient accents.
"""

# Smar-Test Professional Color Palette
# Inspired by modern SaaS applications with a tech-forward aesthetic
COLORS = {
    # Primary brand colors - Purple-Blue gradient theme
    "primary": "#6366f1",           # Vibrant indigo
    "primary_dark": "#4f46e5",      # Deep indigo
    "primary_light": "#818cf8",     # Light indigo
    "accent": "#8b5cf6",            # Purple accent
    "accent_secondary": "#06b6d4",  # Cyan accent

    # Semantic colors
    "success": "#10b981",           # Emerald green
    "warning": "#f59e0b",           # Amber
    "error": "#ef4444",             # Red
    "info": "#3b82f6",              # Blue

    # Neutral colors
    "background": "#f8fafc",        # Very light gray
    "background_secondary": "#f1f5f9", # Light gray
    "surface": "#ffffff",           # White
    "surface_elevated": "#ffffff",  # White with shadow
    "border": "#e2e8f0",            # Light border
    "border_hover": "#cbd5e1",      # Medium border

    # Text colors
    "text": "#0f172a",              # Almost black
    "text_secondary": "#475569",    # Medium gray
    "text_muted": "#94a3b8",        # Light gray
    "text_on_primary": "#ffffff",   # White

    # Gradient colors
    "gradient_start": "#6366f1",    # Indigo
    "gradient_mid": "#8b5cf6",      # Purple
    "gradient_end": "#06b6d4",      # Cyan
}


def apply_custom_styles():
    """
    Apply custom CSS styles to the Smar-Test application.
    Returns CSS string to be used with st.markdown.
    """
    return f"""
    <style>
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Global styles */
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}

        .stApp {{
            background: linear-gradient(135deg, {COLORS['background']} 0%, {COLORS['background_secondary']} 100%);
        }}

        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* Main container */
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }}

        /* Headers with gradient underline */
        h1, h2, h3 {{
            color: {COLORS['text']};
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        h1 {{
            font-size: 2.25rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            background: linear-gradient(90deg, {COLORS['gradient_start']}, {COLORS['gradient_mid']}, {COLORS['gradient_end']});
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            border-bottom: 3px solid;
            border-image: linear-gradient(90deg, {COLORS['gradient_start']}, {COLORS['gradient_mid']}, {COLORS['gradient_end']}) 1;
        }}

        h2 {{
            font-size: 1.75rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: {COLORS['text']};
        }}

        h3 {{
            font-size: 1.375rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: {COLORS['text_secondary']};
        }}

        /* Cards with elevated shadow */
        .card {{
            background: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }}

        .card:hover {{
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
        }}

        .card-header {{
            font-size: 1.25rem;
            font-weight: 600;
            color: {COLORS['text']};
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid {COLORS['border']};
        }}

        /* Gradient card variant */
        .gradient-card {{
            background: linear-gradient(135deg, {COLORS['gradient_start']} 0%, {COLORS['gradient_mid']} 50%, {COLORS['gradient_end']} 100%);
            color: white;
            border: none;
            box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
        }}

        .gradient-card h2, .gradient-card h3, .gradient-card p {{
            color: white !important;
        }}

        /* Status badges with modern design */
        .status-badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.375rem 0.875rem;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 600;
            letter-spacing: 0.025em;
        }}

        .status-success {{
            background: linear-gradient(135deg, {COLORS['success']} 0%, #059669 100%);
            color: white;
            box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
        }}

        .status-warning {{
            background: linear-gradient(135deg, {COLORS['warning']} 0%, #d97706 100%);
            color: white;
            box-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
        }}

        .status-error {{
            background: linear-gradient(135deg, {COLORS['error']} 0%, #dc2626 100%);
            color: white;
            box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
        }}

        .status-info {{
            background: linear-gradient(135deg, {COLORS['info']} 0%, {COLORS['primary']} 100%);
            color: white;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
        }}

        /* Modern buttons with gradient hover */
        .stButton > button {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.625rem 1.25rem;
            font-weight: 600;
            font-size: 0.875rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
        }}

        .stButton > button:hover {{
            background: linear-gradient(135deg, {COLORS['primary_dark']} 0%, {COLORS['accent']} 100%);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
            transform: translateY(-1px);
        }}

        .stButton > button:active {{
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
        }}

        .stButton > button:disabled {{
            background: {COLORS['text_muted']};
            opacity: 0.5;
            cursor: not-allowed;
        }}

        /* Secondary button */
        .secondary-btn > button {{
            background: transparent;
            color: {COLORS['primary']};
            border: 2px solid {COLORS['primary']};
            box-shadow: none;
        }}

        .secondary-btn > button:hover {{
            background: {COLORS['primary']};
            color: white;
            border-color: {COLORS['primary']};
        }}

        /* Input fields with modern styling */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div,
        .stNumberInput > div > div > input {{
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            padding: 0.625rem 0.875rem;
            transition: all 0.2s ease;
            background: {COLORS['surface']};
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > div:focus-within,
        .stNumberInput > div > div > input:focus {{
            border-color: {COLORS['primary']};
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            outline: none;
        }}

        /* File uploader with gradient border */
        .stFileUploader > div {{
            border: 2px dashed {COLORS['border']};
            border-radius: 12px;
            padding: 2rem;
            background: {COLORS['surface']};
            transition: all 0.3s ease;
        }}

        .stFileUploader > div:hover {{
            border-color: {COLORS['primary']};
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
        }}

        /* Checkboxes with custom styling */
        .stCheckbox > label {{
            font-weight: 500;
            color: {COLORS['text_secondary']};
        }}

        .stCheckbox > label:hover {{
            color: {COLORS['text']};
        }}

        /* Progress bar with gradient */
        .stProgress > div > div > div {{
            background: linear-gradient(90deg, {COLORS['gradient_start']}, {COLORS['gradient_mid']}, {COLORS['gradient_end']});
            border-radius: 10px;
        }}

        /* Expander with modern look */
        .streamlit-expanderHeader {{
            font-weight: 600;
            color: {COLORS['text']};
            background: {COLORS['background_secondary']};
            border-radius: 8px;
            padding: 0.75rem 1rem !important;
        }}

        .streamlit-expanderHeader:hover {{
            background: {COLORS['border']};
        }}

        /* Modern tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            border-bottom: 2px solid {COLORS['border']};
            padding-bottom: 0;
        }}

        .stTabs [data-baseweb="tab"] {{
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            color: {COLORS['text_muted']};
            border-bottom: 3px solid transparent;
            border-radius: 8px 8px 0 0;
            transition: all 0.2s ease;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            color: {COLORS['text']};
            background: {COLORS['background_secondary']};
        }}

        .stTabs [aria-selected="true"] {{
            color: {COLORS['primary']};
            border-bottom-color: {COLORS['primary']};
            background: {COLORS['background_secondary']};
        }}

        /* Sidebar with gradient accent */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLORS['surface']} 0%, {COLORS['background']} 100%);
            border-right: 1px solid {COLORS['border']};
        }}

        [data-testid="stSidebar"] .block-container {{
            padding-top: 2rem;
        }}

        /* Sidebar logo area */
        [data-testid="stSidebar"] h2:first-of-type {{
            background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['gradient_mid']}, {COLORS['gradient_end']});
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            letter-spacing: -0.05em;
        }}

        /* Metric cards with modern design */
        [data-testid="stMetricValue"] {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['gradient_mid']});
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        [data-testid="stMetricLabel"] {{
            font-size: 0.875rem;
            font-weight: 600;
            color: {COLORS['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        /* Table styling */
        .dataframe {{
            border: none !important;
            border-radius: 8px;
            overflow: hidden;
        }}

        .dataframe th {{
            background: linear-gradient(135deg, {COLORS['background_secondary']} 0%, {COLORS['border']} 100%) !important;
            color: {COLORS['text']} !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 1rem !important;
        }}

        .dataframe td {{
            border-bottom: 1px solid {COLORS['border']} !important;
            padding: 0.875rem !important;
        }}

        .dataframe tr:hover {{
            background: {COLORS['background']} !important;
        }}

        /* Alert boxes with modern styling */
        .stAlert {{
            border-radius: 8px;
            border: none;
            padding: 1rem 1.25rem;
        }}

        .stAlert > div {{
            font-weight: 500;
        }}

        /* Custom divider with gradient */
        .divider {{
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, {COLORS['border']} 50%, transparent 100%);
            margin: 2rem 0;
        }}

        /* Section title with icon */
        .section-title {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.125rem;
            font-weight: 700;
            color: {COLORS['text']};
            margin-bottom: 1rem;
            padding: 0.5rem 0;
        }}

        .section-title::before {{
            content: "";
            width: 4px;
            height: 24px;
            background: linear-gradient(180deg, {COLORS['gradient_start']}, {COLORS['gradient_mid']});
            border-radius: 2px;
        }}

        /* Priority badges with modern design */
        .priority-high {{
            background: linear-gradient(135deg, {COLORS['error']} 0%, #dc2626 100%);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
        }}

        .priority-medium {{
            background: linear-gradient(135deg, {COLORS['warning']} 0%, #d97706 100%);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            box-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
        }}

        .priority-low {{
            background: linear-gradient(135deg, {COLORS['success']} 0%, #059669 100%);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
        }}

        /* Rule item with hover effect */
        .rule-item {{
            background: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s ease;
        }}

        .rule-item:hover {{
            border-color: {COLORS['primary']};
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
            transform: translateX(4px);
        }}

        /* Connection status with modern indicator */
        .connection-status {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1rem;
            background: {COLORS['background_secondary']};
            border-radius: 8px;
            font-weight: 600;
        }}

        .status-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }}

        .status-dot.connected {{
            background: {COLORS['success']};
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
        }}

        .status-dot.disconnected {{
            background: {COLORS['error']};
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
        }}

        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.5;
            }}
        }}

        /* Test case card with elevated design */
        .test-case-card {{
            background: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }}

        .test-case-card:hover {{
            border-color: {COLORS['primary']};
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
            transform: translateY(-2px);
        }}

        .test-case-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.75rem;
        }}

        .test-case-title {{
            font-weight: 700;
            font-size: 1.125rem;
            color: {COLORS['text']};
        }}

        .test-case-description {{
            color: {COLORS['text_secondary']};
            font-size: 0.875rem;
            line-height: 1.5;
        }}

        /* Brand badge/pill */
        .brand-badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['gradient_mid']}, {COLORS['gradient_end']});
            color: white;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.875rem;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }}

        /* Loading spinner custom */
        .stSpinner > div {{
            border-top-color: {COLORS['primary']} !important;
        }}

        /* Success message box */
        .success-box {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
            border-left: 4px solid {COLORS['success']};
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin: 1rem 0;
        }}

        /* Info box */
        .info-box {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border-left: 4px solid {COLORS['primary']};
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin: 1rem 0;
        }}

        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 10px;
            height: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: {COLORS['background']};
        }}

        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(180deg, {COLORS['primary']}, {COLORS['accent']});
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS['primary_dark']};
        }}
    </style>
    """


def get_status_badge(status: str, text: str) -> str:
    """Generate HTML for a status badge."""
    status_class = f"status-{status}"
    return f'<span class="status-badge {status_class}">{text}</span>'


def get_priority_badge(priority: str) -> str:
    """Generate HTML for a priority badge."""
    priority_lower = priority.lower()
    return f'<span class="priority-{priority_lower}">{priority}</span>'


def get_connection_status(connected: bool) -> str:
    """Generate HTML for connection status indicator."""
    status_class = "connected" if connected else "disconnected"
    status_text = "Connected" if connected else "Disconnected"
    return f'''
    <div class="connection-status">
        <span class="status-dot {status_class}"></span>
        <span>{status_text}</span>
    </div>
    '''


def get_brand_badge() -> str:
    """Generate HTML for Smar-Test brand badge."""
    return '<span class="brand-badge">⚡ Smar-Test</span>'


def get_brand_header() -> str:
    """Generate HTML for main brand header."""
    return """
    <div style="text-align: center; padding: 0.5rem 0 1rem 0; margin-top: -1rem;">
        <h1 style="
            font-size: 3.5rem;
            font-weight: 800;
            margin: 0;
            padding: 0;
            letter-spacing: -0.05em;
            line-height: 1.1;
        ">
            <span style="
                color: #d97706;
                font-size: 3.5rem;
                filter: drop-shadow(0 2px 4px rgba(217, 119, 6, 0.5));
                display: inline-block;
                margin-right: 0.25rem;
                font-weight: 900;
                font-family: 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif;
                -webkit-text-fill-color: #d97706;
                paint-order: stroke fill;
            ">&#9889;</span>
            <span style="
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
                background-clip: text;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">Smar-Test</span>
        </h1>
        <p style="
            font-size: 0.875rem;
            color: #94a3b8;
            margin: 0.5rem 0 0 0;
            padding: 0;
        ">
            AI-Powered Test Case Generation for Modern QA Teams
        </p>
    </div>
    """


def get_success_box(message: str) -> str:
    """Generate HTML for success message box."""
    return f'<div class="success-box">✓ {message}</div>'


def get_info_box(message: str) -> str:
    """Generate HTML for info message box."""
    return f'<div class="info-box">ℹ️ {message}</div>'
