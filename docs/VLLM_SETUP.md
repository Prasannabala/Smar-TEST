# vLLM Setup Guide

## What is vLLM?

vLLM is a high-performance, memory-efficient inference engine for Large Language Models (LLMs). It provides significant speedups over standard transformer libraries through advanced optimizations:

- **PagedAttention**: Efficient KV cache management reducing memory waste
- **Continuous Batching**: Higher throughput by processing requests as they arrive
- **Optimized CUDA Kernels**: Fast GPU computation
- **Tensor Parallelism**: Multi-GPU support for large models
- **Quantization Support**: AWQ, GPTQ for smaller memory footprint

### Performance Benefits

Compared to standard HuggingFace Transformers or Ollama:
- **2-4x faster** inference on the same hardware
- **10-30x higher throughput** with batching
- **Better GPU memory utilization** (up to 24x more efficient)
- **Lower latency** for interactive applications

---

## Requirements

### Hardware Requirements

- **NVIDIA GPU** with CUDA support (required)
- **Compute Capability**: 7.0 or higher (V100, T4, A10, A100, RTX 20/30/40 series)
- **GPU Memory**: Minimum 8GB VRAM (for 7B models), 16GB+ recommended
- **System RAM**: 16GB+ recommended
- **Storage**: 10-50GB for model weights

### Software Requirements

- **Operating System**: Linux (Ubuntu 20.04+, CentOS 7+)
  - Windows: WSL2 with GPU support or Docker
  - macOS: Not supported (no CUDA)
- **CUDA**: 11.8 or 12.1+
- **Python**: 3.9-3.11
- **Docker** (optional): For containerized deployment

---

## Installation

### Option 1: pip Install (Native Linux)

```bash
# Install vLLM
pip install vllm

# Verify installation
python -c "import vllm; print(vllm.__version__)"
```

### Option 2: Docker (Recommended)

Use the provided docker-compose configuration:

```bash
# Start vLLM server with default model (Llama-3.1-8B)
docker-compose --profile vllm up -d

# Check logs
docker logs vllm-server

# Custom model
VLLM_MODEL="Qwen/Qwen2.5-7B-Instruct" docker-compose --profile vllm up -d
```

### Option 3: Manual Docker

```bash
# Pull vLLM image
docker pull vllm/vllm-openai:latest

# Run vLLM server
docker run --runtime nvidia --gpus all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8000:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --trust-remote-code
```

---

## Configuration

### Mode 1: Python API (Direct)

Best for single-process applications with dedicated GPU.

**Settings in UI or `data/settings.json`:**

```json
{
  "llm_provider": "vllm",
  "vllm_model": "meta-llama/Llama-3.1-8B-Instruct",
  "vllm_use_server": false,
  "vllm_tensor_parallel_size": 1,
  "vllm_gpu_memory_utilization": 0.9,
  "vllm_dtype": "auto",
  "vllm_max_model_len": null,
  "vllm_quantization": null
}
```

**Parameters:**

- `vllm_model`: HuggingFace model ID or local path
- `vllm_tensor_parallel_size`: Number of GPUs (1 for single GPU, 2/4/8 for multi-GPU)
- `vllm_gpu_memory_utilization`: GPU memory fraction (0.7-0.95, higher = more capacity)
- `vllm_dtype`: Data type
  - `auto`: Automatic (usually float16)
  - `float16`: Standard precision (most common)
  - `bfloat16`: Better for training, less tested
  - `float32`: Slow, for debugging
- `vllm_max_model_len`: Override max sequence length (e.g., 8192, 16384)
- `vllm_quantization`: Quantization method
  - `null`: No quantization (default)
  - `awq`: 4-bit quantization (requires AWQ model)
  - `gptq`: 4-bit quantization (requires GPTQ model)
  - `squeezellm`: Quantization method

### Mode 2: OpenAI-Compatible Server (Recommended)

Best for multi-user scenarios or when sharing GPU across applications.

**1. Start vLLM Server:**

```bash
# Using Docker Compose
docker-compose --profile vllm up -d

# OR using vLLM CLI
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096 \
  --trust-remote-code
```

**2. Configure Application:**

```json
{
  "llm_provider": "vllm",
  "vllm_model": "meta-llama/Llama-3.1-8B-Instruct",
  "vllm_use_server": true,
  "vllm_server_url": "http://localhost:8000"
}
```

**3. Test Server:**

```bash
curl http://localhost:8000/v1/models
```

---

## Recommended Models

### For Test Case Generation (Main Model)

| Model | Size | VRAM | Speed | Quality |
|-------|------|------|-------|---------|
| **Qwen/Qwen2.5-7B-Instruct** | 7B | 8GB | Fast | Excellent |
| meta-llama/Llama-3.1-8B-Instruct | 8B | 10GB | Fast | Excellent |
| meta-llama/Llama-3.3-70B-Instruct | 70B | 40GB (2xA100) | Moderate | Best |
| Qwen/Qwen2.5-14B-Instruct | 14B | 16GB | Moderate | Excellent |
| mistralai/Mistral-7B-Instruct-v0.3 | 7B | 8GB | Fast | Good |

### For Code Generation (Selenium/Playwright)

| Model | Size | VRAM | Specialization |
|-------|------|------|----------------|
| **Qwen/Qwen2.5-Coder-7B-Instruct** | 7B | 8GB | Code generation |
| meta-llama/CodeLlama-7b-Instruct-hf | 7B | 8GB | Code generation |
| deepseek-ai/DeepSeek-Coder-6.7B-Instruct | 7B | 8GB | Code generation |

### Quantized Models (Lower VRAM)

If you have limited GPU memory, use quantized models:

```bash
# AWQ quantized (4-bit, ~50% VRAM reduction)
TheBloke/Llama-3.1-8B-Instruct-AWQ
TheBloke/Qwen2.5-7B-Instruct-AWQ

# GPTQ quantized (4-bit)
TheBloke/Llama-3.1-8B-Instruct-GPTQ
```

**Configuration:**

```json
{
  "vllm_model": "TheBloke/Llama-3.1-8B-Instruct-AWQ",
  "vllm_quantization": "awq",
  "vllm_gpu_memory_utilization": 0.8
}
```

---

## Performance Tuning

### GPU Memory Optimization

```json
{
  "vllm_gpu_memory_utilization": 0.95,  // Use more GPU memory
  "vllm_max_model_len": 4096            // Reduce context window
}
```

- Higher `gpu_memory_utilization` = more requests in parallel
- Lower `max_model_len` = less memory per request

### Multi-GPU Setup

For models larger than single GPU capacity (e.g., 70B models):

```json
{
  "vllm_model": "meta-llama/Llama-3.3-70B-Instruct",
  "vllm_tensor_parallel_size": 2,  // Split across 2 GPUs
  "vllm_gpu_memory_utilization": 0.9
}
```

**Docker with multiple GPUs:**

```bash
docker run --runtime nvidia --gpus all \
  -e VLLM_TENSOR_PARALLEL=2 \
  -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3.3-70B-Instruct \
  --tensor-parallel-size 2
```

### Throughput Optimization

For high-volume workloads:

```bash
vllm serve model_name \
  --max-num-seqs 256 \              # More parallel requests
  --max-num-batched-tokens 8192 \   # Larger batches
  --gpu-memory-utilization 0.95
```

---

## Usage in Application

### Using the UI

1. Open Streamlit app: `http://localhost:8501`
2. Go to **LLM Settings** (sidebar)
3. Select **LLM Provider**: `vLLM (High-Performance Local)`
4. Choose mode:
   - **Python API**: Set `Use Server Mode` to `False`
   - **Server Mode**: Set `Use Server Mode` to `True`, enter server URL
5. Configure model and parameters
6. Click **Save Settings**
7. Generate tests as usual

### Programmatic Usage

```python
from config.settings import Settings, save_settings
from core.llm_adapter import get_llm_adapter

# Configure vLLM
settings = Settings()
settings.llm_provider = "vllm"
settings.vllm_model = "meta-llama/Llama-3.1-8B-Instruct"
settings.vllm_use_server = True
settings.vllm_server_url = "http://localhost:8000"
save_settings(settings)

# Use adapter
llm = get_llm_adapter(settings)
response = llm.generate(
    "Generate test cases for login functionality",
    system_prompt="You are a QA engineer."
)
print(response)
```

---

## Troubleshooting

### Issue: "CUDA out of memory"

**Solution 1**: Reduce GPU memory utilization

```json
{
  "vllm_gpu_memory_utilization": 0.7,
  "vllm_max_model_len": 2048
}
```

**Solution 2**: Use quantized model

```json
{
  "vllm_model": "TheBloke/Llama-3.1-8B-Instruct-AWQ",
  "vllm_quantization": "awq"
}
```

**Solution 3**: Use smaller model

```json
{
  "vllm_model": "Qwen/Qwen2.5-7B-Instruct"
}
```

### Issue: "vLLM not available" or ImportError

**Linux/Docker:**

```bash
pip install vllm
# OR
docker pull vllm/vllm-openai:latest
```

**Windows:**

vLLM doesn't support Windows natively. Use:
- WSL2 with GPU passthrough
- Docker Desktop with WSL2 backend
- Cloud GPU (AWS, GCP, RunPod)

### Issue: Server timeout or slow responses

**Increase timeout:**

```json
{
  "vllm_timeout": 1200  // 20 minutes
}
```

**Check server logs:**

```bash
docker logs vllm-server
```

### Issue: Model download fails

**Pre-download model:**

```python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    cache_dir="/root/.cache/huggingface"
)
```

**Or use docker volume:**

```bash
docker run -v ~/.cache/huggingface:/root/.cache/huggingface ...
```

---

## Environment Variables

For docker-compose:

```bash
# .env file
VLLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
VLLM_GPU_MEMORY=0.9
VLLM_TENSOR_PARALLEL=1
VLLM_DTYPE=auto
VLLM_MAX_MODEL_LEN=4096
```

---

## Comparison: vLLM vs Ollama vs HuggingFace

| Feature | vLLM | Ollama | HF Transformers |
|---------|------|--------|-----------------|
| **Speed** | Fastest | Fast | Slow |
| **Throughput** | Highest | Medium | Low |
| **Memory Efficiency** | Best | Good | Poor |
| **GPU Required** | Yes (CUDA) | No | Optional |
| **Multi-GPU** | Yes | No | Limited |
| **Ease of Setup** | Medium | Easy | Easy |
| **Platform** | Linux | All | All |
| **Production Ready** | Yes | Yes | No |

**Use vLLM when:**
- You have NVIDIA GPU(s)
- You need maximum performance
- Running on Linux or Docker
- Serving multiple users

**Use Ollama when:**
- You want simple setup
- Running on CPU or various platforms
- Single-user desktop usage
- Don't need maximum speed

**Use HF Transformers when:**
- Research/experimentation
- No production requirements
- Need specific model features

---

## Cloud Deployment

### RunPod (GPU Cloud)

```bash
# SSH into RunPod instance
ssh root@runpod-instance

# Install vLLM
pip install vllm

# Start server
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --gpu-memory-utilization 0.9
```

Configure app to point to RunPod URL.

### AWS EC2 (g4dn/p3 instances)

Use the docker-compose setup or install vLLM natively.

### GCP Compute Engine

Similar to AWS, use GPU instances (T4, A100).

---

## Best Practices

1. **Start with server mode** for flexibility
2. **Monitor GPU usage** with `nvidia-smi -l 1`
3. **Use quantized models** if memory-constrained
4. **Set appropriate max_model_len** (4096 is usually enough for test cases)
5. **Pre-download models** to avoid timeout during first run
6. **Use tensor parallelism** for 70B+ models
7. **Test with small model first** (e.g., Qwen2.5-7B) before scaling up

---

## Additional Resources

- [vLLM Documentation](https://docs.vllm.ai/)
- [vLLM GitHub](https://github.com/vllm-project/vllm)
- [Model Compatibility](https://docs.vllm.ai/en/latest/models/supported_models.html)
- [Performance Benchmarks](https://blog.vllm.ai/2023/06/20/vllm.html)

---

## Support

For issues related to vLLM integration in this project:
1. Check this documentation
2. Review application logs
3. Verify GPU/CUDA setup with `nvidia-smi`
4. Test vLLM independently first
5. Open issue on project GitHub

For vLLM-specific issues:
- [vLLM GitHub Issues](https://github.com/vllm-project/vllm/issues)
- [vLLM Discord](https://discord.gg/vllm)
