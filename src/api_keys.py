
"""
API Key Manager for AI Founder OS
"""

import subprocess
import json
from typing import Dict, List, Optional

# Default fallback models when no API key
DEFAULT_MODELS = {
    "openai": [
        {"id": "gpt-4o-2025-03-26", "name": "GPT-4o (2025-03-26)"},
        {"id": "gpt-4o", "name": "GPT-4o"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        {"id": "o1", "name": "O1"},
        {"id": "o1-mini", "name": "O1 Mini"},
        {"id": "o3-mini", "name": "O3 Mini"},
    ],
    "anthropic": [
        {"id": "claude-opus-4-5-20250514", "name": "Claude Opus 4.5"},
        {"id": "claude-sonnet-4-5-20250514", "name": "Claude Sonnet 4.5"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku"},
    ],
    "deepseek": [
        {"id": "deepseek-chat", "name": "DeepSeek Chat"},
        {"id": "deepseek-reasoner", "name": "DeepSeek Reasoner"},
        {"id": "deepseek-coder", "name": "DeepSeek Coder"},
    ],
    "minimax": [
        {"id": "MiniMax-Text-01", "name": "MiniMax Text 01"},
        {"id": "MiniMax-M2.1", "name": "MiniMax M2.1"},
        {"id": "MiniMax-M2", "name": "MiniMax M2"},
    ],
    "alibaba": [
        {"id": "qwen-turbo", "name": "Qwen Turbo"},
        {"id": "qwen-plus", "name": "Qwen Plus"},
        {"id": "qwen-max", "name": "Qwen Max"},
        {"id": "qwen2.5-72b", "name": "Qwen 2.5 72B"},
        {"id": "qwen2.5-coder-32b", "name": "Qwen 2.5 Coder"},
    ],
    "zhipu": [
        {"id": "glm-4", "name": "GLM-4"},
        {"id": "glm-4-flash", "name": "GLM-4 Flash"},
        {"id": "glm-4-plus", "name": "GLM-4 Plus"},
        {"id": "glm-4-long", "name": "GLM-4 Long"},
        {"id": "glm-4o", "name": "GLM-4o"},
    ],
    "openrouter": [
        {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet"},
        {"id": "google/gemini-2.0-pro-exp", "name": "Gemini 2.0 Pro"},
        {"id": "meta-llama-3.3-70b-instruct", "name": "Llama 3.3 70B"},
    ],
    "github": [
        {"id": "gpt-4o", "name": "GPT-4o"},
        {"id": "gpt-4", "name": "GPT-4"},
    ],
    "brave": [
        {"id": "web-search", "name": "Web Search API"},
    ],
}


def curl_get(url: str, headers: Dict[str, str] = None) -> Optional[Dict]:
    """Make a GET request using curl"""
    try:
        cmd = ["curl", "-s", url]
        if headers:
            for k, v in headers.items():
                cmd.extend(["-H", f"{k}: {v}"])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Curl error: {e}")
    return None


def fetch_openai_models(api_key: str) -> List[Dict]:
    """Fetch models from OpenAI"""
    if not api_key:
        return []
    data = curl_get(
        "https://api.openai.com/v1/models",
        {"Authorization": f"Bearer {api_key}"}
    )
    if data and "data" in data:
        return [{"id": m["id"], "name": m.get("name", m["id"])} for m in data["data"][:20]]
    return DEFAULT_MODELS.get("openai", [])


def fetch_deepseek_models(api_key: str) -> List[Dict]:
    """Fetch models from DeepSeek"""
    if not api_key:
        return []
    data = curl_get(
        "https://api.deepseek.com/v1/models",
        {"Authorization": f"Bearer {api_key}"}
    )
    if data and "data" in data:
        return [{"id": m["id"], "name": m.get("id", m.get("id"))} for m in data["data"]]
    return DEFAULT_MODELS.get("deepseek", [])


def fetch_alibaba_models(api_key: str) -> List[Dict]:
    """Fetch models from Alibaba (Qwen)"""
    if not api_key:
        return []
    data = curl_get(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/models",
        {"Authorization": f"Bearer {api_key}"}
    )
    if data and "data" in data:
        models = data["data"].get("models", [])
        return [{"id": m["id"], "name": m.get("id", "")} for m in models[:20]]
    return DEFAULT_MODELS.get("alibaba", [])


def fetch_zhipu_models(api_key: str) -> List[Dict]:
    """Fetch models from Zhipu AI"""
    if not api_key:
        return []
    data = curl_get(
        "https://open.bigmodel.cn/api/paas/v4/models",
        {"Authorization": f"Bearer {api_key}"}
    )
    if data and "data" in data:
        return [{"id": m["id"], "name": m.get("name", m["id"])} for m in data["data"][:20]]
    return DEFAULT_MODELS.get("zhipu", [])


def fetch_models_for_provider(provider: str, api_key: str) -> List[Dict]:
    """Fetch models for a specific provider"""
    if not api_key:
        return DEFAULT_MODELS.get(provider, [])
    
    fetchers = {
        "openai": fetch_openai_models,
        "deepseek": fetch_deepseek_models,
        "alibaba": fetch_alibaba_models,
        "zhipu": fetch_zhipu_models,
    }
    
    fetcher = fetchers.get(provider)
    if fetcher:
        result = fetcher(api_key)
        if result:
            return result
    return DEFAULT_MODELS.get(provider, [])


def get_provider_models(provider: str, api_key: Optional[str] = None) -> List[Dict]:
    """Get models for a provider, using API key if provided"""
    return fetch_models_for_provider(provider, api_key if api_key else "")
