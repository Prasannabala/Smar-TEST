# ============================================
# Test Case Generation Agent - Dockerfile
# ============================================
# Multi-stage build for a lightweight production image
#
# Usage:
#   docker build -t testcase-agent .
#   docker run -p 8501:8501 testcase-agent
#
# With Ollama (use docker-compose instead):
#   docker-compose up
# ============================================

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# --- Dependencies Stage ---
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Application Stage ---
FROM dependencies AS app

# Copy application code
COPY config/ ./config/
COPY core/ ./core/
COPY models/ ./models/
COPY storage/ ./storage/
COPY templates/ ./templates/
COPY ui/ ./ui/
COPY app.py .

# Create data directories (will be overridden by volume mounts)
RUN mkdir -p data/clients data/exports

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')" || exit 1

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false"]
