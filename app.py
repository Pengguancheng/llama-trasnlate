from flask import Flask, request, jsonify
from llama_cpp import Llama
import os

app = Flask(__name__)

# Language code to full name mapping
LANGUAGE_CODES = {
    # Requested in issue description
    'vi': 'Vietnamese',
    'id': 'Indonesian',
    'th': 'Thai',
    'zh': 'Chinese',
    # Other common languages
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ru': 'Russian',
    'ar': 'Arabic',
    'pt': 'Portuguese'
}

# Initialize the model
GGUF_FILE = os.environ.get('GGUF_FILE', "models/LLaMAX3-8B-Alpaca.Q8_0.gguf")
N_GPU_LAYERS = int(os.environ.get('N_GPU_LAYERS', '-1'))  # -1 means all layers
N_THREADS = int(os.environ.get('N_THREADS', 8))

# 使用llama_cpp直接加載GGUF模型
llm = Llama(
    model_path=GGUF_FILE,
    n_gpu_layers=N_GPU_LAYERS,  # 使用GPU加速
    n_threads=N_THREADS,        # 使用多線程
    n_ctx=2048                  # 上下文長度
)

def Prompt_template(query, src_language, trg_language):
    # 统一所有语言的翻译指令，处理非标准文本
    instruction = (
        f'Translate the following text from {src_language} to {trg_language}. '
        'For non-standard text, follow this process: '
        '1) Segment the text into meaningful units; '
        '2) Identify non-standard spellings, abbreviations, or slang and map them to standard forms; '
        '3) Infer the meaning of any colloquial terms using context; '
        '4) Mentally reconstruct the normalized version of the original sentence; '
        '5) Translate accurately based on the reconstructed meaning. '
        'Return ONLY the final translation result without any explanations or process notes.'
    )

    prompt = (
        'Below is an instruction that describes a task, paired with an input that provides further context. '
        'Write a response that appropriately completes the request.\n'
        f'### Instruction:\n{instruction}\n'
        f'### Input:\n{query}\n### Response:'
    )
    return prompt

def translate_with_llama(query, src_language, trg_language):
    DEFAULT_MAX_TOKENS = 1024
    DEFAULT_TEMPERATURE = 0.2

    # 使用直接的文本生成而非聊天格式
    result = llm(
        Prompt_template(query, src_language, trg_language),
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
        echo=False
    )

    # 提取並清理結果
    raw_translation = result.get('choices', [{}])[0].get('text', '').strip()

    return raw_translation


@app.route('/translate', methods=['POST'])
def translate():
    data = request.json

    # Validate input
    if not data or 'text' not in data or 'source_lang' not in data or 'target_lang' not in data:
        return jsonify({
            'error': 'Missing required parameters. Please provide text, source_lang, and target_lang.'
        }), 400

    text = data['text']
    source_lang = data['source_lang']
    target_lang = data['target_lang']

    # Convert language codes to full names if they exist in our mapping
    source_lang_full = LANGUAGE_CODES.get(source_lang.lower(), source_lang)
    target_lang_full = LANGUAGE_CODES.get(target_lang.lower(), target_lang)

    try:
        # 使用llama_cpp直接生成翻譯
        generated_text = translate_with_llama(text, source_lang_full, target_lang_full)

        return jsonify({
            'source_text': text,
            'source_lang': source_lang,
            'source_lang_full': source_lang_full,
            'target_lang': target_lang,
            'target_lang_full': target_lang_full,
            'translation': generated_text
        })
    except Exception as e:
        return jsonify({
            'error': f'Translation failed: {str(e)}'
        }), 500

@app.route('/languages', methods=['GET'])
def get_languages():
    """
    Returns a mapping of language codes to their full names.
    This can be used as a reference for translation requests.
    """
    return jsonify({
        'language_codes': LANGUAGE_CODES,
        'message': 'Use these language codes or full names in the source_lang and target_lang fields of translation requests.'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點，確認服務是否正常運行"""
    return jsonify({
        "status": "healthy",
        "model": GGUF_FILE
    })

@app.route('/batch-translate', methods=['POST'])
def batch_translate():
    """
    批量翻译API，可以一次请求多个目标语言的翻译结果
    目标语言可以用\n分隔的字符串或数组形式提供
    """
    data = request.json

    # 验证输入
    if not data or 'text' not in data or 'source_lang' not in data or 'target_langs' not in data:
        return jsonify({
            'error': '缺少必要参数。请提供text、source_lang和target_langs。'
        }), 400

    text = data['text']
    source_lang = data['source_lang']
    target_langs = data['target_langs']

    # 处理目标语言参数
    # 可以是用\n分隔的字符串或者数组
    if isinstance(target_langs, str):
        target_langs = target_langs.split('\n')

    # 转换源语言代码为全名
    source_lang_full = LANGUAGE_CODES.get(source_lang.lower(), source_lang)

    results = ''
    errors = {}

    # 对每个目标语言进行翻译
    for target_lang in target_langs:
        target_lang = target_lang.strip()
        if not target_lang:  # 跳过空字符串
            continue

        # 转换目标语言代码为全名
        target_lang_full = LANGUAGE_CODES.get(target_lang.lower(), target_lang)

        try:
            # 使用现有翻译函数
            translation = translate_with_llama(text, source_lang_full, target_lang_full)

            # 保存结果
            results = f'{results}\n{translation}'
        except Exception as e:
            # 记录错误
            errors[target_lang] = str(e)

    # 构建响应
    response = {
        'source_text': text,
        'source_lang': source_lang,
        'source_lang_full': source_lang_full,
        'translations': results
    }

    # 如果有错误，添加到响应中
    if errors:
        response['errors'] = errors
        return jsonify(response), 500

    return results

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)