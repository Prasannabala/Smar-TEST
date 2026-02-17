# Application Initialization & Data Isolation

## 🔐 Important: User-Isolated Settings

This application uses **per-user settings** to ensure data isolation and security. Each user manages their own configuration completely separate from other users.

## 📁 Directory Structure

### Project Directory (Git Repository)
```
smar-test/
├── app.py                    (Main app)
├── app_desktop.py            (Desktop executable)
├── settings.template.json    (Template - reference only)
├── config/                   (Application code)
├── core/                     (Core modules)
├── models/                   (Data models)
├── storage/                  (Database)
├── ui/                       (User interface)
└── data/                     (⚠️ LOCAL ONLY - never committed to git)
    ├── settings.json         (❌ NOT USED - use ~/.smar-test/ instead)
    ├── app.db                (❌ NOT USED - use ~/.smar-test/ instead)
    ├── clients/              (❌ NOT USED - use ~/.smar-test/ instead)
    └── exports/              (❌ NOT USED - use ~/.smar-test/ instead)
```

### User Home Directory (Per-User Settings)
```
~/.smar-test/
├── settings.json             (✅ YOUR settings - stored here)
├── clients/
│   ├── client_1.json         (✅ YOUR client data)
│   ├── client_2.json
│   └── ...
├── exports/                  (✅ YOUR exported test files)
└── (future: app.db)          (✅ YOUR database - per user)
```

**Platform-specific paths:**
- **Windows**: `C:\Users\{username}\.smar-test\`
- **macOS**: `/Users/{username}/.smar-test/`
- **Linux**: `/home/{username}/.smar-test/`

## ✅ First Run - Clean Initialization

When you first run the application:

1. **No settings.json exists yet** ✓
2. **App starts with clean defaults**
3. **SettingsManager creates** `~/.smar-test/` directory
4. **You configure your settings** via the UI
5. **Settings are saved to** `~/.smar-test/settings.json` (YOUR settings only)
6. **Next time you run** - your settings are automatically loaded

## ⚠️ What Changed

| Item | Before | Now |
|------|--------|-----|
| Settings stored in | `data/settings.json` (shared) | `~/.smar-test/settings.json` (per-user) |
| Client data stored in | `data/clients/` (shared) | `~/.smar-test/clients/` (per-user) |
| Exports stored in | `data/exports/` (shared) | `~/.smar-test/exports/` (per-user) |
| Git commits | Included settings.json | Never includes user data |
| Data isolation | ❌ No - all users shared | ✅ Yes - each user isolated |

## 🚀 How to Use

### First Time Setup

1. **Clone/Download** the repository
2. **Run the application**
   ```bash
   streamlit run app.py
   ```
   OR
   ```
   Double-click: Smar-Test.exe
   ```
3. **First-run experience:**
   - App detects no settings exist
   - Shows default LLM options
   - You select your LLM provider
   - You enter your API keys (if needed)
   - Click "Save Settings"
4. **Settings saved** to `~/.smar-test/settings.json`
5. **Next time** - all settings load automatically

### Switching Between Multiple Users

On the same computer, different users can:
- Have their own `~/.smar-test/` directory
- Each with their own settings.json
- Each with their own clients
- No cross-contamination

### Backup Your Settings

To backup your settings:
```bash
# Windows
copy C:\Users\YourUsername\.smar-test\settings.json backup.json

# macOS/Linux
cp ~/.smar-test/settings.json backup.json
```

To restore:
```bash
# Windows
copy backup.json C:\Users\YourUsername\.smar-test\settings.json

# macOS/Linux
cp backup.json ~/.smar-test/settings.json
```

## 🔒 Security

### What's Stored in User Directory
✅ **Safe (non-sensitive):**
- LLM provider choice
- Model names
- Server URLs
- Generation preferences
- Client information (test requirements, etc.)

❌ **NEVER stored in files:**
- API keys (loaded from environment variables)
- Authentication tokens
- Passwords

### Environment Variables
API keys should be provided via environment variables:
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
$env:GROQ_API_KEY="gsk_..."
```

Or create `~/.env` (local file, not committed):
```
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

## 🔍 Verification

To verify the application is properly isolated:

1. Check that `data/` directory is empty or contains only `.gitkeep`:
   ```bash
   ls -la data/
   ```

2. Check that `.gitignore` excludes `data/`:
   ```bash
   cat .gitignore | grep data
   ```

3. Check that your settings are in home directory:
   ```bash
   # Windows
   dir %USERPROFILE%\.smar-test\

   # macOS/Linux
   ls ~/.smar-test/
   ```

4. Verify git doesn't track user data:
   ```bash
   git status data/
   # Should show: "On branch main, nothing to commit"
   ```

## 📝 Configuration File Format

Your `~/.smar-test/settings.json` will contain:

```json
{
  "llm_provider": "openai",
  "openai_model": "gpt-4",
  "groq_model": "llama-3.1-70b-versatile",
  "anthropic_model": "claude-3-sonnet-20240229",
  "include_edge_cases": true,
  "include_negative_tests": true,
  "include_boundary_tests": true,
  "default_export_format": "excel"
}
```

**NOT included:**
- API keys (loaded from environment)
- Personal data (if shared)
- Sensitive information

## ✨ Benefits

✅ **Data Isolation** - Each user has separate settings
✅ **Security** - No user data in git repository
✅ **Portability** - Settings follow you on your account
✅ **Clean Repository** - Only code, no user artifacts
✅ **Multi-User Support** - Multiple users on same computer
✅ **Easy Backup** - Just copy `~/.smar-test/` directory

## 🆘 Troubleshooting

**Q: Settings not loading on next run**
A: Check that `~/.smar-test/settings.json` exists and is readable

**Q: "No module named jaraco" error**
A: This is a PyInstaller dependency issue - should be fixed in latest version

**Q: Client data appears from another user**
A: This indicates you may be looking at the old `data/clients/` directory. Use `~/.smar-test/clients/` instead

**Q: Want to reset settings to defaults**
A: Delete `~/.smar-test/settings.json` and restart the app

---

**Last Updated:** February 2026
**Version:** 1.3.0+
