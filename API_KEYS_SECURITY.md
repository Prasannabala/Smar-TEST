# API Keys & Tokens Security Documentation

## Overview

All API keys and tokens (OpenAI, Groq, Anthropic, HuggingFace) are handled with **maximum security**:
- ❌ **NEVER saved to disk**
- ✅ **ONLY loaded from environment variables**
- ✅ **Filtered from all saved settings files**
- ✅ **Stored in memory only during session**

---

## Where Keys Are Stored

### ✅ SECURE: Environment Variables (Recommended)
Keys should be set in your environment:

```bash
# Windows (Command Prompt)
set OPENAI_API_KEY=sk-...
set HF_API_TOKEN=hf_...
set GROQ_API_KEY=gsk-...
set ANTHROPIC_API_KEY=sk-ant-...

# Windows (PowerShell)
$env:OPENAI_API_KEY = "sk-..."
$env:HF_API_TOKEN = "hf_..."

# Mac/Linux
export OPENAI_API_KEY="sk-..."
export HF_API_TOKEN="hf_..."
export GROQ_API_KEY="gsk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Or in .env file (Git-ignored)
OPENAI_API_KEY=sk-...
HF_API_TOKEN=hf_...
GROQ_API_KEY=gsk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### ❌ NOT STORED: Disk/Files
The following are **NEVER** written to disk:
- ❌ `~/.smar-test/settings.json` - Does NOT contain keys
- ❌ `~/.smar-test/app.db` - Does NOT store keys
- ❌ Any JSON export files - Do NOT contain keys

---

## How It Works

### 1. User Interface Input (Session Memory Only)

When you enter an API key in the Streamlit UI:

```python
# In app.py - Settings page
hf_api_token = st.text_input(
    "API Token",
    value=settings.hf_api_token,  # Empty string or env var
    type="password",              # Hidden input
    placeholder="hf_...",
)

settings.hf_api_token = hf_api_token  # Stored in memory ONLY
```

**What happens:**
- ✅ Key is stored in `settings.hf_api_token` (memory only)
- ✅ Key is used during test generation (current session)
- ❌ Key is NOT saved to disk
- ⏱️ Key is cleared when you close/refresh the app

### 2. Saving Settings (Sensitive Keys Filtered)

When you save LLM settings:

```python
# In config/settings.py - save() method
settings_dict = asdict(self)
settings_dict_safe = {
    k: v for k, v in settings_dict.items()
    if not k.endswith('_key') and not k.endswith('_token')
    # This filters out: openai_api_key, groq_api_key,
    #                   anthropic_api_key, hf_api_token
}

manager.save_settings(settings_dict_safe)  # Only safe data saved
```

**What gets saved to `~/.smar-test/settings.json`:**
```json
{
  "llm_provider": "huggingface",
  "hf_model_id": "meta-llama/Llama-3.1-8B-Instruct",
  "hf_use_api": true,
  "ollama_model": "qwen2.5:7b",
  ...
  // hf_api_token is NOT here!
  // openai_api_key is NOT here!
  // All sensitive keys are excluded!
}
```

### 3. Loading Settings (Keys From Environment Only)

When you restart the app:

```python
# In config/settings.py - load() method
settings = cls(**safe_data)  # Load from settings.json (no keys)

# Then load sensitive keys ONLY from environment
settings.openai_api_key = os.getenv('OPENAI_API_KEY', '')
settings.groq_api_key = os.getenv('GROQ_API_KEY', '')
settings.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
settings.hf_api_token = os.getenv('HF_API_TOKEN', '')
```

**What happens:**
- ✅ Settings loaded from disk (no keys)
- ✅ Keys loaded from environment variables
- ✅ Keys populated in memory
- ❌ Keys NOT saved to any file

---

## Security Layers

### Layer 1: File Filtering
```python
# In settings.py and settings_manager.py
settings_dict_safe = {
    k: v for k, v in settings_dict.items()
    if not k.endswith('_key') and not k.endswith('_token')
}
```
Any field ending with `_key` or `_token` is automatically excluded.

### Layer 2: Environment Variables
```bash
# Keys are passed via environment, not in files
export OPENAI_API_KEY="sk-..."
export HF_API_TOKEN="hf_..."
```

### Layer 3: .gitignore Protection
```
# In .gitignore
.env
.env.local
.env.production
credentials.json
```
Environment files are never committed to Git.

### Layer 4: Memory Only
Keys exist only in:
- ✅ Environment variables (system-level)
- ✅ Session memory (current app session)
- ❌ Disk files (NEVER)
- ❌ Git repository (NEVER)

---

## HuggingFace Token Specific Flow

### Input Flow
```
1. You enter token in Streamlit UI
   ↓
2. Token stored in settings.hf_api_token (memory)
   ↓
3. You click "Save Settings"
   ↓
4. Token FILTERED OUT before saving
   ↓
5. Only settings.json (no token) is saved
```

### Verification
```python
# To verify token is not saved:
import json
with open('~/.smar-test/settings.json', 'r') as f:
    data = json.load(f)
    print('hf_api_token' in data)  # Should be False!
```

### Usage Flow
```
1. During test generation
   ↓
2. settings.hf_api_token (from memory) is used
   ↓
3. API call made to HuggingFace
   ↓
4. Response processed
   ↓
5. Token never written anywhere
```

---

## Where Each Key Type Is Stored

| Key Type | Environment Var | settings.json | Database | Memory | Usage |
|----------|----------------|---------------|----------|--------|-------|
| OpenAI | ✅ Yes | ❌ No | ❌ No | ✅ Yes | API calls |
| Groq | ✅ Yes | ❌ No | ❌ No | ✅ Yes | API calls |
| Anthropic | ✅ Yes | ❌ No | ❌ No | ✅ Yes | API calls |
| HuggingFace | ✅ Yes | ❌ No | ❌ No | ✅ Yes | API calls |

---

## What IS Saved to Disk

### `~/.smar-test/settings.json` Contains:
- ✅ LLM provider name (e.g., "huggingface")
- ✅ Model IDs (e.g., "meta-llama/Llama-3.1-8B-Instruct")
- ✅ Model URLs (e.g., "http://localhost:11434")
- ✅ Timeout settings
- ✅ Export format preferences
- ❌ NO API KEYS
- ❌ NO TOKENS
- ❌ NO CREDENTIALS

### `~/.smar-test/app.db` Contains:
- ✅ Client configurations
- ✅ Test history
- ✅ Client rules and documents
- ❌ NO API KEYS
- ❌ NO TOKENS
- ❌ NO CREDENTIALS

### `~/.smar-test/clients/*.json` Contains:
- ✅ Client metadata
- ✅ Project information
- ✅ Tech stack
- ✅ Test rules
- ❌ NO API KEYS
- ❌ NO TOKENS
- ❌ NO CREDENTIALS

---

## Best Practices

### ✅ DO
1. **Set keys in environment variables**
   ```bash
   export HF_API_TOKEN="hf_..."
   ```

2. **Use .env files for local development**
   ```
   # .env (Git-ignored)
   HF_API_TOKEN=hf_...
   OPENAI_API_KEY=sk-...
   ```

3. **Use system environment for production**
   - Set in IDE environment variables
   - Set in Docker environment
   - Set in CI/CD secrets

4. **Keep environment files in .gitignore**
   ```
   # Already done!
   .env
   .env.local
   .env.production
   ```

### ❌ DON'T
1. ❌ Don't hardcode keys in code
2. ❌ Don't save keys to settings files
3. ❌ Don't commit .env files to Git
4. ❌ Don't share API keys
5. ❌ Don't store keys in database

---

## Verification Checklist

- [x] Keys NOT in settings.json
- [x] Keys NOT in app.db
- [x] Keys NOT in JSON client exports
- [x] Keys loaded from environment variables only
- [x] Keys filtered before saving
- [x] .env files in .gitignore
- [x] Session state cleared on logout
- [x] Memory-only key storage

---

## Troubleshooting

### Keys Not Loading
**Problem:** HuggingFace token is empty in the UI

**Solution:** Set environment variable before launching app
```bash
export HF_API_TOKEN="hf_..."
streamlit run app.py
```

### Keys Being Saved
**Problem:** Seeing API keys in settings.json

**This shouldn't happen** - Check that you're using the latest version with filtering enabled.

### Keys Lost on Refresh
**Problem:** Token disappears when page reloads

**This is expected behavior** - Session memory is cleared. Re-enter or set environment variable.

---

## Summary

🔒 **Security Architecture:**
- Environment Variables → Session Memory → API Calls
- Settings File → No Keys (ever)
- Database → No Keys (ever)
- Files → No Keys (ever)

✅ **All API keys are secure and follow industry best practices!**
