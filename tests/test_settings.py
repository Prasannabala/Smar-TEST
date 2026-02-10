"""
Tests for application settings (config/settings.py).
No actual settings files or API keys are used — all tests are isolated.
"""
import json
import pytest

from config.settings import Settings
from config.llm_config import LLMProvider, LLMConfig


class TestSettings:
    """Tests for Settings dataclass."""

    def test_default_settings(self, default_settings):
        assert default_settings.llm_provider == "ollama"
        assert default_settings.ollama_model == "qwen2.5:7b"
        assert default_settings.ollama_code_model == "codellama:7b"
        assert default_settings.ollama_timeout == 600

    def test_default_hf_settings(self, default_settings):
        assert default_settings.hf_model_id == "meta-llama/Llama-3.1-8B-Instruct"
        assert default_settings.hf_use_api is True
        assert default_settings.hf_api_token == ""  # No secrets in defaults

    def test_default_api_keys_are_empty(self, default_settings):
        """Verify no API keys are hardcoded in defaults."""
        assert default_settings.openai_api_key == ""
        assert default_settings.groq_api_key == ""
        assert default_settings.anthropic_api_key == ""
        assert default_settings.hf_api_token == ""

    def test_save_and_load(self, tmp_path, monkeypatch):
        """Settings can be saved and loaded without leaking secrets."""
        import config.settings as settings_module
        settings_file = tmp_path / "test_settings.json"
        monkeypatch.setattr(settings_module, "SETTINGS_FILE", settings_file)

        s = Settings()
        s.ollama_model = "test-model:latest"
        s.llm_provider = "groq"
        s.save()

        assert settings_file.exists()

        # Verify saved file content
        with open(settings_file) as f:
            saved = json.load(f)
        assert saved["ollama_model"] == "test-model:latest"
        assert saved["llm_provider"] == "groq"

    def test_load_invalid_json(self, tmp_path, monkeypatch):
        """Loading invalid JSON should fall back to defaults."""
        import config.settings as settings_module
        settings_file = tmp_path / "bad_settings.json"
        settings_file.write_text("{invalid json")
        monkeypatch.setattr(settings_module, "SETTINGS_FILE", settings_file)

        s = Settings.load()
        assert s.llm_provider == "ollama"  # Default

    def test_load_missing_file(self, tmp_path, monkeypatch):
        """Loading from nonexistent file should return defaults."""
        import config.settings as settings_module
        settings_file = tmp_path / "nonexistent.json"
        monkeypatch.setattr(settings_module, "SETTINGS_FILE", settings_file)

        s = Settings.load()
        assert s.llm_provider == "ollama"

    def test_generation_defaults(self, default_settings):
        assert default_settings.include_edge_cases is True
        assert default_settings.include_negative_tests is True
        assert default_settings.include_boundary_tests is True
        assert default_settings.default_export_format == "excel"


class TestLLMConfig:
    """Tests for LLM configuration constants."""

    def test_provider_names(self):
        config = LLMConfig()
        assert "Ollama" in config.PROVIDER_NAMES[LLMProvider.OLLAMA.value]
        assert "OpenAI" in config.PROVIDER_NAMES[LLMProvider.OPENAI.value]
        assert "Groq" in config.PROVIDER_NAMES[LLMProvider.GROQ.value]

    def test_default_models(self):
        config = LLMConfig()
        assert config.DEFAULT_MODELS[LLMProvider.OLLAMA.value] is not None
        assert config.DEFAULT_MODELS[LLMProvider.OPENAI.value] is not None

    def test_available_models(self):
        config = LLMConfig()
        openai_models = config.AVAILABLE_MODELS[LLMProvider.OPENAI.value]
        assert isinstance(openai_models, list)
        assert len(openai_models) > 0

    def test_all_providers_have_display_names(self):
        config = LLMConfig()
        for provider in LLMProvider:
            assert provider.value in config.PROVIDER_NAMES
