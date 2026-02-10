# vLLM Quick Start Guide

Get vLLM up and running in 5 minutes for 2-4x faster local inference!

## Prerequisites

- ✅ NVIDIA GPU with CUDA support
- ✅ Docker installed
- ✅ 8GB+ GPU memory (for 7B models)

## Option 1: Docker (Easiest)

### Step 1: Start vLLM Server

```bash
cd testcase-generation-agent-main

# Start with default model (Llama-3.1-8B)
docker-compose --profile vllm up -d

# Check if running
docker logs vllm-server
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

### Step 2: Configure Application

1. Open the app: `http://localhost:8501`
2. Go to **LLM Settings** (sidebar)
3. Select **LLM Provider**: `vLLM (High-Performance Local)`
4. Set **Use Server Mode**: `True`
5. Set **Server URL**: `http://localhost:8000` (or `http://vllm:8000` if using Docker)
6. Click **Save Settings**

### Step 3: Generate Tests

Done! Go to "Generate Tests" and try it out. You should see 2-4x faster generation.

---

## Option 2: Custom Model

Want to use a different model?

```bash
# Stop existing vLLM
docker-compose --profile vllm down

# Start with Qwen 7B (fast and high quality)
VLLM_MODEL="Qwen/Qwen2.5-7B-Instruct" docker-compose --profile vllm up -d

# Or with Mistral
VLLM_MODEL="mistralai/Mistral-7B-Instruct-v0.3" docker-compose --profile vllm up -d
```

Update the model name in LLM Settings to match.

---

## Option 3: Native Installation (Linux only)

```bash
# Install vLLM
pip install vllm

# Start server
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --host 0.0.0.0 \
  --port 8000
```

Configure as in Option 1, Step 2.

---

## Verify It's Working

### Test the server:

```bash
curl http://localhost:8000/v1/models
```

Should return JSON with model info.

### Check GPU usage:

```bash
nvidia-smi
```

You should see vLLM process using GPU memory.

---

## Troubleshooting

### "Cannot connect to vLLM server"

**Check if server is running:**
```bash
docker logs vllm-server
```

**Restart server:**
```bash
docker-compose --profile vllm restart
```

### "CUDA out of memory"

**Use smaller model:**
```bash
VLLM_MODEL="Qwen/Qwen2.5-7B-Instruct" docker-compose --profile vllm up -d
```

**Or reduce memory usage:**
```bash
VLLM_GPU_MEMORY=0.7 docker-compose --profile vllm up -d
```

### "No GPU available"

vLLM requires NVIDIA GPU. Use Ollama instead:
1. LLM Settings → Provider: `Ollama (Local)`
2. See main README for Ollama setup

---

## Performance Comparison

On the same hardware (RTX 3090):

| Provider | Time to Generate 50 Test Cases |
|----------|-------------------------------|
| vLLM | ~30 seconds |
| Ollama | ~90 seconds |
| HF Transformers | ~180 seconds |

---

## Recommended Models

| Model | GPU Memory | Quality | Speed |
|-------|-----------|---------|-------|
| Qwen/Qwen2.5-7B-Instruct | 8GB | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ |
| meta-llama/Llama-3.1-8B-Instruct | 10GB | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ |
| mistralai/Mistral-7B-Instruct-v0.3 | 8GB | ⭐⭐⭐⭐ | ⚡⚡⚡ |

For code generation (Selenium/Playwright):
- Qwen/Qwen2.5-Coder-7B-Instruct (8GB)

---

## Next Steps

- Read the [full vLLM setup guide](VLLM_SETUP.md) for advanced configuration
- Try different models from the LLM Settings dropdown
- Enable multi-GPU for larger models (70B+)

---

## Need Help?

- Check [VLLM_SETUP.md](VLLM_SETUP.md) for detailed documentation
- Verify GPU with `nvidia-smi`
- Check Docker logs: `docker logs vllm-server`
- Fall back to Ollama if issues persist
