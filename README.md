# ⚡ Smar-Test

**Smart + Test = Smartest Test Case Generation**

A professional-grade AI-powered tool for generating comprehensive test cases from requirements documents using advanced LLMs.

## Features

- **Multiple LLM Support**:
  - Ollama (local)
  - Hugging Face
  - OpenAI
  - Groq
  - Anthropic
- **Client Context Management**: Store client-specific rules, navigation patterns, and best practices
- **Comprehensive Test Generation**:
  - Manual Test Cases
  - Gherkin BDD Feature Files
  - Selenium Python Scripts
  - Playwright JavaScript Tests
- **Multiple Export Formats**: Excel, CSV, Markdown
- **Modern UI**: Clean, intuitive interface
- **Secure & Private**: All data stored locally in `~/.smar-test/`

## Quick Start

### Prerequisites

- Python 3.9+
- pip package manager
- Your favorite IDE (VS Code, PyCharm, etc.)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Prasannabala/Smar-TEST.git
cd Smar-TEST
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the application**:
```bash
streamlit run app.py
```

5. **Access the UI**:
   - Opens automatically in your browser at `http://localhost:8501`
   - Or manually navigate to that URL

## First Time Setup

### 1. Create a User Account
- Enter your username to isolate your workspace
- Your data will be stored in `~/.smar-test/`

### 2. Configure LLM Settings
- Click "⚙️ LLM Settings" in sidebar
- Select your LLM provider (Ollama, OpenAI, Groq, etc.)
- Configure provider-specific settings
- Click "Save Settings"

### 3. (Optional) Set Up Client Context
- Click "💼 Client Setup" in sidebar
- Create a new client with project details
- Add navigation rules, business rules, best practices
- Upload context documents if needed

### 4. Generate Test Cases
- Click "🚀 Generate Tests" in sidebar
- Upload your requirements document
- Select test types to generate
- Click "Generate Test Cases"
- Review and export results

## Data Storage

All your data is stored **locally** on your machine:

```
~/.smar-test/
├── settings.json          # Your LLM configuration
├── app.db                 # Client data and history
├── clients/               # Client-specific files
└── exports/               # Generated test files
```

**Benefits:**
- ✅ Your data stays on your computer
- ✅ No data sent to any servers
- ✅ Works completely offline
- ✅ Easy to backup

## API Keys & Security

API keys for cloud LLM providers (OpenAI, Groq, etc.) should be provided via **environment variables**:

```bash
# Set environment variables
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="gsk_..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Then run the app
streamlit run app.py
```

Or create a `.env` file:
```
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
ANTHROPIC_API_KEY=sk-ant-...
```

**Important**: API keys are never saved to disk and are only used during the session.

## Project Structure

```
Smar-TEST/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
│
├── config/                   # Configuration modules
│   ├── settings.py          # Application settings
│   ├── settings_manager.py  # Settings persistence
│   ├── user_session.py      # User authentication
│   └── llm_config.py        # LLM configurations
│
├── core/                     # Core functionality
│   ├── llm_adapter.py       # LLM provider adapters
│   ├── document_parser.py   # Document parsing
│   ├── test_generator.py    # Test generation engine
│   └── export_handler.py    # Export functionality
│
├── models/                   # Data models
│   ├── client_context.py    # Client context
│   ├── test_case.py         # Test case models
│   └── requirement.py       # Requirement model
│
├── storage/                  # Data persistence
│   ├── database.py          # SQLite database
│   └── file_manager.py      # File management
│
└── ui/                       # User interface
    ├── components.py        # UI components
    └── styles.py            # Styling
```

## LLM Providers

### Ollama (Local - Recommended)
- Free and runs on your computer
- No API key needed
- Works offline
- Supports: Mistral, Llama, Qwen, etc.

Setup:
```bash
ollama pull mistral:latest
ollama serve  # Keep running in separate terminal
```

### OpenAI
- Requires API key
- Models: GPT-4, GPT-3.5
- Get key: https://platform.openai.com/api-keys

### Groq
- Requires API key
- Fast inference
- Free tier available
- Get key: https://console.groq.com/keys

### Anthropic
- Requires API key
- Claude models
- Get key: https://console.anthropic.com

### Hugging Face
- Requires API token (optional for public models)
- Many open-source models
- Get token: https://huggingface.co/settings/tokens

## Testing Workflow

1. **Prepare requirements document** (TXT, PDF, or DOCX)
2. **Add client context** (optional but recommended)
3. **Configure LLM settings**
4. **Upload requirements** to the app
5. **Select test types** to generate
6. **Review generated tests**
7. **Export in preferred format**
8. **Import to your test management system**

## Security & Privacy

- ✅ All data stored locally on your machine
- ✅ API keys never saved to disk
- ✅ User authentication for workspace isolation
- ✅ No data sent to external servers (except LLM API calls)
- ✅ Complete control over your data

See `SECURITY.md` for detailed security documentation.

## Troubleshooting

### Issue: "Port 8501 already in use"
```bash
streamlit run app.py --server.port 8502
```

### Issue: "Module not found"
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "Ollama connection refused"
```bash
# Start Ollama in a separate terminal
ollama serve
```

### Issue: "API key not recognized"
```bash
# Verify environment variable is set
echo $OPENAI_API_KEY  # On Windows: echo %OPENAI_API_KEY%
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use and modify.

## Support

For issues and feature requests, please open a GitHub issue.

---

**Happy testing! 🚀**
