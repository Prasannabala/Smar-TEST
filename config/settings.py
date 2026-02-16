"""
Application settings and configuration management.
"""
import os
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CLIENTS_DIR = DATA_DIR / "clients"
EXPORTS_DIR = DATA_DIR / "exports"
DB_PATH = DATA_DIR / "app.db"
SETTINGS_FILE = DATA_DIR / "settings.json"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CLIENTS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)


@dataclass
class Settings:
    """Application settings with persistence."""

    # LLM Settings
    llm_provider: str = "ollama"  # ollama, huggingface, openai, groq, anthropic

    # Ollama settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"  # Main model for test case generation
    ollama_code_model: str = "codellama:7b"  # Model for Selenium/Playwright code generation
    ollama_timeout: int = 600  # 10 minutes default (local models can be slow)
    use_code_model_for_scripts: bool = True  # Auto-switch to code model for automation scripts

    # HuggingFace settings
    hf_model_id: str = "meta-llama/Llama-3.1-8B-Instruct"
    hf_use_api: bool = True  # Default to API mode (cloud) since it's more accessible
    hf_api_token: str = ""

    # Online API settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-70b-versatile"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-sonnet-20240229"

    # vLLM settings (high-performance local inference)
    vllm_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    vllm_use_server: bool = False  # Use OpenAI-compatible server mode (True) or Python API (False)
    vllm_server_url: str = "http://localhost:8000"  # URL when using server mode
    vllm_tensor_parallel_size: int = 1  # Number of GPUs for tensor parallelism
    vllm_gpu_memory_utilization: float = 0.9  # Fraction of GPU memory to use (0-1)
    vllm_max_model_len: int = None  # Maximum sequence length (None = model default)
    vllm_dtype: str = "auto"  # Data type: auto, float16, bfloat16, float32
    vllm_quantization: str = None  # Quantization: awq, gptq, squeezellm, or None
    vllm_timeout: int = 600  # Request timeout in seconds

    # Generation settings
    include_edge_cases: bool = True
    include_negative_tests: bool = True
    include_boundary_tests: bool = True

    # Export settings
    default_export_format: str = "excel"  # excel, csv, markdown

    def save(self) -> None:
        """Save settings to JSON file via SettingsManager."""
        try:
            from config.settings_manager import SettingsManager
            manager = SettingsManager()
            # Don't save API keys
            settings_dict = asdict(self)
            settings_dict_safe = {k: v for k, v in settings_dict.items()
                                 if not k.endswith('_key') and not k.endswith('_token')}
            manager.save_settings(settings_dict_safe)
        except ImportError:
            # Fallback to old location
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls) -> 'Settings':
        """Load settings from SettingsManager or JSON file or create default."""
        # Try to load from SettingsManager first
        try:
            from config.settings_manager import SettingsManager
            manager = SettingsManager()
            saved_settings = manager.load_settings()
            if saved_settings:
                try:
                    settings = cls(**saved_settings)
                    # Load sensitive keys from environment
                    settings.openai_api_key = os.getenv('OPENAI_API_KEY', '')
                    settings.groq_api_key = os.getenv('GROQ_API_KEY', '')
                    settings.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
                    settings.hf_api_token = os.getenv('HF_API_TOKEN', '')
                    return settings
                except TypeError:
                    pass
        except ImportError:
            pass

        # Fallback to old location
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                settings = cls(**data)
                # Load sensitive keys from environment
                settings.openai_api_key = os.getenv('OPENAI_API_KEY', '')
                settings.groq_api_key = os.getenv('GROQ_API_KEY', '')
                settings.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
                settings.hf_api_token = os.getenv('HF_API_TOKEN', '')
                return settings
            except (json.JSONDecodeError, TypeError):
                pass

        # Return defaults with environment variables
        settings = cls()
        settings.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        settings.groq_api_key = os.getenv('GROQ_API_KEY', '')
        settings.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        settings.hf_api_token = os.getenv('HF_API_TOKEN', '')
        return settings


# Singleton settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings


def save_settings(settings: Settings) -> None:
    """Save and update global settings."""
    global _settings
    settings.save()
    _settings = settings
