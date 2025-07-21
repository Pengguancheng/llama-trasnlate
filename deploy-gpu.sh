#!/bin/bash

# 構建 GPU 支持的 Docker 映像
echo "構建支持 GPU 的 Docker 映像..."
docker build -t flask-translation-api-gpu:latest -f Dockerfile.gpu .

# 停止並移除舊容器（如果存在）
echo "停止舊容器..."
docker stop flask-translation-service-gpu 2>/dev/null || true
docker rm flask-translation-service-gpu 2>/dev/null || true

# 運行新容器
echo "啟動新容器（GPU 支持）..."
docker run -d \
  --name flask-translation-service-gpu \
  --gpus all \
  -p 5000:5000 \
  -v $(pwd)/models:/app/models \
  -e GGUF_FILE=models/LLaMAX3-8B-Alpaca.Q8_0.gguf \
  -e N_GPU_LAYERS=-1 \
  -e N_THREADS=8 \
  --restart unless-stopped \
  flask-translation-api-gpu:latest

echo "部署完成！"
echo "服務可在 http://localhost:5000 訪問"
echo "使用 'docker logs flask-translation-service-gpu' 查看日誌"
