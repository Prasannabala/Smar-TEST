# Settings Persistence Guide - Smar-Test

## Quick Answer: Where Are Settings Saved?

**Location:** `~/.smar-test/settings.json`
- Windows: `C:\Users\<your-username>\.smar-test\settings.json`
- Linux/Mac: `~/.smar-test/settings.json`

**How to verify:**
1. Go to **🔧 Advanced Settings** page
2. Look at **📥 Load Settings** section on the left
3. If you see **"📂 Saved settings found at: `~/.smar-test/settings.json`"** → Settings are saved! ✅

---

## How Settings Persistence Works

### Step 1: Save Settings (Manual)
1. Go to **⚙️ LLM Settings** page in sidebar
2. Configure your LLM provider (Ollama, OpenAI, Groq, etc.)
3. Click **"Save Settings"** button
4. Settings are immediately saved to `~/.smar-test/settings.json`

### Step 2: Auto-Load on Restart (Automatic)
1. Close the Streamlit app
2. Restart the app: `streamlit run app.py`
3. App automatically:
   - Checks if `~/.smar-test/settings.json` exists
   - Loads all your saved settings
   - Applies them to current session
   - Falls back to defaults if file doesn't exist

### Step 3: Verify in Advanced Settings (Check)
1. Go to **🔧 Advanced Settings** page
2. Check **📥 Load Settings** section
3. **If settings exist:** You'll see "📂 Saved settings found at: `~/.smar-test/settings.json`"
4. **If no settings:** You'll see "No saved settings found..."

---

## Folder Structure

```
~/.smar-test/
├── settings.json          # Your LLM configuration (auto-saved when you click Save)
├── clients/               # Client configurations
│   ├── client_1.json
│   ├── client_2.json
│   └── ...
└── exports/              # Downloaded test files
    ├── tests_20240215.xlsx
    └── ...
```

---

## What Gets Saved vs. What Doesn't

### ✅ SAVED to JSON File
- LLM Provider choice (Ollama, OpenAI, Groq, Anthropic, HuggingFace)
- Model selections and configurations
- Base URLs and server settings
- Timeout values
- Generation preferences (edge cases, negative tests, boundary tests)
- Export format preferences

### ❌ NOT SAVED (For Security)
- API Keys (OpenAI, Groq, Anthropic, HuggingFace)
- Passwords and tokens
- Sensitive authentication data

**Why?** API keys should be:
1. Loaded from environment variables only
2. Entered manually each session (more secure)
3. Never stored in files (prevents accidental exposure)

---

## How to Verify Settings Are Saved

### Method 1: Check Advanced Settings Page
```
Action: Go to "🔧 Advanced Settings" page
Look for: "📂 Saved settings found at: ~/.smar-test/settings.json"
Result: Settings are saved! ✅
```

### Method 2: Check File Explorer
**Windows:**
```
1. Open File Explorer
2. Navigate to: C:\Users\<your-username>\.smar-test\
3. Look for: settings.json file
4. If it's there → Settings are saved! ✅
```

**Linux/Mac:**
```
1. Open Terminal
2. Run: ls ~/.smar-test/
3. Look for: settings.json file
4. If it's there → Settings are saved! ✅
```

### Method 3: View File Content
**Windows:** Double-click `settings.json` in File Explorer (opens in Notepad)

**Linux/Mac:**
```
cat ~/.smar-test/settings.json
```

Example content you'll see:
```json
{
  "llm_provider": "ollama",
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "qwen2.5:7b",
  "ollama_code_model": "codellama:7b",
  "ollama_timeout": 1800,
  "include_edge_cases": true,
  "include_negative_tests": true,
  "include_boundary_tests": true,
  "default_export_format": "excel"
}
```

---

## Common Scenarios

### Scenario 1: First-Time Setup
```
1. Install and start Streamlit app
2. No settings file exists yet
3. Go to "⚙️ LLM Settings"
4. Configure Ollama with model "qwen2.5:7b"
5. Click "Save Settings"
6. File created at: ~/.smar-test/settings.json
7. Next time you start app, settings auto-load! ✅
```

### Scenario 2: Settings Persist After Restart
```
1. Configure settings in LLM Settings page
2. Click "Save Settings"
3. File saved to: ~/.smar-test/settings.json
4. Close the Streamlit app
5. Restart the app: streamlit run app.py
6. Go to "⚙️ LLM Settings"
7. Your settings are still there! ✅ (Auto-loaded from file)
```

### Scenario 3: Backup and Restore
```
1. Go to "🔧 Advanced Settings"
2. Click "💾 Save Settings JSON" button
3. Download "smar_test_settings.json"
4. Keep it safe as a backup
5. To restore: Upload it back in the same page
6. All settings restored! ✅
```

### Scenario 4: Share Configuration with Team
```
1. User A configures settings and saves
2. Goes to "🔧 Advanced Settings"
3. Downloads "smar_test_settings.json"
4. Shares file with User B (via email, Slack, etc.)
5. User B goes to "🔧 Advanced Settings"
6. Uploads the JSON file
7. User B now has same configuration! ✅
```

---

## Troubleshooting

### Problem: "No saved settings found" message in Advanced Settings

**Possible causes:**
1. You haven't clicked "Save Settings" in LLM Settings page yet
2. The settings.json file was deleted
3. The file is in wrong location

**Solution:**
```
1. Go to "⚙️ LLM Settings" page
2. Configure your LLM provider (e.g., Ollama with qwen2.5:7b)
3. Click "Save Settings" button
4. Go back to "🔧 Advanced Settings"
5. You should now see "📂 Saved settings found at..." message
```

### Problem: Settings disappear after app restart

**Possible causes:**
1. Settings were never saved (you didn't click "Save Settings" button)
2. The file was accidentally deleted
3. File permissions issue

**Solution:**
```
1. Check if file exists: C:\Users\<username>\.smar-test\settings.json
2. If missing, go to LLM Settings and click "Save Settings"
3. If permissions issue, ensure file is readable/writable
4. Restart app again
```

### Problem: Can't find the `.smar-test` folder

**Windows:**
```
1. Open File Explorer
2. Click address bar at top
3. Paste: C:\Users\<your-username>\.smar-test\
4. Press Enter
5. Folder should appear
```

**If still not visible:**
```
1. Right-click in File Explorer → View → Options
2. Check "Show hidden files"
3. Now the .smar-test folder should be visible
```

**Linux/Mac:**
```
1. Open Terminal
2. Run: ls -la ~/.smar-test/
3. If folder doesn't exist, app will create it on first save
```

### Problem: Settings aren't loading on app restart

**Check:**
1. Does file exist at `~/.smar-test/settings.json`?
2. Is file readable/writable (check permissions)?
3. Is JSON file format valid (no syntax errors)?

**Solution:**
```
1. Delete the corrupted file (if applicable)
2. Go to LLM Settings and click "Save Settings" again
3. Restart app
4. Settings should load now
```

---

## Technical Details

### File Format
- **Type:** JSON (JavaScript Object Notation)
- **Encoding:** UTF-8
- **Human-readable:** Yes (can open in any text editor)
- **Portable:** Yes (can transfer between machines)

### API Key Exclusion Logic
The system automatically excludes any settings key that:
- Ends with `_key` (e.g., `openai_api_key`)
- Ends with `_token` (e.g., `hf_api_token`)

This ensures sensitive data is never written to the JSON file.

### Auto-Creation
- Folder `~/.smar-test/` is auto-created on first save
- File `settings.json` is auto-created on first save
- Subfolders `clients/` and `exports/` are auto-created

### Storage Limitations
- File size: ~1 KB (JSON is very compact)
- Maximum clients: Unlimited (stored in clients/ subfolder)
- Maximum settings: Unlimited (single JSON object)

---

## Important Notes

1. **Auto-load happens automatically** - No manual action needed on app restart
2. **Manual save required** - You must click "Save Settings" button to persist changes
3. **Privacy** - Settings stored locally on your machine only
4. **Security** - API keys never saved to file (for your protection)
5. **Persistence** - Survives app restarts, computer reboots, and app crashes
6. **Backup** - Always keep a backup copy using "💾 Save Settings JSON" button
7. **Portable** - Can transfer settings to other machines by downloading and uploading JSON

---

## Next Steps

1. **Configure your LLM:** Go to "⚙️ LLM Settings"
2. **Save settings:** Click "Save Settings" button
3. **Verify saved:** Go to "🔧 Advanced Settings" and check for "📂 Saved settings found..."
4. **Backup:** Download smar_test_settings.json from Advanced Settings page
5. **Test persistence:** Restart app and verify settings are still there
6. **Start generating:** Go to "🚀 Generate Tests" and create test cases!

---

## Support

If you have issues:
1. Check the Troubleshooting section above
2. Verify file exists at `~/.smar-test/settings.json`
3. Check file has readable/writable permissions
4. Try deleting and recreating the file by saving settings again
5. Open a GitHub issue if problem persists
