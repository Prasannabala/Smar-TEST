"""
Unified LLM Adapter supporting multiple providers.
Ollama (Local), HuggingFace (Local/API), OpenAI, Groq, Anthropic.
"""
import json
import requests
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Generator
from dataclasses import dataclass

from config.settings import get_settings, Settings
from config.llm_config import LLMProvider


class BaseLLMAdapter(ABC):
    """Abstract base class for LLM adapters."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate text with streaming."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM is available."""
        pass

    @abstractmethod
    def get_models(self) -> List[str]:
        """Get available models."""
        pass


class OllamaAdapter(BaseLLMAdapter):
    """Ollama local LLM adapter."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral:latest", timeout: int = 600):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout  # 10 minutes default for complex prompts

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Ollama."""
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 4096,  # Context window
                "temperature": 0.7,
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.ReadTimeout:
            raise ConnectionError(f"Ollama request timed out after {self.timeout}s. The model may be slow. Try a smaller/faster model or increase timeout.")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate text with streaming."""
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.7,
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload, stream=True, timeout=self.timeout)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done", False):
                        break
        except requests.exceptions.ReadTimeout:
            raise ConnectionError(f"Ollama request timed out after {self.timeout}s. Try a smaller/faster model.")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")

    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                # Check if our model exists (handle both "mistral:latest" and "mistral" formats)
                base_model = self.model.split(":")[0]
                return any(base_model in name for name in model_names)
            return False
        except:
            return False

    def get_models(self) -> List[str]:
        """Get available Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models]
            return []
        except:
            return []


class HuggingFaceAdapter(BaseLLMAdapter):
    """HuggingFace adapter supporting local transformers and Inference API.

    API mode uses the HuggingFace Inference Providers router (router.huggingface.co)
    which provides access to models via multiple providers (Featherless AI, Together,
    Fireworks, SambaNova, Cerebras, etc.) through an OpenAI-compatible endpoint.

    The router auto-selects the best available provider using ':fastest' suffix.
    """

    # Base URL for the HuggingFace router
    ROUTER_BASE = "https://router.huggingface.co"

    def __init__(self, model_id: str, use_api: bool = False, api_token: Optional[str] = None):
        self.model_id = model_id
        self.use_api = use_api
        self.api_token = api_token
        self._pipeline = None
        self._tokenizer = None

    def _get_pipeline(self):
        """Lazy load the transformers pipeline."""
        if self._pipeline is None and not self.use_api:
            try:
                from transformers import pipeline, AutoTokenizer
                import torch

                device = "cuda" if torch.cuda.is_available() else "cpu"
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                self._pipeline = pipeline(
                    "text-generation",
                    model=self.model_id,
                    tokenizer=self._tokenizer,
                    device=device,
                    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                )
            except ImportError:
                raise ImportError("transformers and torch are required for local HuggingFace models")
        return self._pipeline

    def _get_api_headers(self) -> Dict[str, str]:
        """Build authorization headers for the HuggingFace API."""
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def _get_routed_model_id(self) -> str:
        """Get model ID with routing suffix for auto provider selection.

        If the user already specified a provider (e.g. 'model:sambanova'),
        use as-is. Otherwise append ':fastest' for automatic routing.
        """
        if ':' in self.model_id:
            return self.model_id  # User already specified a provider/policy
        return f"{self.model_id}:fastest"

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using HuggingFace."""
        if self.use_api:
            return self._generate_api(prompt, system_prompt)
        else:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            return self._generate_local(full_prompt)

    def _generate_api(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using HuggingFace Inference Providers (router.huggingface.co).

        Uses the OpenAI-compatible chat completions endpoint with automatic
        provider routing (:fastest). Falls back to legacy text-generation
        format if chat completions fails.
        """
        if not self.api_token:
            raise ConnectionError(
                "HuggingFace API token is required. Get one at: "
                "https://huggingface.co/settings/tokens "
                "(select 'Make calls to Inference Providers' permission)"
            )

        headers = self._get_api_headers()
        routed_model = self._get_routed_model_id()
        last_error = None

        # --- Approach 1: OpenAI-compatible Chat Completions (recommended) ---
        try:
            chat_url = f"{self.ROUTER_BASE}/v1/chat/completions"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            chat_payload = {
                "model": routed_model,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.7,
            }

            response = requests.post(chat_url, headers=headers, json=chat_payload, timeout=180)

            # Parse error details before raising
            if response.status_code != 200:
                error_detail = ""
                try:
                    err_json = response.json()
                    error_detail = err_json.get("error", {})
                    if isinstance(error_detail, dict):
                        error_detail = error_detail.get("message", str(error_detail))
                except:
                    error_detail = response.text[:200]

                # Specific handling for 403 Forbidden
                if response.status_code == 403:
                    last_error = f"Access Denied (403): Check your API token has 'Inference Providers' permission at https://huggingface.co/settings/tokens"
                else:
                    last_error = f"Chat API ({response.status_code}): {error_detail}"
            else:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                    if content:
                        return content
                last_error = "Chat API returned empty response"

        except requests.exceptions.Timeout:
            last_error = "Chat API request timed out (180s). Try a smaller model."
        except requests.exceptions.ConnectionError as e:
            last_error = f"Cannot reach router.huggingface.co: {e}"
        except requests.exceptions.RequestException as e:
            last_error = f"Chat API error: {e}"

        # --- Approach 2: Legacy HF Inference text-generation format ---
        try:
            legacy_url = f"{self.ROUTER_BASE}/hf-inference/models/{self.model_id}"
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            legacy_payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 4096,
                    "temperature": 0.7,
                    "return_full_text": False,
                }
            }

            response = requests.post(legacy_url, headers=headers, json=legacy_payload, timeout=180)

            if response.status_code != 200:
                error_detail = ""
                try:
                    err_json = response.json()
                    error_detail = err_json.get("error", str(err_json))
                except:
                    error_detail = response.text[:200]

                # Specific handling for 403 Forbidden
                if response.status_code == 403:
                    raise ConnectionError(
                        f"Access Denied (403) - HuggingFace API\n\n"
                        f"Your API token doesn't have the required permissions.\n\n"
                        f"Fix this:\n"
                        f"  1. Go to: https://huggingface.co/settings/tokens\n"
                        f"  2. Click 'New token'\n"
                        f"  3. Enable 'Make calls to Inference Providers'\n"
                        f"  4. Copy the token and set it in your LLM Settings\n\n"
                        f"Error details: {error_detail}"
                    )

                # If both approaches failed, give a helpful combined error
                raise ConnectionError(
                    f"HuggingFace API failed for model '{self.model_id}'.\n"
                    f"  Chat Completions: {last_error}\n"
                    f"  Legacy API ({response.status_code}): {error_detail}\n\n"
                    f"Possible fixes:\n"
                    f"  1. Verify your API token has 'Inference Providers' permission\n"
                    f"  2. Check model is available at: https://huggingface.co/models?inference_provider=all\n"
                    f"  3. Try a known working model: meta-llama/Llama-3.1-8B-Instruct or Qwen/Qwen2.5-7B-Instruct"
                )

            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return ""

        except ConnectionError:
            raise  # Re-raise our custom error messages
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"HuggingFace API failed for model '{self.model_id}'.\n"
                f"  Chat Completions: {last_error}\n"
                f"  Legacy API: {e}\n\n"
                f"Possible fixes:\n"
                f"  1. Verify your API token has 'Inference Providers' permission\n"
                f"  2. Check model is available at: https://huggingface.co/models?inference_provider=all\n"
                f"  3. Try a known working model: meta-llama/Llama-3.1-8B-Instruct or Qwen/Qwen2.5-7B-Instruct"
            )

    def _generate_local(self, prompt: str) -> str:
        """Generate using local transformers."""
        pipe = self._get_pipeline()
        result = pipe(
            prompt,
            max_new_tokens=4096,
            temperature=0.7,
            do_sample=True,
            return_full_text=False,
        )
        if result and len(result) > 0:
            return result[0].get("generated_text", "")
        return ""

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate with streaming (falls back to non-streaming for HF)."""
        result = self.generate(prompt, system_prompt)
        chunk_size = 50
        for i in range(0, len(result), chunk_size):
            yield result[i:i + chunk_size]

    def is_available(self) -> bool:
        """Check if HuggingFace model is available."""
        if self.use_api:
            if not self.api_token:
                return False
            try:
                # Check model exists on HuggingFace Hub
                url = f"https://huggingface.co/api/models/{self.model_id}"
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    return False

                # Verify the token works with the router
                headers = self._get_api_headers()
                check_url = f"{self.ROUTER_BASE}/v1/models"
                response = requests.get(check_url, headers=headers, timeout=5)
                return response.status_code == 200
            except:
                return False
        else:
            try:
                from transformers import AutoConfig
                AutoConfig.from_pretrained(self.model_id)
                return True
            except:
                return False

    def get_models(self) -> List[str]:
        """Get suggested HuggingFace models available via Inference Providers."""
        return [
            "meta-llama/Llama-3.1-8B-Instruct",
            "meta-llama/Llama-3.3-70B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.2",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "HuggingFaceTB/SmolLM3-3B",
            "meta-llama/Llama-3.2-3B-Instruct",
        ]


class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI API adapter."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using OpenAI."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("openai package is required for OpenAI models")
        except Exception as e:
            raise ConnectionError(f"OpenAI API error: {e}")

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate with streaming."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except ImportError:
            raise ImportError("openai package is required for OpenAI models")

    def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        if not self.api_key:
            return False
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            client.models.list()
            return True
        except:
            return False

    def get_models(self) -> List[str]:
        """Get available OpenAI models."""
        return ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]


class GroqAdapter(BaseLLMAdapter):
    """Groq API adapter."""

    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Groq."""
        try:
            from groq import Groq
            client = Groq(api_key=self.api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("groq package is required for Groq models")
        except Exception as e:
            raise ConnectionError(f"Groq API error: {e}")

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate with streaming."""
        try:
            from groq import Groq
            client = Groq(api_key=self.api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except ImportError:
            raise ImportError("groq package is required for Groq models")

    def is_available(self) -> bool:
        """Check if Groq API is available."""
        if not self.api_key:
            return False
        try:
            from groq import Groq
            client = Groq(api_key=self.api_key)
            # Simple check
            return True
        except:
            return False

    def get_models(self) -> List[str]:
        """Get available Groq models."""
        return [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.2-90b-text-preview",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ]


class AnthropicAdapter(BaseLLMAdapter):
    """Anthropic API adapter."""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Anthropic."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)

            kwargs = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = client.messages.create(**kwargs)
            return response.content[0].text
        except ImportError:
            raise ImportError("anthropic package is required for Anthropic models")
        except Exception as e:
            raise ConnectionError(f"Anthropic API error: {e}")

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate with streaming."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)

            kwargs = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            with client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    yield text
        except ImportError:
            raise ImportError("anthropic package is required for Anthropic models")

    def is_available(self) -> bool:
        """Check if Anthropic API is available."""
        if not self.api_key:
            return False
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            return True
        except:
            return False

    def get_models(self) -> List[str]:
        """Get available Anthropic models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
        ]


class VLLMAdapter(BaseLLMAdapter):
    """vLLM local inference adapter.

    vLLM is a high-throughput and memory-efficient inference engine for LLMs.
    It provides significant speedups over standard transformers through:
    - PagedAttention for efficient KV cache management
    - Continuous batching for higher throughput
    - Optimized CUDA kernels
    - Tensor parallelism for multi-GPU support

    Supports both direct Python API and OpenAI-compatible server mode.
    """

    def __init__(
        self,
        model: str = "meta-llama/Llama-3.1-8B-Instruct",
        use_server: bool = False,
        server_url: str = "http://localhost:8000",
        tensor_parallel_size: int = 1,
        gpu_memory_utilization: float = 0.9,
        max_model_len: Optional[int] = None,
        dtype: str = "auto",
        quantization: Optional[str] = None,
        timeout: int = 600,
    ):
        """Initialize vLLM adapter.

        Args:
            model: HuggingFace model ID or local path
            use_server: If True, connect to vLLM OpenAI-compatible server. If False, use Python API.
            server_url: URL of vLLM server (when use_server=True)
            tensor_parallel_size: Number of GPUs for tensor parallelism
            gpu_memory_utilization: Fraction of GPU memory to use (0-1)
            max_model_len: Maximum sequence length (None = model default)
            dtype: Data type (auto, float16, bfloat16, float32)
            quantization: Quantization method (awq, gptq, squeezellm, None)
            timeout: Request timeout in seconds
        """
        self.model = model
        self.use_server = use_server
        self.server_url = server_url.rstrip('/')
        self.tensor_parallel_size = tensor_parallel_size
        self.gpu_memory_utilization = gpu_memory_utilization
        self.max_model_len = max_model_len
        self.dtype = dtype
        self.quantization = quantization
        self.timeout = timeout
        self._llm = None
        self._sampling_params = None

    def _get_llm(self):
        """Lazy load the vLLM engine."""
        if self._llm is None and not self.use_server:
            try:
                from vllm import LLM, SamplingParams

                kwargs = {
                    "model": self.model,
                    "tensor_parallel_size": self.tensor_parallel_size,
                    "gpu_memory_utilization": self.gpu_memory_utilization,
                    "dtype": self.dtype,
                    "trust_remote_code": True,
                }

                if self.max_model_len:
                    kwargs["max_model_len"] = self.max_model_len

                if self.quantization:
                    kwargs["quantization"] = self.quantization

                self._llm = LLM(**kwargs)
                self._sampling_params = SamplingParams(
                    temperature=0.7,
                    top_p=0.95,
                    max_tokens=4096,
                )
            except ImportError:
                raise ImportError(
                    "vLLM is required for vLLM adapter. Install with: pip install vllm\n"
                    "Note: vLLM requires CUDA and works best on Linux with NVIDIA GPUs."
                )
        return self._llm

    def _format_messages(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Format prompt with system message if provided."""
        if system_prompt:
            return f"{system_prompt}\n\n{prompt}"
        return prompt

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using vLLM."""
        if self.use_server:
            return self._generate_server(prompt, system_prompt)
        else:
            return self._generate_local(prompt, system_prompt)

    def _generate_local(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using local vLLM Python API."""
        llm = self._get_llm()
        full_prompt = self._format_messages(prompt, system_prompt)

        outputs = llm.generate([full_prompt], self._sampling_params)

        if outputs and len(outputs) > 0:
            return outputs[0].outputs[0].text
        return ""

    def _generate_server(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using vLLM OpenAI-compatible server."""
        url = f"{self.server_url}/v1/completions"

        full_prompt = self._format_messages(prompt, system_prompt)

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.95,
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0].get("text", "")
            return ""
        except requests.exceptions.Timeout:
            raise ConnectionError(f"vLLM server request timed out after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to vLLM server at {self.server_url}: {e}")

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate text with streaming.

        Note: Streaming is only supported in server mode.
        In Python API mode, falls back to non-streaming generation.
        """
        if self.use_server:
            return self._generate_stream_server(prompt, system_prompt)
        else:
            # Python API doesn't support streaming in the same way
            # Fall back to chunked non-streaming response
            result = self.generate(prompt, system_prompt)
            chunk_size = 50
            for i in range(0, len(result), chunk_size):
                yield result[i:i + chunk_size]

    def _generate_stream_server(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate with streaming using vLLM server."""
        url = f"{self.server_url}/v1/completions"

        full_prompt = self._format_messages(prompt, system_prompt)

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.95,
            "stream": True,
        }

        try:
            response = requests.post(url, json=payload, stream=True, timeout=self.timeout)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data: "):
                        line = line[6:]  # Remove "data: " prefix
                        if line.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(line)
                            if "choices" in data and len(data["choices"]) > 0:
                                text = data["choices"][0].get("text", "")
                                if text:
                                    yield text
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.Timeout:
            raise ConnectionError(f"vLLM server request timed out after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to vLLM server: {e}")

    def is_available(self) -> bool:
        """Check if vLLM is available."""
        if self.use_server:
            try:
                response = requests.get(f"{self.server_url}/v1/models", timeout=5)
                return response.status_code == 200
            except:
                return False
        else:
            try:
                import vllm
                import torch
                return torch.cuda.is_available()
            except ImportError:
                return False

    def get_models(self) -> List[str]:
        """Get suggested vLLM-compatible models."""
        if self.use_server:
            try:
                response = requests.get(f"{self.server_url}/v1/models", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data:
                        return [m.get("id", "") for m in data["data"]]
            except:
                pass

        # Return popular vLLM-compatible models
        return [
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
        ]


class LLMAdapter:
    """
    Unified LLM adapter that wraps all providers.
    Factory pattern for creating the appropriate adapter.
    """

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._adapter: Optional[BaseLLMAdapter] = None
        self._initialize_adapter()

    def _initialize_adapter(self) -> None:
        """Initialize the appropriate adapter based on settings."""
        provider = self.settings.llm_provider

        if provider == LLMProvider.OLLAMA.value:
            self._adapter = OllamaAdapter(
                base_url=self.settings.ollama_base_url,
                model=self.settings.ollama_model,
                timeout=getattr(self.settings, 'ollama_timeout', 600)
            )
        elif provider == LLMProvider.HUGGINGFACE.value:
            self._adapter = HuggingFaceAdapter(
                model_id=self.settings.hf_model_id,
                use_api=self.settings.hf_use_api,
                api_token=self.settings.hf_api_token
            )
        elif provider == LLMProvider.OPENAI.value:
            self._adapter = OpenAIAdapter(
                api_key=self.settings.openai_api_key,
                model=self.settings.openai_model
            )
        elif provider == LLMProvider.GROQ.value:
            self._adapter = GroqAdapter(
                api_key=self.settings.groq_api_key,
                model=self.settings.groq_model
            )
        elif provider == LLMProvider.ANTHROPIC.value:
            self._adapter = AnthropicAdapter(
                api_key=self.settings.anthropic_api_key,
                model=self.settings.anthropic_model
            )
        elif provider == LLMProvider.VLLM.value:
            self._adapter = VLLMAdapter(
                model=getattr(self.settings, 'vllm_model', 'meta-llama/Llama-3.1-8B-Instruct'),
                use_server=getattr(self.settings, 'vllm_use_server', False),
                server_url=getattr(self.settings, 'vllm_server_url', 'http://localhost:8000'),
                tensor_parallel_size=getattr(self.settings, 'vllm_tensor_parallel_size', 1),
                gpu_memory_utilization=getattr(self.settings, 'vllm_gpu_memory_utilization', 0.9),
                max_model_len=getattr(self.settings, 'vllm_max_model_len', None),
                dtype=getattr(self.settings, 'vllm_dtype', 'auto'),
                quantization=getattr(self.settings, 'vllm_quantization', None),
                timeout=getattr(self.settings, 'vllm_timeout', 600)
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using the configured provider."""
        return self._adapter.generate(prompt, system_prompt)

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Generate text with streaming."""
        return self._adapter.generate_stream(prompt, system_prompt)

    def is_available(self) -> bool:
        """Check if the configured LLM is available."""
        return self._adapter.is_available()

    def get_models(self) -> List[str]:
        """Get available models for the current provider."""
        return self._adapter.get_models()

    def get_provider_name(self) -> str:
        """Get the current provider name."""
        return self.settings.llm_provider

    def refresh(self) -> None:
        """Refresh the adapter with current settings."""
        self.settings = get_settings()
        self._initialize_adapter()


# Factory function
def get_llm_adapter(settings: Optional[Settings] = None) -> LLMAdapter:
    """Get an LLM adapter instance."""
    return LLMAdapter(settings)


def get_code_llm_adapter(settings: Optional[Settings] = None) -> LLMAdapter:
    """
    Get an LLM adapter optimized for code generation (Selenium/Playwright).
    Uses CodeLlama if available and configured, otherwise falls back to main model.
    """
    settings = settings or get_settings()

    # Only use code model for Ollama provider with the setting enabled
    if (settings.llm_provider == LLMProvider.OLLAMA.value and
        getattr(settings, 'use_code_model_for_scripts', True)):

        code_model = getattr(settings, 'ollama_code_model', 'codellama:7b')

        # Check if code model is available
        try:
            adapter = OllamaAdapter(
                base_url=settings.ollama_base_url,
                model=code_model,
                timeout=getattr(settings, 'ollama_timeout', 600)
            )
            if adapter.is_available():
                # Return a wrapper that uses the code model
                class CodeLLMAdapter(LLMAdapter):
                    def __init__(self, settings, code_adapter):
                        self.settings = settings
                        self._adapter = code_adapter

                return CodeLLMAdapter(settings, adapter)
        except Exception:
            pass  # Fall back to main adapter

    # Fall back to regular adapter
    return LLMAdapter(settings)
