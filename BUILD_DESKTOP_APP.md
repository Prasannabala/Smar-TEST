# Building Smar-Test Desktop Application

This guide explains how to build the Smar-Test application into a standalone Windows executable (`.exe` file).

## Overview

The desktop app is built using **PyInstaller**, which converts the Python/Streamlit app into a single executable file that:
- ✅ Runs on Windows without Python installed
- ✅ Doesn't require any dependencies
- ✅ Can use local Ollama models (localhost:11434)
- ✅ Can also use API models (OpenAI, Groq, etc.)
- ✅ Settings persist to `~/.smar-test/` directory

## Two Ways to Get the Desktop App

### Option 1: Download Pre-Built (Recommended for Users)
Most users should just **download the pre-built executable** from GitHub Releases:
- No development environment needed
- No compilation time
- Just download and run

**Link:** https://github.com/Prasannabala/Smar-TEST/releases

### Option 2: Build from Source (For Developers)
If you want to modify the app and rebuild, follow this guide.

---

## Prerequisites

### System Requirements
- **OS:** Windows 10 or later (64-bit)
- **RAM:** 4GB minimum
- **Disk Space:** 500MB for build, 200MB for final executable
- **Python:** 3.9 or later (not needed if just downloading pre-built)

### Software Requirements (For Building)

1. **Python 3.9+**
   ```bash
   python --version
   ```
   If not installed, download from: https://www.python.org/downloads/

2. **Git** (for cloning the repo)
   ```bash
   git --version
   ```
   Download from: https://git-scm.com/

---

## Step-by-Step Build Instructions

### Step 1: Clone the Repository
```bash
git clone https://github.com/Prasannabala/Smar-TEST.git
cd Smar-TEST
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

Windows PowerShell:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```bash
# Install main dependencies
pip install -r requirements.txt

# Install build dependencies
pip install -r requirements-build.txt
```

### Step 4: Create Desktop App Version
The `app_desktop.py` file should already exist in the repo. If not:
```bash
copy app.py app_desktop.py
```

### Step 5: Run the Build Script
```bash
python build_desktop.py
```

This will:
1. Clean previous builds
2. Run PyInstaller
3. Create `dist/Smar-Test.exe`

**Build time:** 2-5 minutes (depends on your system)

### Step 6: Test the Executable
```bash
dist\Smar-Test.exe
```

The app should launch with Streamlit:
- Default browser opens at `http://localhost:8501`
- Settings save to `~/.smar-test/`
- You can use local Ollama or API keys

---

## Troubleshooting Build Issues

### Issue: "python: command not found"
**Solution:** Python is not in your PATH. Either:
- Add Python to PATH during reinstall, OR
- Use full path: `C:\Python310\python.exe build_desktop.py`

### Issue: "pyinstaller: command not found"
**Solution:** PyInstaller not installed. Run:
```bash
pip install -r requirements-build.txt
```

### Issue: Build runs but `.exe` file not created
**Solution:** Check for errors in the build output. Common causes:
- Missing dependencies (install with `pip install -r requirements.txt`)
- Antivirus software blocking build (disable temporarily)
- Disk space issue (free up at least 500MB)

### Issue: `.exe` file runs but closes immediately
**Solution:** Check the console output by running:
```bash
dist\Smar-Test.exe 2>&1 | more
```
Or use a text editor to create a batch file:

**run-debug.bat:**
```batch
@echo off
dist\Smar-Test.exe
pause
```

Then run `run-debug.bat` to see error messages.

---

## Publishing the Desktop App

Once you've successfully built and tested the `.exe` file:

### Step 1: Create GitHub Release
1. Go to: https://github.com/Prasannabala/Smar-TEST/releases
2. Click "Create a new release"
3. Tag: `v1.0-desktop` (or appropriate version)
4. Title: "Smar-Test Desktop v1.0 - Windows Executable"
5. Attach file: `dist/Smar-Test.exe`

### Step 2: Update Download Button in App
In `app.py`, find the download button code (around line 187):
```python
st.link_button(
    "⬇️ Download for Windows",
    url="https://github.com/Prasannabala/Smar-TEST/releases/download/v1.0-desktop/Smar-Test.exe",
    use_container_width=True
)
```

Update the URL to point to your release.

### Step 3: Announce Release
- Update README.md
- Post on social media
- Create release notes

---

## Understanding the Build Process

### What PyInstaller Does
1. **Analyzes** your Python code for imports
2. **Bundles** all dependencies into the executable
3. **Compiles** to machine code (via UPX)
4. **Creates** a standalone `.exe` file

### What Gets Included
- Python runtime (3MB)
- All pip packages from `requirements.txt`
- Streamlit framework
- All app code and configs
- UI assets and styles

### Why File Size is Large (~200-300MB)
- Python runtime: ~50MB
- Streamlit: ~30MB
- NumPy/Pandas/SciPy: ~80MB
- LLM libraries (OpenAI, Groq, etc.): ~30MB
- Other dependencies: ~20MB

### Reducing File Size (Advanced)
You can reduce size by:
1. Using `pyinstaller --strip` flag
2. Removing unused dependencies
3. Using UPX compression

---

## Version Management

### Updating the Desktop App
When you make changes to `app.py`:

1. **Update app_desktop.py too:**
   ```bash
   copy app.py app_desktop.py
   ```

2. **Increment version** in build script or release notes

3. **Rebuild:**
   ```bash
   python build_desktop.py
   ```

4. **Test locally** before releasing

5. **Create new GitHub Release** with updated version

---

## Desktop vs Web App Differences

| Feature | Web (Streamlit Cloud) | Desktop (Executable) |
|---------|----------------------|----------------------|
| **Provider Selection** | API models only | API + Local Ollama + vLLM |
| **Ollama Support** | Via ngrok tunnel | Via localhost:11434 |
| **Settings Storage** | ~/.smar-test/ | ~/.smar-test/ (same) |
| **Installation** | Just open URL | Download & run .exe |
| **Requires Python** | No | No |
| **Always Up-to-date** | Yes | No (manual updates) |
| **Offline Capable** | No (needs API) | Yes (with local Ollama) |

---

## FAQ

**Q: Can I modify the desktop app for myself?**
A: Yes! Clone the repo, modify `app_desktop.py`, and rebuild with `build_desktop.py`.

**Q: Do I need to rebuild for Mac/Linux?**
A: This guide is for Windows. For Mac/Linux, use platform-specific build scripts or use `--onedir` instead of `--onefile`.

**Q: Will the executable be detected as malware?**
A: PyInstaller executables sometimes trigger antivirus warnings because they bundle Python. This is normal and harmless. You can:
- Use a code signing certificate (costs ~$300/year)
- Build on the target platform (Windows)
- Distribute from your website with clear instructions

**Q: Can I distribute the .exe commercially?**
A: Check the licenses of all included dependencies. Streamlit is Apache 2.0 (allows commercial use), but verify others in `requirements.txt`.

---

## Next Steps

1. ✅ Build the desktop app: `python build_desktop.py`
2. ✅ Test it: `dist\Smar-Test.exe`
3. ✅ Create GitHub Release with the `.exe` file
4. ✅ Update download button URL in app.py
5. ✅ Share with users!

---

**Questions?** Create an issue on GitHub: https://github.com/Prasannabala/Smar-TEST/issues

Happy building! 🚀
