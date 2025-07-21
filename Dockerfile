# Use Python 3.9 slim as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      cmake \
      libopenblas-dev \
      python3-dev \
      gcc \
      g++ \
      clang \
      curl && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir flask==2.3.3 gunicorn==21.2.0 requests>=2.31.0

# Set CMake args for BLAS and install llama-cpp-python from official CPU wheel index
ENV CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS"
RUN pip install --no-cache-dir llama-cpp-python==0.2.38 \
      --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# Copy application code
COPY app.py .

# Prepare model directory
RUN mkdir -p models

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    GGUF_FILE=models/LLaMAX3-8B-Alpaca.Q8_0.gguf \
    N_GPU_LAYERS=0 \
    N_THREADS=8 \
    PORT=5000

# Expose port and add healthcheck
EXPOSE ${PORT}
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "app:app", "--timeout", "120"]
