# Quick Verification Checklist

## Before Deploying to Streamlit Cloud

Use this checklist to verify everything works:

### ✅ Settings Persistence
- [ ] Run: `streamlit run app.py`
- [ ] Go to "⚙️ LLM Settings"
- [ ] Change a setting (model, provider, etc.)
- [ ] Click "Save Settings"
- [ ] Check confirmation message shows full path
- [ ] Close the browser completely
- [ ] Open http://localhost:8501 again
- [ ] Verify setting is still there ✓

### ✅ Client Creation
- [ ] Go to "💼 Client Setup"
- [ ] Create a test client: "TestClient123"
- [ ] Fill in description
- [ ] Close browser
- [ ] Open app again
- [ ] Client "TestClient123" appears in list ✓

### ✅ Settings File Creation
- [ ] Windows: Check `C:\Users\{your-username}\.smar-test\settings.json` exists
- [ ] Linux/Mac: Check `~/.smar-test/settings.json` exists
- [ ] File should contain JSON with your settings
- [ ] File should NOT contain any API keys ✓

### ✅ Backup/Restore
- [ ] Go to "🔧 Advanced Settings"
- [ ] Click "Download settings.json"
- [ ] File "settings.json" downloads
- [ ] Save it somewhere safe
- [ ] Change a setting
- [ ] Upload the downloaded file
- [ ] Verify old settings restored ✓

### ✅ Advanced Settings Display
- [ ] Settings path shown with full file path (not ~/...)
- [ ] Shows actual location like: `C:\Users\prasa\.smar-test\settings.json`
- [ ] No tilde (~) in the display ✓

### ✅ API Keys NOT in Settings
- [ ] Open downloaded settings.json in text editor
- [ ] Search for "api_key" - should find nothing
- [ ] Search for "token" - should find nothing
- [ ] Settings file should only have non-sensitive config ✓

### ✅ Environment Variables
- [ ] Create `.env` file in project root:
  ```
  OPENAI_API_KEY=test_key_123
  ```
- [ ] Run: `streamlit run app.py`
- [ ] Verify app starts without errors
- [ ] API key loaded from .env ✓

### ✅ LLM Settings Page
- [ ] Displays all provider options ✓
- [ ] Can select each provider (Ollama, OpenAI, Groq, etc.)
- [ ] Shows appropriate fields for each provider
- [ ] Save button works and shows confirmation ✓

### ✅ Test Generation
- [ ] Create a client
- [ ] Upload a requirements file (any text file)
- [ ] Configure generation settings
- [ ] Can select multiple test types (basic, edge cases, etc.)
- [ ] Export buttons appear ✓

### ✅ No Errors on Startup
- [ ] Run app: `streamlit run app.py`
- [ ] Check terminal for errors - should be clean ✓
- [ ] App loads without any warnings ✓

### ✅ Requirements File
- [ ] `requirements.txt` exists
- [ ] Contains all dependencies
- [ ] Run: `pip install -r requirements.txt`
- [ ] No errors during installation ✓

### ✅ Database & Files
- [ ] Check `data/` folder exists
- [ ] Check `data/app.db` exists
- [ ] Check `data/clients/` folder exists
- [ ] Check `data/exports/` folder exists ✓

### ✅ Configuration Files
- [ ] `.streamlit/config.toml` exists
- [ ] Contains light theme config
- [ ] `.env.example` exists (template for users)
- [ ] `.gitignore` contains `.env` ✓

---

## Summary

**All checks passed?** ✅ Ready to deploy!

**If any check failed:**
1. Note which check failed
2. Check logs: `streamlit run app.py 2>&1`
3. Fix the issue
4. Re-run the failing checks
5. Once all pass, deploy to Streamlit Cloud

---

## Deployment to Streamlit Cloud

When ready:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for production deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Connect GitHub repo
   - Select: `Prasannabala/Smar-TEST`
   - Main file: `app.py`
   - Click "Deploy"

3. **Add Secrets:**
   - Go to app → Settings → Secrets
   - Add environment variables:
     ```
     HF_API_TOKEN=your_token_here
     OPENAI_API_KEY=your_key_here
     GROQ_API_KEY=your_key_here
     ANTHROPIC_API_KEY=your_key_here
     ```

4. **Test on Cloud:**
   - Visit your Streamlit Cloud URL
   - Run through all checks above
   - Share with users!

---

**Good luck! 🚀**
