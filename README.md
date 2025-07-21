# Translation API Service
# GGUF 模型翻譯 API

這個 Flask 應用程式使用 llama-cpp-python 直接處理 GGUF 格式量化模型提供翻譯服務，無需解量化過程。

## 環境設置

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 環境變數

- `GGUF_FILE`: GGUF 檔案路徑，默認為 "models/LLaMAX3-8B-Alpaca.Q8_0.gguf"
- `N_GPU_LAYERS`: 使用GPU加速的層數，-1表示所有層，默認為-1
- `N_THREADS`: 使用的CPU線程數，默認為4
- `PORT`: 服務埠號，默認為 5000

## 啟動服務

```bash
python app.py
```

## API 使用

### 翻譯 API

```
POST /translate
```

請求體：

```json
{
  "text": "你好，今天是个好日子",
  "source_lang": "zh",
  "target_lang": "en"
}
```

### 批次翻譯 API

```
POST /batch-translate
```

請求體：

```json
{
  "text": "你好，今天是个好日子",
  "source_lang": "zh",
  "target_langs": ["en", "vi", "id"]
}
```

或者使用 \n 分隔的字符串：

```json
{
  "text": "你好，今天是个好日子",
  "source_lang": "zh",
  "target_langs": "en\nvi\nid"
}
```

### 支援的語言

```
GET /languages
```

### 健康檢查

```
GET /health
```
This project provides a REST API for translating text between different languages using the LLaMA model.

## Features

- Translate text between various languages
- Support for language codes (vi, id, th, zh, etc.) and full language names
- Simple REST API interface
- Containerized with Docker
- Health check endpoint
- Language code reference endpoint

## API Endpoints

### Translate Text

**Endpoint:** `/translate`
**Method:** POST
**Request Body:**
```json
{
  "text": "Text to translate",
  "source_lang": "Source language (e.g., 'vi' or 'Vietnamese')",
  "target_lang": "Target language (e.g., 'zh' or 'Chinese')"
}
```

**Response:**
```json
{
  "source_text": "Original text",
  "source_lang": "Source language code or name as provided",
  "source_lang_full": "Full source language name",
  "target_lang": "Target language code or name as provided",
  "target_lang_full": "Full target language name",
  "translation": "Translated text"
}
```

### Batch Translation

**Endpoint:** `/batch-translate`
**Method:** POST
**Request Body:**
```json
{
  "text": "Text to translate",
  "source_lang": "Source language (e.g., 'zh' or 'Chinese')",
  "target_langs": ["en", "vi", "id"] 
}
```

Alternatively, you can use a newline-separated string for target languages:

```json
{
  "text": "Text to translate",
  "source_lang": "Source language (e.g., 'zh' or 'Chinese')",
  "target_langs": "en\nvi\nid"
}
```

**Response:**
```json
{
  "source_text": "Original text",
  "source_lang": "Source language code or name as provided",
  "source_lang_full": "Full source language name",
  "translations": {
    "en": {
      "target_lang_full": "English",
      "translation": "Translated text in English"
    },
    "vi": {
      "target_lang_full": "Vietnamese",
      "translation": "Translated text in Vietnamese"
    },
    "id": {
      "target_lang_full": "Indonesian",
      "translation": "Translated text in Indonesian"
    }
  }
}
```

**Notes:**
- You can use either language codes (e.g., 'vi', 'zh') or full language names (e.g., 'Vietnamese', 'Chinese') for `source_lang` and `target_lang`.
- The API will automatically convert language codes to full names when communicating with the translation model.
- See the `/languages` endpoint for a complete list of supported language codes.

### Language Codes Reference

**Endpoint:** `/languages`
**Method:** GET
**Response:**
```json
{
  "language_codes": {
    "vi": "Vietnamese",
    "id": "Indonesian",
    "th": "Thai",
    "zh": "Chinese",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "ar": "Arabic",
    "pt": "Portuguese"
  },
  "message": "Use these language codes or full names in the source_lang and target_lang fields of translation requests."
}
```

### Health Check

**Endpoint:** `/health`
**Method:** GET
**Response:**
```json
{
  "status": "healthy",
  "model": "Path to the model"
}
```

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- LLaMA model files in the `models/` directory

### Local Development

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

### Docker Deployment

#### 方法 1: 使用 Docker 命令

1. 構建 Docker 映像:
   ```bash
   docker build -t translation-api .
   ```

2. 運行容器:
   ```bash
   docker run -v /path/to/models:/app/models -p 5000:5000 translation-api
   ```

   將 `/path/to/models` 替換為您 LLaMA 模型文件的路徑。

#### 方法 2: 使用 Docker Compose

1. 運行服務:
   ```bash
   docker-compose up -d
   ```

2. 查看日誌:
   ```bash
   docker-compose logs -f
   ```

3. 停止服務:
   ```bash
   docker-compose down
   ```

#### 方法 3: 使用部署腳本

1. 添加執行權限:
   ```bash
   chmod +x deploy.sh
   ```

2. 運行部署腳本:
   ```bash
   ./deploy.sh
   ```

## Example Usage

### Using Full Language Names

```bash
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Này từ bụng 2m go dc tran fio 1m8, mừng qá",
    "source_lang": "Vietnamese",
    "target_lang": "Chinese"
  }'
```

### Using Language Codes

```bash
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Này từ bụng 2m go dc tran fio 1m8, mừng qá",
    "source_lang": "vi",
    "target_lang": "zh"
  }'
```

### Getting Language Code Reference

```bash
curl -X GET http://localhost:5000/languages
```

## Docker 配置注意事項

### 硬件需求
- **CPU**: 根據模型大小，建議至少 4 核心
- **內存**: 至少 8GB RAM，推薦 16GB+
- **GPU**: 可選，但會加速處理

### 模型掛載
運行 Docker 容器時，您必須掛載包含 GGUF 模型文件的目錄：

```bash
docker run -v /本機/模型/路徑:/app/models -p 5000:5000 translation-api
```

### GPU 加速
使用 NVIDIA GPU 加速需要安裝 NVIDIA Container Toolkit:

```bash
docker run --gpus all -v /本機/模型/路徑:/app/models -p 5000:5000 translation-api
```

### 環境變數調整
您可以通過傳遞環境變數來調整容器行為：

```bash
docker run \
  -e GGUF_FILE=models/您的模型.gguf \
  -e N_GPU_LAYERS=20 \
  -e N_THREADS=4 \
  -e PORT=8080 \
  -v /本機/模型/路徑:/app/models \
  -p 8080:8080 \
  translation-api
```

## 排錯指南

### Docker 構建問題

如果在構建 Docker 映像時遇到與 `llama-cpp-python` 相關的錯誤，可以嘗試以下解決方案：

1. **使用預構建的 llama-cpp-python 包**：
   我們使用來自 Rasa 的預構建輪子，避免了本地編譯問題：
   ```bash
   # CPU 版本（默認 Dockerfile）
   pip install llama-cpp-python==0.2.38 --extra-index-url https://wheels.rasa.com/llama-cpp-python/cpu/
   # GPU 版本（Dockerfile.gpu）
   pip install llama-cpp-python==0.2.38 --extra-index-url https://wheels.rasa.com/llama-cpp-python/cuda/
   ```

2. **使用 GPU 版本**：如果需要 GPU 加速，使用 `Dockerfile.gpu` 和 `docker-compose.gpu.yml`：
   ```bash
   docker-compose -f docker-compose.gpu.yml up -d
   # 或者
   ./deploy-gpu.sh
   ```

### 運行時問題

1. **模型載入錯誤**：確保模型路徑正確，並且已掛載到容器中：
   ```bash
   docker run -v $(pwd)/models:/app/models ...
   ```

2. **內存不足**：較大的模型可能需要更多內存，調整 Docker 內存限制：
   ```bash
   docker run --memory=16g ...
   ```

3. **GPU 訪問問題**：確保 NVIDIA Container Toolkit 已正確安裝並配置：
   ```bash
   # 檢查 GPU 是否可用
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```