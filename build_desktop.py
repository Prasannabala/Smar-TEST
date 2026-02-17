#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for Smar-Test Desktop Application using PyInstaller.

This script converts the Streamlit app into a standalone Windows executable.

Usage:
    python build_desktop.py

Requirements:
    pip install pyinstaller

Output:
    dist/Smar-Test.exe - Standalone executable (no Python installation required)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def build_desktop_app():
    """Build the desktop application using PyInstaller."""

    print("=" * 70)
    print("Building Smar-Test Desktop Application")
    print("=" * 70)

    # Get project root directory
    project_root = Path(__file__).parent
    print(f"\nProject root: {project_root}")

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"[OK] PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("[ERROR] PyInstaller not found!")
        print("  Install with: pip install pyinstaller")
        sys.exit(1)

    # Check if app_desktop.py exists
    app_file = project_root / "app_desktop.py"
    if not app_file.exists():
        print(f"[ERROR] {app_file} not found!")
        sys.exit(1)
    print(f"[OK] Found {app_file}")

    # Clean previous builds
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    spec_file = project_root / "Smar-Test.spec"

    print("\nCleaning previous builds...")
    for path in [dist_dir, build_dir, spec_file]:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                print(f"  Removed {path}")
            else:
                try:
                    path.unlink()
                    print(f"  Removed {path}")
                except:
                    print(f"  Could not remove {path}, will continue anyway")

    # PyInstaller command
    print("\nRunning PyInstaller...")
    cmd = [
        "pyinstaller",
        "--name=Smar-Test",
        "--onefile",  # Create single executable
        "--windowed",  # No console window
        "--icon=ui/assets/icon.ico" if (project_root / "ui/assets/icon.ico").exists() else None,
        "--add-data=config:config",  # Include config directory
        "--add-data=core:core",  # Include core directory
        "--add-data=models:models",  # Include models directory
        "--add-data=storage:storage",  # Include storage directory
        "--add-data=ui:ui",  # Include ui directory
        "--collect-all=streamlit",  # Collect all Streamlit files
        "--hidden-import=config",
        "--hidden-import=core",
        "--hidden-import=models",
        "--hidden-import=storage",
        "--hidden-import=ui",
        "--hidden-import=requests",
        "--hidden-import=pandas",
        "--hidden-import=openai",
        "--hidden-import=groq",
        "--hidden-import=anthropic",
        "--hidden-import=huggingface_hub",
        "--hidden-import=jaraco",
        "--hidden-import=jaraco.classes",
        "--hidden-import=jaraco.functools",
        "--hidden-import=jaraco.context",
        "--hidden-import=jaraco.text",
        str(app_file),
    ]

    # Remove None values (missing icon)
    cmd = [c for c in cmd if c is not None]

    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        print(f"\n[OK] Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed with error code {e.returncode}")
        sys.exit(1)

    # Check if executable was created
    exe_path = dist_dir / "Smar-Test.exe"
    if exe_path.exists():
        file_size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"[OK] Executable created: {exe_path}")
        print(f"  File size: {file_size_mb:.1f} MB")
        print(f"\n[OK] Build complete! You can now run: {exe_path}")
    else:
        print(f"[ERROR] Executable not found at {exe_path}")
        sys.exit(1)


def create_installer():
    """Create a Windows installer using NSIS (optional)."""
    print("\n" + "=" * 70)
    print("Creating Windows Installer (optional)")
    print("=" * 70)

    # Check if NSIS is installed
    nsis_path = Path("C:/Program Files (x86)/NSIS/makensis.exe")
    if not nsis_path.exists():
        print("\n[INFO]  NSIS not found. Skipping installer creation.")
        print("   To create a professional installer:")
        print("   1. Install NSIS: https://nsis.sourceforge.io/")
        print("   2. Run this script again")
        return

    print("[OK] NSIS found, creating installer...")
    # TODO: Create NSIS script and build installer

    print("[INFO]  Installer creation not yet implemented")


if __name__ == "__main__":
    build_desktop_app()
    # create_installer()  # Uncomment when NSIS support is added

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Test the executable locally:")
    print("   dist/Smar-Test.exe")
    print("\n2. Upload to GitHub Releases:")
    print("   - Go to: https://github.com/Prasannabala/Smar-TEST/releases")
    print("   - Create new release")
    print("   - Upload Smar-Test.exe")
    print("\n3. Update download URL in app.py")
    print("=" * 70)
