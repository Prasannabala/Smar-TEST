# Web vs Desktop App Split - Complete Guide

## Overview

Smar-Test now comes in **two versions** optimized for different use cases:

### 🌐 Web Version (Streamlit Cloud)
- **URL:** https://smar-test-cloud.streamlit.app
- **Providers:** API models only (OpenAI, Groq, Anthropic, HuggingFace)
- **Ollama:** Via ngrok tunnel setup
- **Installation:** None - just open the URL
- **Best For:** Cloud-based testing, shared teams, no local setup

### 💻 Desktop Version (Windows Executable)
- **Installation:** Download `.exe` file, run it
- **Providers:** API models + Local Ollama + vLLM
- **Ollama:** Use localhost:11434 directly
- **Installation:** Windows 10+ (no Python required)
- **Best For:** Local development, privacy, offline capability

---

## Architecture Comparison

```
┌─────────────────────────────────────────────────────────────┐
│                     Smar-Test Application                   │
│                                                              │
│  ┌──────────────────────┬──────────────────────────────┐   │
│  │                      │                              │   │
│  │   Environment        │     Provider Selection UI    │   │
│  │   Detection          │                              │   │
│  │   (config/           │  - Web: API only             │   │
│  │   environment.py)    │  - Desktop: All providers    │   │
│  │                      │                              │   │
│  └──────────────────────┴──────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────┬──────────────────────────────┐   │
│  │                      │                              │   │
│  │  Web App             │  Desktop App                 │   │
│  │  (app.py)            │  (app_desktop.py)            │   │
│  │                      │                              │   │
│  │  Running on:         │  Running as:                 │   │
│  │  - Streamlit Cloud   │  - PyInstaller .exe          │   │
│  │  - Shows download    │  - Local Windows exe         │   │
│  │    button            │  - Uses local Ollama         │   │
│  │  - Hides Ollama      │                              │   │
│  │                      │                              │   │
│  └──────────────────────┴──────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Shared Settings Storage                      │   │
│  │  ~/.smar-test/settings.json (both versions)          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Environment Detection

### How It Works

The app automatically detects its execution environment:

```python
# config/environment.py
env = detect_environment()
# Returns:
# - is_cloud: bool        # Running on Streamlit Cloud
# - is_desktop: bool      # Running as PyInstaller .exe
# - is_local: bool        # Running in local development
# - is_web: bool          # Running on web (cloud or local)
```

### Detection Logic

**Streamlit Cloud Detection:**
- File path starts with `/mount/src` (cloud mount point)
- OR `STREAMLIT_SERVER_HEADLESS=true` environment variable

**Desktop Detection:**
- `sys.frozen == True` (PyInstaller sets this)
- `sys.MEIPASS` exists (PyInstaller temp directory)

**Local Development:**
- Neither cloud nor desktop conditions met
- Running with `streamlit run app.py`

---

## Provider Availability by Environment

### Web Version (Streamlit Cloud)
```
LLM Provider Selection:
┌─────────────────────────────────┐
│ ✓ HuggingFace                   │
│ ✓ OpenAI                        │
│ ✓ Groq                          │
│ ✓ Anthropic                     │
│ ✗ Ollama (hidden)               │
│ ✗ vLLM (hidden)                 │
└─────────────────────────────────┘

Info Message:
"💡 Running on Streamlit Cloud - API models only.
Want to use Ollama? Download the desktop app above!"

Download Button:
[📥 Download for Windows] → GitHub Releases
```

### Desktop Version (Executable)
```
LLM Provider Selection:
┌─────────────────────────────────┐
│ ✓ Ollama (localhost:11434)       │
│ ✓ HuggingFace                   │
│ ✓ OpenAI                        │
│ ✓ Groq                          │
│ ✓ Anthropic                     │
│ ✓ vLLM                          │
└─────────────────────────────────┘

No Download Button
(Already running as executable)
```

### Local Development (Streamlit CLI)
```
LLM Provider Selection:
┌─────────────────────────────────┐
│ ✓ Ollama                         │
│ ✓ HuggingFace                   │
│ ✓ OpenAI                        │
│ ✓ Groq                          │
│ ✓ Anthropic                     │
│ ✓ vLLM                          │
└─────────────────────────────────┘

No Download Button
(Developer testing mode)
```

---

## File Structure

```
Smar-Test/
├── app.py                    # Web app (main)
├── app_desktop.py            # Desktop app (same code, different env)
│
├── config/
│   ├── environment.py        # NEW: Environment detection utilities
│   ├── settings.py           # LLM settings
│   ├── settings_manager.py   # Persistent storage
│   └── llm_config.py         # Provider definitions
│
├── build_desktop.py          # NEW: PyInstaller build script
├── requirements-build.txt    # NEW: Build dependencies
│
├── BUILD_DESKTOP_APP.md      # NEW: Build guide
├── WEB_DESKTOP_SPLIT.md      # This file
│
└── [other files unchanged]
```

---

## How to Use

### For Web Users (Streamlit Cloud)
1. Open: https://smar-test-cloud.streamlit.app
2. Select API model provider (OpenAI, Groq, etc.)
3. Enter API key
4. Generate test cases
5. OR: Click "📥 Download for Windows" to use desktop version

### For Desktop Users
1. Download `Smar-Test.exe` from GitHub Releases
2. Run the executable (Windows 10+)
3. App opens at `http://localhost:8501`
4. Select provider (Ollama recommended for local use)
5. Set Ollama URL: `http://localhost:11434`
6. Make sure Ollama is running locally first
7. Generate test cases offline!

### For Developers
```bash
# Run web version locally (for testing cloud behavior)
streamlit run app.py

# Build desktop version
pip install -r requirements-build.txt
python build_desktop.py

# Test desktop executable
dist/Smar-Test.exe
```

---

## Settings Synchronization

Both versions use **the same settings directory**:
```
~/.smar-test/
├── settings.json           # Shared settings
├── clients/                # Shared client configs
│   └── *.json
└── exports/                # Shared download history
```

### Benefits
- ✅ Switch between web and desktop seamlessly
- ✅ Settings persist across installations
- ✅ Client data shared between versions
- ✅ Export history preserved

### Example
1. Configure Ollama in desktop app
2. Run web app locally
3. Web app has same Ollama settings!
4. Publish to Streamlit Cloud
5. Cloud app starts fresh (no localhost option)

---

## Security Considerations

### API Keys (Never Saved to File)
```python
# API keys are NEVER saved to settings.json
# They're loaded from environment variables only

Environment Variables:
- OPENAI_API_KEY       (for OpenAI)
- GROQ_API_KEY         (for Groq)
- ANTHROPIC_API_KEY    (for Anthropic)
- HF_API_TOKEN         (for HuggingFace)
```

### Desktop App Security
- ✅ API keys not bundled in executable
- ✅ Must be provided at runtime
- ✅ Streamlit handles secure input
- ✅ No credentials transmitted unnecessarily

### Web App Security (Streamlit Cloud)
- ✅ API keys stored in Streamlit secrets
- ✅ Never visible in logs or UI
- ✅ Encrypted in transit
- ✅ Cannot use local Ollama (security)

---

## Migration Guide

### From Web to Desktop
1. Download `Smar-Test.exe` from GitHub Releases
2. Run the executable
3. App will load your existing settings from `~/.smar-test/`
4. Configure Ollama: `http://localhost:11434`
5. Start using locally!

### From Desktop to Web
1. Go to: https://smar-test-cloud.streamlit.app
2. Click ⚙️ LLM Settings
3. Select API provider (OpenAI, Groq, etc.)
4. Enter API key
5. Cloud version loads settings from `~/.smar-test/settings.json`
6. Note: Ollama will be hidden (cloud has no access to localhost)

### Switching Providers Mid-Session
1. Go to ⚙️ LLM Settings
2. Change provider
3. Click "Save Settings"
4. Settings saved to `~/.smar-test/settings.json`
5. Other version loads them on next startup

---

## Troubleshooting

### Web App Shows Only API Models
**Expected behavior** - Streamlit Cloud cannot access localhost.
- Solution: Use ngrok tunnel (see in-app instructions)
- Or: Use desktop app for local Ollama

### Desktop App Won't Start
- Check: Windows 10+ required
- Try: Run as Administrator
- Check: Antivirus not blocking .exe

### Settings Not Syncing
- Check: Both use `~/.smar-test/` directory
- Try: Manually check: `echo %USERPROFILE%\.smar-test\settings.json`
- Try: Delete settings and reconfigure

### Ollama Not Found
- Desktop: Make sure `ollama serve` is running in terminal
- Web: Must use ngrok tunnel (cannot access localhost)

---

## Technical Details

### Web App Detection
```python
is_cloud = (
    os.path.abspath(__file__).startswith("/mount/src") or
    os.getenv("STREAMLIT_SERVER_HEADLESS") == "true"
)
```

### Desktop App Detection
```python
is_desktop = (
    getattr(sys, 'frozen', False) and
    hasattr(sys, 'MEIPASS')
)
```

### Provider Filtering
```python
def get_available_providers(env):
    if env["is_cloud"]:
        return ["huggingface", "openai", "groq", "anthropic"]
    elif env["is_desktop"]:
        return ["ollama", "huggingface", "openai", "groq", "anthropic", "vllm"]
    else:  # local dev
        return ["ollama", "huggingface", "openai", "groq", "anthropic", "vllm"]
```

---

## Future Enhancements

- [ ] Auto-updater for desktop app
- [ ] Mac and Linux desktop versions
- [ ] Installer with Start Menu shortcut
- [ ] Portable version (USB-friendly)
- [ ] Web app auto-detection of local Ollama via LAN
- [ ] Settings sync between multiple machines

---

## Support

**Questions?** Create an issue on GitHub:
https://github.com/Prasannabala/Smar-TEST/issues

**Want to contribute?** See CONTRIBUTING.md

---

## Summary

| Aspect | Web | Desktop |
|--------|-----|---------|
| **Access** | URL + Browser | Download + Run |
| **Providers** | API only | API + Ollama + vLLM |
| **Ollama** | ngrok tunnel | localhost:11434 |
| **Settings** | `~/.smar-test/` | `~/.smar-test/` |
| **Python Needed** | No | No |
| **Always Updated** | Yes | Manual updates |
| **Offline** | No | Yes (with Ollama) |
| **Best For** | Cloud/Teams | Local Development |

Both versions work together seamlessly with shared settings storage! 🎉
