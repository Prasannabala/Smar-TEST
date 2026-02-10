# Test Case Generation Agent - MVP Implementation Plan

## Executive Summary

A professional-grade test case generation tool that transforms requirements documents into comprehensive manual test cases and optional automation scripts (Gherkin, Selenium, Playwright). The system supports client-specific project contexts for generating contextually accurate test cases.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT WEB UI                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │   Client    │  │ Requirements│  │    Test     │  │   Export   │ │
│  │   Setup     │  │   Upload    │  │  Generation │  │   Center   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        CORE ENGINE LAYER                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  LLM Adapter    │  │  Client Context │  │  Test Generator     │ │
│  │  (Ollama/APIs)  │  │  Manager        │  │  Pipeline           │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PERSISTENCE LAYER                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  SQLite DB      │  │  Client Docs    │  │  Generated Tests    │ │
│  │  (Metadata)     │  │  (JSON/Files)   │  │  (Exports)          │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
testcase-generation-agent/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── README.md                   # Project documentation
│
├── config/
│   ├── __init__.py
│   ├── settings.py             # Application settings & constants
│   └── llm_config.py           # LLM provider configurations
│
├── core/
│   ├── __init__.py
│   ├── llm_adapter.py          # Unified LLM interface (Ollama/OpenAI/Groq/etc.)
│   ├── document_parser.py      # Parse TXT, PDF, DOCX files
│   ├── test_generator.py       # Main test generation logic
│   └── export_handler.py       # Export to Excel, CSV, Markdown
│
├── models/
│   ├── __init__.py
│   ├── client_context.py       # Client project data models
│   ├── test_case.py            # Test case data structures
│   └── requirement.py          # Requirement document models
│
├── storage/
│   ├── __init__.py
│   ├── database.py             # SQLite database operations
│   └── file_manager.py         # File storage operations
│
├── templates/
│   ├── __init__.py
│   ├── manual_test.py          # Manual test case templates
│   ├── gherkin.py              # Gherkin feature templates
│   ├── selenium.py             # Selenium script templates
│   └── playwright.py           # Playwright JS templates
│
├── ui/
│   ├── __init__.py
│   ├── components.py           # Reusable UI components
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── client_setup.py     # Client context management page
│   │   ├── requirements.py     # Requirements upload page
│   │   ├── generate.py         # Test generation page
│   │   └── export.py           # Export center page
│   └── styles.py               # CSS and styling
│
├── data/
│   ├── clients/                # Client-specific data (JSON files)
│   ├── exports/                # Generated test case exports
│   └── app.db                  # SQLite database
│
└── tests/                      # Unit tests (future enhancement)
    └── __init__.py
```

---

## Component Specifications

### 1. LLM Adapter (`core/llm_adapter.py`)

**Purpose**: Unified interface for multiple LLM providers

**Supported Providers**:
| Provider | Type | Configuration |
|----------|------|---------------|
| Ollama | Local | Base URL (default: http://localhost:11434), Model name |
| Hugging Face | Local/API | Model ID, API Token (optional for local), Inference mode |
| OpenAI | Online | API Key, Model selection |
| Groq | Online | API Key, Model selection |
| Anthropic | Online | API Key, Model selection |

**Hugging Face Integration**:
- **Local Inference**: Run HF models locally via `transformers` library
- **API Inference**: Use HF Inference API for hosted models
- **Model Selection**: Text-generation models (e.g., `mistralai/Mistral-7B-Instruct-v0.2`, `meta-llama/Llama-2-7b-chat-hf`)

**Interface**:
```python
class LLMAdapter:
    def __init__(self, provider: str, config: dict)
    def generate(self, prompt: str, system_prompt: str = None) -> str
    def is_available(self) -> bool
    def get_models(self) -> list[str]  # For Ollama: fetch available models

class HuggingFaceAdapter(LLMAdapter):
    def __init__(self, model_id: str, use_api: bool = False, api_token: str = None)
    # Supports both local transformers pipeline and HF Inference API
```

**Default Configuration** (for your setup):
- Provider: Ollama
- Base URL: http://localhost:11434
- Model: mistral:latest

**Alternative**: Hugging Face models when better performance is needed

---

### 2. Client Context Manager (`storage/database.py` + `models/client_context.py`)

**Purpose**: Store and retrieve client-specific project information

**Client Context Data Model**:
```python
@dataclass
class ClientContext:
    id: str                      # UUID
    name: str                    # "Client A", "Client B"
    created_at: datetime
    updated_at: datetime

    # Project Details
    project_name: str
    project_description: str

    # Navigation & Rules
    navigation_rules: list[str]  # UI navigation paths, flows
    thumb_rules: list[str]       # Testing thumb rules, conventions
    business_rules: list[str]    # Domain-specific business rules

    # Technical Context
    tech_stack: list[str]        # Technologies used
    test_environment: str        # Environment details

    # Best Practices (uploadable)
    best_practices: list[str]    # Client-specific best practices

    # Raw uploaded documents
    uploaded_docs: list[dict]    # {filename, content, type}
```

**Storage**:
- SQLite for metadata (client list, timestamps, relationships)
- JSON files for detailed context (data/clients/{client_id}.json)

---

### 3. Test Case Models (`models/test_case.py`)

**Manual Test Case Structure**:
```python
@dataclass
class ManualTestCase:
    test_id: str                 # Auto-generated: TC_001, TC_002
    test_name: str               # Descriptive name
    test_description: str        # What this test verifies
    preconditions: list[str]     # Required setup
    test_steps: list[TestStep]   # Numbered steps
    expected_results: list[str]  # Expected outcomes per step
    priority: str                # High, Medium, Low
    category: str                # Functional, UI, Integration, etc.

@dataclass
class TestStep:
    step_number: int
    action: str                  # What to do
    test_data: str               # Input data (if any)
    expected_result: str         # Expected outcome for this step
```

**Automation Script Structure**:
```python
@dataclass
class AutomationScript:
    script_type: str             # "gherkin", "selenium", "playwright"
    filename: str                # Auto-generated filename
    content: str                 # The actual script code
    related_manual_tests: list[str]  # Links to manual test IDs
```

---

### 4. Test Generation Pipeline (`core/test_generator.py`)

**Pipeline Flow**:

```
┌──────────────────┐
│ 1. PARSE INPUT   │
│ - Requirements   │
│ - Client Context │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 2. ANALYZE       │
│ - Extract features│
│ - Identify flows │
│ - Map to rules   │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 3. GENERATE      │
│ MANUAL TESTS     │
│ (Always)         │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 4. ENHANCE       │
│ - Edge cases     │
│ - Negative tests │
│ - Boundary tests │
└────────┬─────────┘
         ▼
┌──────────────────────────────────────────┐
│ 5. GENERATE AUTOMATION (If Selected)     │
│ ┌──────────┐ ┌──────────┐ ┌───────────┐ │
│ │ Gherkin  │ │ Selenium │ │Playwright │ │
│ │ (BDD)    │ │ (Python) │ │   (JS)    │ │
│ └──────────┘ └──────────┘ └───────────┘ │
└────────┬─────────────────────────────────┘
         ▼
┌──────────────────┐
│ 6. FORMAT &      │
│    EXPORT        │
└──────────────────┘
```

**LLM Prompts Strategy**:

Each generation stage uses structured prompts with:
- Client context injection (navigation rules, thumb rules, business rules)
- Built-in testing best practices
- Output format enforcement (JSON structured output)

---

### 5. Export Handler (`core/export_handler.py`)

**Supported Formats**:

| Format | Use Case | Library |
|--------|----------|---------|
| Excel (.xlsx) | Manual test cases with structured columns | openpyxl |
| CSV | Simple data exchange | csv (built-in) |
| Markdown (.md) | Documentation, readable format | - |
| .feature | Gherkin files | - |
| .py | Selenium scripts | - |
| .spec.js | Playwright tests | - |

**Auto-naming Convention**:
```
{client_name}_{requirement_doc_name}_{test_type}_{YYYYMMDD_HHMMSS}.{ext}

Examples:
- ClientA_LoginRequirements_ManualTests_20240115_143022.xlsx
- ClientA_LoginRequirements_Gherkin_20240115_143022.feature
- ClientA_LoginRequirements_Playwright_20240115_143022.spec.js
```

---

### 6. UI Design (`ui/`)

**Design Principles**:
- Minimal, clean, professional
- Subtle, professional icons (using Streamlit's built-in or simple Unicode)
- Enterprise-grade look and feel
- Clear visual hierarchy

**Page Structure**:

#### Page 1: Client Setup
```
┌─────────────────────────────────────────────────────────────┐
│  ⚙ CLIENT CONFIGURATION                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Select Existing Client ▼]  or  [+ New Client]            │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Client Name: [________________________]                    │
│  Project:     [________________________]                    │
│                                                             │
│  Navigation Rules:                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Login → Dashboard → Settings                      │   │
│  │ • Dashboard → Reports → Export                      │   │
│  │ [+ Add Rule]                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Thumb Rules:                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • All forms require validation before submit        │   │
│  │ • Session timeout after 30 mins                     │   │
│  │ [+ Add Rule]                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Upload Context Documents: [Choose Files]                   │
│                                                             │
│  [Save Client Configuration]                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Page 2: Requirements & Generation
```
┌─────────────────────────────────────────────────────────────┐
│  📋 TEST CASE GENERATION                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Active Client: [Client A ▼]                               │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Requirements Document:                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📄 Drag & drop or click to upload                  │   │
│  │     Supports: TXT, PDF, DOCX                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Test Types to Generate:                                    │
│  ☑ Manual Test Cases (Required)                            │
│  ☐ Gherkin (BDD Feature Files)                             │
│  ☐ Selenium (Python)                                       │
│  ☐ Playwright (JavaScript)                                 │
│                                                             │
│  Generation Options:                                        │
│  ☑ Include edge cases                                      │
│  ☑ Include negative tests                                  │
│  ☑ Include boundary tests                                  │
│                                                             │
│  [Generate Test Cases]                                      │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│  Progress:                                                  │
│  ████████████░░░░░░░░ 60% - Generating manual tests...     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Page 3: Results & Export
```
┌─────────────────────────────────────────────────────────────┐
│  📤 GENERATED TEST CASES                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Summary: 24 Manual Tests | 24 Gherkin Scenarios           │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Manual Test Cases                                    [▼]   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ TC_001: Verify successful user login                │   │
│  │ TC_002: Verify login with invalid password          │   │
│  │ TC_003: Verify login with empty fields              │   │
│  │ ...                                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Export Options:                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Format: [Excel ▼]  [CSV]  [Markdown]                │   │
│  │                                                     │   │
│  │ [Download Manual Tests]                             │   │
│  │ [Download Gherkin Files]                            │   │
│  │ [Download All as ZIP]                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 7. LLM Settings Page (Sidebar or Dedicated)

```
┌─────────────────────────────────────────────────────────────┐
│  LLM CONFIGURATION                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Provider Type:                                             │
│  ○ Ollama (Local)                                          │
│  ○ Hugging Face (Local/API)                                │
│  ○ Online API (OpenAI, Groq, Anthropic)                    │
│                                                             │
│  ─── Ollama Settings ───                                    │
│  Base URL: [http://localhost:11434]                        │
│  Model:    [mistral:latest ▼]  [Refresh Models]            │
│  Status:   ● Connected                                      │
│                                                             │
│  ─── Hugging Face Settings ───                              │
│  Model ID: [mistralai/Mistral-7B-Instruct-v0.2]            │
│  Mode:     ○ Local (transformers)  ○ Inference API         │
│  API Token:[●●●●●●●●●●●●] (optional for public models)     │
│  Status:   ● Model Loaded                                   │
│                                                             │
│  ─── Online API Settings ───                                │
│  Provider: [OpenAI ▼] [Groq] [Anthropic]                   │
│  API Key:  [●●●●●●●●●●●●●●●●●●●●]                          │
│  Model:    [gpt-4 ▼]                                       │
│                                                             │
│  [Test Connection]  [Save Settings]                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Dependencies (requirements.txt)

```
# Core Framework
streamlit>=1.30.0

# LLM Integration - Local
langchain>=0.1.0
langchain-community>=0.0.10
ollama>=0.1.0

# Hugging Face Integration
transformers>=4.36.0
torch>=2.0.0
accelerate>=0.25.0
huggingface-hub>=0.20.0

# Document Processing
pypdf>=3.17.0
python-docx>=1.1.0

# Export
openpyxl>=3.1.2
pandas>=2.0.0

# Database
sqlalchemy>=2.0.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0

# Optional: Online LLM Providers (install as needed)
# openai>=1.0.0
# anthropic>=0.18.0
# langchain-groq>=0.0.1
```

**Note on Hugging Face Local Models**:
- Requires GPU for optimal performance (CUDA recommended)
- CPU inference possible but slower
- Models are downloaded and cached locally (~4-14GB depending on model size)

---

## Implementation Phases

### Phase 1: Foundation (Core Infrastructure)
1. Set up project structure
2. Implement LLM Adapter (Ollama focus)
3. Create database schema and storage layer
4. Build document parser (TXT, PDF, DOCX)

### Phase 2: Client Context Management
1. Client context data models
2. CRUD operations for clients
3. Client setup UI page
4. Document upload and parsing

### Phase 3: Test Generation Engine
1. Manual test case generator with structured output
2. Prompt engineering for thorough test cases
3. Edge case, negative, and boundary test generation
4. Integration with client context

### Phase 4: Automation Scripts
1. Gherkin generator
2. Selenium (Python) generator
3. Playwright (JavaScript) generator
4. Script-to-manual test linking

### Phase 5: Export & Polish
1. Excel export with formatting
2. CSV and Markdown export
3. ZIP bundling
4. Auto-naming implementation
5. UI polish and professional styling

---

## Sample Manual Test Case Output

```
┌────────────────────────────────────────────────────────────────────┐
│ TEST CASE: TC_001                                                  │
├────────────────────────────────────────────────────────────────────┤
│ TEST NAME: Verify successful user login with valid credentials     │
├────────────────────────────────────────────────────────────────────┤
│ DESCRIPTION: Validate that a registered user can successfully      │
│ login to the application using valid username and password         │
├────────────────────────────────────────────────────────────────────┤
│ PRECONDITIONS:                                                     │
│ • User account exists in the system                                │
│ • User is on the login page                                        │
│ • Browser cookies are cleared                                      │
├────────────────────────────────────────────────────────────────────┤
│ TEST STEPS:                                                        │
│                                                                    │
│ Step 1: Navigate to login page                                     │
│   Action: Open browser and navigate to {application_url}/login     │
│   Expected: Login page displays with username and password fields  │
│                                                                    │
│ Step 2: Enter valid username                                       │
│   Action: Enter "testuser@example.com" in username field           │
│   Expected: Username is accepted and displayed in the field        │
│                                                                    │
│ Step 3: Enter valid password                                       │
│   Action: Enter "ValidP@ssw0rd" in password field                  │
│   Expected: Password is masked and accepted                        │
│                                                                    │
│ Step 4: Click login button                                         │
│   Action: Click the "Login" button                                 │
│   Expected: User is redirected to dashboard                        │
│                                                                    │
│ Step 5: Verify successful login                                    │
│   Action: Observe the page after redirect                          │
│   Expected: Dashboard displays with user's name visible            │
├────────────────────────────────────────────────────────────────────┤
│ PRIORITY: High                                                     │
│ CATEGORY: Functional - Authentication                              │
└────────────────────────────────────────────────────────────────────┘
```

---

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM (Default) | Ollama + Mistral:latest | Local, no API costs, your preference |
| LLM (Alternative) | Hugging Face models | Flexibility for better performance models |
| Selenium Language | Python | Most common, your preference |
| Test Priority | Auto-assigned by LLM | Less manual work, intelligent assignment |
| Excel Format | Standard QA columns | Test ID, Name, Description, Steps, Expected Results, Priority, Status |
| Database | SQLite | Simple, file-based, no setup needed |
| UI Framework | Streamlit | Already in use, rapid development |
| Export | openpyxl + pandas | Robust Excel support |
| No Docker | Local installation | Your preference, simpler setup |
| No Tavily | LLM knowledge + templates | No external search dependency |

---

## Next Steps

Upon your approval of this plan:

1. I will restructure the existing codebase according to the new architecture
2. Implement Phase 1 (Foundation) first
3. Test with your Ollama + Mistral setup
4. Proceed through remaining phases iteratively

---

## Confirmed Decisions

| Question | Decision |
|----------|----------|
| Selenium language | Python |
| Test priority assignment | Auto-assigned by LLM |
| Excel columns | Standard QA format (Test ID, Name, Description, Steps, Expected Results, Priority, Status) |
| Hugging Face support | Yes - for models with better performance |

---

## Excel Export Format (Standard QA)

| Column | Description |
|--------|-------------|
| Test ID | Auto-generated (TC_001, TC_002, etc.) |
| Test Name | Descriptive test name |
| Description | What this test verifies |
| Preconditions | Required setup before test |
| Test Steps | Numbered steps with actions |
| Expected Results | Expected outcome for each step |
| Priority | High / Medium / Low (auto-assigned) |
| Status | New / In Progress / Passed / Failed / Blocked |

---

*Plan Version: 1.1*
*Updated: Added Hugging Face support, confirmed Selenium (Python), auto-priority, standard Excel format*
