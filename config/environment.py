"""
Environment detection utility for Smar-Test.

Detects the current execution environment (Streamlit Cloud, Desktop app, or local development)
and provides helper functions for environment-specific behavior.
"""

import os
import sys
from typing import Dict


def detect_environment() -> Dict[str, bool]:
    """
    Detect the current execution environment.

    Returns:
        Dict with boolean flags for different environments:
        - is_cloud: Running on Streamlit Cloud
        - is_desktop: Running as PyInstaller executable
        - is_local: Running on local machine (development)
        - is_web: Running on web (cloud or local Streamlit)
    """
    # Check if running as PyInstaller executable
    is_desktop = getattr(sys, 'frozen', False) and hasattr(sys, 'MEIPASS')

    # Check if running on Streamlit Cloud
    # Streamlit Cloud mounts app at /mount/src and sets STREAMLIT_SERVER_HEADLESS=true
    is_cloud = (
        os.path.abspath(__file__).startswith("/mount/src") or
        os.getenv("STREAMLIT_SERVER_HEADLESS") == "true"
    )

    # Running locally (development)
    is_local = not is_cloud and not is_desktop

    # Web version (cloud or local Streamlit)
    is_web = is_cloud or (not is_desktop)

    return {
        "is_cloud": is_cloud,
        "is_desktop": is_desktop,
        "is_local": is_local,
        "is_web": is_web,
    }


def get_available_providers(env: Dict[str, bool]) -> list:
    """
    Get list of available LLM providers based on environment.

    Args:
        env: Dictionary from detect_environment()

    Returns:
        List of provider names that should be available
    """
    all_providers = ["ollama", "huggingface", "openai", "groq", "anthropic", "vllm"]

    if env["is_cloud"]:
        # Streamlit Cloud: API models only (no local Ollama)
        return ["huggingface", "openai", "groq", "anthropic"]
    elif env["is_desktop"]:
        # Desktop app: All providers (includes local Ollama)
        return all_providers
    else:
        # Local development: All providers for testing
        return all_providers


def should_show_ollama(env: Dict[str, bool]) -> bool:
    """
    Determine if Ollama settings should be shown.

    Args:
        env: Dictionary from detect_environment()

    Returns:
        True if running locally or as desktop app, False if on Streamlit Cloud
    """
    return not env["is_cloud"]


def should_show_download_button(env: Dict[str, bool]) -> bool:
    """
    Determine if desktop app download button should be shown.

    Args:
        env: Dictionary from detect_environment()

    Returns:
        True if running on Streamlit Cloud
    """
    return env["is_cloud"]


def get_ollama_placeholder() -> str:
    """
    Get placeholder text for Ollama base URL based on environment.

    Returns:
        Placeholder URL text
    """
    env = detect_environment()
    if env["is_cloud"]:
        return "https://your-ngrok-url.ngrok.io"
    else:
        return "http://localhost:11434"


if __name__ == "__main__":
    # Test the detection
    env = detect_environment()
    print(f"Environment Detection Results:")
    print(f"  Is Cloud: {env['is_cloud']}")
    print(f"  Is Desktop: {env['is_desktop']}")
    print(f"  Is Local: {env['is_local']}")
    print(f"  Is Web: {env['is_web']}")
    print(f"\nAvailable Providers: {get_available_providers(env)}")
    print(f"Show Ollama: {should_show_ollama(env)}")
    print(f"Show Download Button: {should_show_download_button(env)}")
