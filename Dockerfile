# 使用 Python 3.9 作為基礎映像
FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements 檔案
COPY requirements.txt .

# 安裝基礎依賴
RUN pip install --no-cache-dir flask==2.3.3 gunicorn==21.2.0 requests>=2.31.0

# 使用預構建的 CPU 版 llama-cpp-python 包
RUN pip install --no-cache-dir llama-cpp-python==0.2.38 --extra-index-url https://wheels.rasa.com/llama-cpp-python/cpu/

# 複製應用程式代碼
COPY app.py .

# 創建模型目錄
RUN mkdir -p models

# 設置環境變數
ENV PYTHONUNBUFFERED=1
ENV GGUF_FILE=models/LLaMAX3-8B-Alpaca.Q8_0.gguf
ENV N_GPU_LAYERS=0
ENV N_THREADS=8
ENV PORT=5000

# 暴露端口
EXPOSE ${PORT}

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 運行應用程式
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "app:app", "--timeout", "120"]