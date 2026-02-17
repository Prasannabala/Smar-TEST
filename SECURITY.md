# Security Policy for Smar-Test

## Overview

Smar-Test takes security seriously. This document explains how sensitive information (API keys, tokens, credentials) is handled and protected.

## ✅ Security Guarantees

### 1. **API Keys Are NEVER Stored in Files**
- ❌ API keys are **NOT** saved to `settings.json`
- ❌ API keys are **NOT** saved to `~/.smar-test/settings.json`
- ✅ API keys are **ONLY** loaded from environment variables or Streamlit secrets

### 2. **Sensitive Data Filtering**
All settings files are automatically filtered to exclude:
- Fields ending with `_key` (e.g., `openai_api_key`, `groq_api_key`, `anthropic_api_key`)
- Fields ending with `_token` (e.g., `hf_api_token`)

This filtering happens in:
- `config/settings.py` - `save()` method (lines 79-89)
- `config/settings_manager.py` - `save_settings()` method (lines 59-85)

### 3. **Password Field Protection in UI**
All API key inputs use Streamlit's password field (`type="password"`):
- Keys are masked in the UI when typed
- Keys are never visible on screen
- Stored only in session state (in-memory)

### 4. **Environment Variable Priority**
API keys are loaded from environment variables in this order:
1. `OPENAI_API_KEY` environment variable
2. `GROQ_API_KEY` environment variable
3. `ANTHROPIC_API_KEY` environment variable
4. `HF_API_TOKEN` environment variable

See `config/settings.py` lines 100-104.

## 🔐 How to Provide API Keys

### Option 1: Environment Variables (Recommended)

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
$env:GROQ_API_KEY="gsk_..."
$env:ANTHROPIC_API_KEY="sk-ant-..."
$env:HF_API_TOKEN="hf_..."
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-...
set GROQ_API_KEY=gsk_...
set ANTHROPIC_API_KEY=sk-ant-...
set HF_API_TOKEN=hf_...
```

**Linux/macOS:**
```bash
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="gsk_..."
export ANTHROPIC_API_KEY="sk-ant-..."
export HF_API_TOKEN="hf_..."
```

**Permanent Setup (Linux/macOS - add to `~/.bashrc` or `~/.zshrc`):**
```bash
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="gsk_..."
export ANTHROPIC_API_KEY="sk-ant-..."
export HF_API_TOKEN="hf_..."
```

### Option 2: .env File

Create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
ANTHROPIC_API_KEY=sk-ant-...
HF_API_TOKEN=hf_...
```

⚠️ **IMPORTANT**: `.env` is in `.gitignore` and will never be committed to GitHub.

### Option 3: Streamlit Cloud Secrets (Recommended for Cloud)

For Streamlit Cloud deployment:
1. Go to your app settings
2. Navigate to "Secrets" section
3. Add your keys in the format:
```toml
OPENAI_API_KEY = "sk-..."
GROQ_API_KEY = "gsk_..."
ANTHROPIC_API_KEY = "sk-ant-..."
HF_API_TOKEN = "hf_..."
```

Streamlit will automatically load these into environment variables.

## 📁 What Gets Saved to Disk

**Safe to save (non-sensitive):**
- ✅ LLM provider choice (ollama, openai, groq, etc.)
- ✅ Model names
- ✅ Local server URLs
- ✅ Generation settings (edge cases, negative tests, etc.)
- ✅ User preferences

**Never saved (sensitive):**
- ❌ API keys
- ❌ Authentication tokens
- ❌ Personal credentials

## 🛡️ Data Storage Locations

**Local Development:**
```
~/.smar-test/
├── settings.json          (Non-sensitive config only)
├── clients/
│   ├── client_1.json
│   └── client_2.json
└── exports/               (Downloaded test files)
```

**Database:**
```
data/app.db                (SQLite database)
```

**Never Created:**
```
❌ credentials.json
❌ secrets.json
❌ api_keys.json
```

## ⚠️ Important Security Notes

### Do NOT:
- ❌ Hardcode API keys in the source code
- ❌ Commit `.env` files to GitHub
- ❌ Paste API keys in Slack/Teams/public channels
- ❌ Share settings.json files if they might contain keys
- ❌ Store API keys in browser localStorage or cookies

### Do:
- ✅ Use environment variables
- ✅ Use `.env` file (locally only, not committed)
- ✅ Use Streamlit Cloud Secrets (for cloud deployment)
- ✅ Rotate API keys regularly
- ✅ Use read-only API keys where possible
- ✅ Monitor API usage for suspicious activity

## 🔍 Security Audit

The code has been audited to ensure:
1. ✅ API keys are filtered before saving (settings.py, settings_manager.py)
2. ✅ API keys are loaded only from environment variables
3. ✅ UI password fields are used for key input
4. ✅ Settings files never contain sensitive data
5. ✅ Session state is in-memory (not persisted to disk)

## 🚨 If Your API Key Was Compromised

1. **Immediately regenerate the key:**
   - OpenAI: https://platform.openai.com/account/api-keys
   - Groq: https://console.groq.com/keys
   - Anthropic: https://console.anthropic.com/
   - HuggingFace: https://huggingface.co/settings/tokens

2. **Update environment variables** with the new key

3. **Check usage logs** for suspicious activity

4. **Monitor your account** for unauthorized charges

## 📞 Reporting Security Issues

If you discover a security vulnerability, please email: [your-email] instead of creating a public GitHub issue.

Do NOT disclose the vulnerability publicly until it has been patched.

## Version History

- **v1.2.0** - Added comprehensive security documentation and filtering
- **v1.1.0** - Fixed jaraco module import, improved build stability
- **v1.0.0** - Initial release

---

**Last Updated:** February 2026
**Security Level:** ✅ VERIFIED
