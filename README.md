# ⚡ Smar-Test

**Smart + Test = Smartest Test Case Generation**

A professional-grade AI-powered tool for generating comprehensive test cases from requirements documents using advanced LLMs.

## Features

- **Multiple LLM Support**:
  - **vLLM** (high-performance local inference, 2-4x faster)
  - Ollama (local)
  - Hugging Face
  - OpenAI
  - Groq
  - Anthropic
- **Client Context Management**: Store client-specific rules, navigation patterns, and best practices
- **Comprehensive Test Generation**:
  - Manual Test Cases (always generated)
  - Gherkin BDD Feature Files (optional)
  - Selenium Python Scripts (optional)
  - Playwright JavaScript Tests (optional)
- **Multiple Export Formats**: Excel, CSV, Markdown, ZIP bundle
- **Professional UI**: Modern gradient-based design with smooth animations and progress tracking
- **Smart Branding**: Stylish interface with "Smar-Test" theme combining indigo, purple, and cyan gradients

## Quick Start

### Option 1: Local Installation (Recommended)

#### Prerequisites

- Python 3.9+
- Ollama running locally (recommended) with Mistral model

#### Installation

1. Clone the repository:
```bash
git clone https://github.com/Prasannabala/Smar-TEST.git
cd Smar-TEST
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start Ollama with Mistral:
```bash
ollama pull mistral:latest
ollama serve
```

5. Run Smar-Test:
```bash
streamlit run app.py
```

6. Open **Smar-Test** at http://localhost:8501 in your browser

**Data Storage:** All settings and client configs auto-save to `~/.smar-test/` folder

---

### Option 2: Streamlit Cloud (Online Hosting)

#### Deploy in 3 Steps:

1. **Push to GitHub** (already done):
   - Your code is at: https://github.com/Prasannabala/Smar-TEST

2. **Connect to Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Click "Create app"
   - Select repository: `Smar-TEST`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"

3. **Your app is live!**
   - Access at: `https://smar-test.streamlit.app` (or custom URL)

#### Using on Streamlit Cloud:

1. **First Visit**: Fill in LLM settings and client configs
2. **Save Settings**: Click sidebar "📤 Save" to download `smar_test_settings.json`
3. **Keep JSON File**: Save it on your computer
4. **Next Visit**: Click sidebar "📥 Load" → Upload the JSON file
5. **All settings restored!** (API keys excluded for security)

## Usage

### 1. Configure LLM (First Time)

1. Click "LLM Settings" in the sidebar
2. Select your provider (default: Ollama)
3. For Ollama, ensure it's running and select your model
4. Click "Save Settings"

### 2. Set Up Client (Optional but Recommended)

1. Click "Client Setup" in the sidebar
2. Create a new client with:
   - Client name and project details
   - Navigation rules (app flows)
   - Thumb rules (testing conventions)
   - Business rules (domain logic)
   - Best practices
3. Upload context documents if needed

### 3. Generate Test Cases

1. Click "Generate Tests" in the sidebar
2. Select a client context (optional)
3. Upload your requirements document (TXT, PDF, or DOCX)
4. Select test types to generate:
   - Manual Test Cases (always included)
   - Gherkin (BDD)
   - Selenium (Python)
   - Playwright (JavaScript)
5. Configure options (edge cases, negative tests, boundary tests)
6. Click "Generate Test Cases"
7. Review generated tests
8. Export in your preferred format

## Data Persistence & Settings

### Local Machine (`~/.smar-test/`)

When running locally, all settings and client data automatically save to:

```
~/.smar-test/
├── settings.json          # LLM provider config (auto-loaded on startup)
├── clients/               # Client configurations
│   ├── client_1.json
│   ├── client_2.json
│   └── ...
└── exports/               # Generated test files
    ├── tests_20240215.xlsx
    └── ...
```

**Benefits:**
- ✅ Settings auto-load on app startup
- ✅ All data on your machine (private)
- ✅ Survives app restarts
- ✅ Easy to backup (just copy the folder)

### Streamlit Cloud (Online)

When using Streamlit Cloud, use the sidebar buttons:

- **📤 Save**: Downloads `smar_test_settings.json` to your computer
- **📥 Load**: Upload saved JSON to restore settings

**Flow:**
```
1. Visit cloud app → Configure settings
2. Click "📤 Save" → Download JSON to computer
3. Next visit → Click "📥 Load" → Upload the JSON
4. ✅ All settings restored! (API keys excluded for security)
```

---

## Project Structure

```
Smar-TEST/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
│
├── config/                     # Configuration
│   ├── settings.py            # App settings
│   ├── settings_manager.py    # Settings persistence manager
│   └── llm_config.py          # LLM configurations
│
├── core/                       # Core logic
│   ├── llm_adapter.py         # LLM provider adapters
│   ├── document_parser.py      # Document parsing
│   ├── test_generator.py       # Test generation engine
│   └── export_handler.py       # Export functionality
│
├── models/                     # Data models
│   ├── client_context.py       # Client context model
│   ├── test_case.py            # Test case models
│   └── requirement.py          # Requirement model
│
├── storage/                    # Data persistence
│   ├── database.py            # SQLite operations
│   └── file_manager.py        # File management
│
├── templates/                  # Prompt templates
│   └── prompts.py             # LLM prompts
│
└── ui/                         # User interface
    ├── components.py          # UI components
    └── styles.py              # CSS styling
```

## Test Case Format

Generated manual test cases include:

| Field | Description |
|-------|-------------|
| Test ID | Unique identifier (TC_001, TC_002, etc.) |
| Test Name | Descriptive name |
| Description | What the test verifies |
| Preconditions | Required setup |
| Test Steps | Numbered steps with actions |
| Expected Results | Expected outcomes |
| Priority | High, Medium, Low (auto-assigned) |
| Status | New, In Progress, Passed, Failed, Blocked |
| Category | Functional, UI, Integration, etc. |
| Tags | Keywords for filtering |

## LLM Providers

### vLLM (Recommended for High-Performance Local) ⚡
- **2-4x faster** than Ollama or standard transformers
- Best GPU utilization and throughput
- Supports Llama, Qwen, Mistral, and more
- Requires NVIDIA GPU with CUDA

**Quick Start with Docker:**
```bash
# Start vLLM server
docker-compose --profile vllm up -d

# Configure in UI: Select "vLLM (High-Performance Local)" provider
```

### Ollama (Easy Local Setup)
- Free, runs locally
- No API key needed
- Works on CPU/GPU, all platforms
- Supports many models (Mistral, Llama, etc.)

### Hugging Face
- Local inference or API
- Many open-source models
- API token optional for public models

### OpenAI
- GPT-4, GPT-3.5
- Requires API key

### Groq
- Fast inference
- Llama, Mixtral models
- Requires API key

### Anthropic
- Claude models
- Requires API key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use and modify.

## Support

For issues and feature requests, please open a GitHub issue.
