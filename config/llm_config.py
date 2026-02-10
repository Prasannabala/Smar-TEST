"""
LLM Provider configurations and constants.
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any


class LLMProvider(Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    GROQ = "groq"
    ANTHROPIC = "anthropic"
    VLLM = "vllm"


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""

    # Provider display names
    PROVIDER_NAMES: Dict[str, str] = None

    # Default models per provider
    DEFAULT_MODELS: Dict[str, str] = None

    # Available models for online providers
    AVAILABLE_MODELS: Dict[str, List[str]] = None

    def __post_init__(self):
        self.PROVIDER_NAMES = {
            LLMProvider.OLLAMA.value: "Ollama (Local)",
            LLMProvider.HUGGINGFACE.value: "Hugging Face",
            LLMProvider.OPENAI.value: "OpenAI",
            LLMProvider.GROQ.value: "Groq",
            LLMProvider.ANTHROPIC.value: "Anthropic",
            LLMProvider.VLLM.value: "vLLM (High-Performance Local)",
        }

        self.DEFAULT_MODELS = {
            LLMProvider.OLLAMA.value: "mistral:latest",
            LLMProvider.HUGGINGFACE.value: "mistralai/Mistral-7B-Instruct-v0.2",
            LLMProvider.OPENAI.value: "gpt-4",
            LLMProvider.GROQ.value: "llama-3.1-70b-versatile",
            LLMProvider.ANTHROPIC.value: "claude-3-sonnet-20240229",
            LLMProvider.VLLM.value: "meta-llama/Llama-3.1-8B-Instruct",
        }

        self.AVAILABLE_MODELS = {
            LLMProvider.OPENAI.value: [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-3.5-turbo",
            ],
            LLMProvider.GROQ.value: [
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "llama-3.2-90b-text-preview",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
            ],
            LLMProvider.ANTHROPIC.value: [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
                "claude-3-5-sonnet-20241022",
            ],
            LLMProvider.HUGGINGFACE.value: [
                "mistralai/Mistral-7B-Instruct-v0.2",
                "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "meta-llama/Llama-2-7b-chat-hf",
                "meta-llama/Llama-2-13b-chat-hf",
                "HuggingFaceH4/zephyr-7b-beta",
                "microsoft/phi-2",
            ],
            LLMProvider.VLLM.value: [
                "meta-llama/Llama-3.1-8B-Instruct",
                "meta-llama/Llama-3.1-70B-Instruct",
                "meta-llama/Llama-3.3-70B-Instruct",
                "Qwen/Qwen2.5-7B-Instruct",
                "Qwen/Qwen2.5-14B-Instruct",
                "Qwen/Qwen2.5-32B-Instruct",
                "Qwen/Qwen2.5-Coder-7B-Instruct",
                "mistralai/Mistral-7B-Instruct-v0.3",
                "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            ],
        }


# Singleton instance
llm_config = LLMConfig()
