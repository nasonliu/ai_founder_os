"""
AI Provider Configuration
Defines available AI providers and their models.
"""

PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": [
            {"id": "gpt-4o", "name": "GPT-4o", "context": 128000, "price": "$5/1M"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "context": 128000, "price": "$0.15/1M"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context": 128000, "price": "$10/1M"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context": 16000, "price": "$0.50/1M"},
        ]
    },
    "anthropic": {
        "name": "Anthropic",
        "models": [
            {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "context": 200000, "price": "$3/1M"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context": 200000, "price": "$15/1M"},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context": 200000, "price": "$3/1M"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context": 200000, "price": "$0.25/1M"},
        ]
    },
    "deepseek": {
        "name": "DeepSeek",
        "models": [
            {"id": "deepseek-chat", "name": "DeepSeek Chat", "context": 64000, "price": "$0.14/1M"},
            {"id": "deepseek-coder", "name": "DeepSeek Coder", "context": 16000, "price": "$0.14/1M"},
        ]
    },
    "minimax": {
        "name": "MiniMax",
        "models": [
            {"id": "MiniMax-Text-01", "name": "MiniMax Text 01", "context": 1000000, "price": "Free"},
            {"id": "abab6.5s", "name": "Abab 6.5s", "context": 245000, "price": "¥1/1M"},
            {"id": "abab6.5g", "name": "Abab 6.5g", "context": 245000, "price": "¥1/1M"},
        ]
    },
    "alibaba": {
        "name": "Alibaba (Qwen)",
        "models": [
            {"id": "qwen-turbo", "name": "Qwen Turbo", "context": 1000000, "price": "¥1/1M"},
            {"id": "qwen-plus", "name": "Qwen Plus", "context": 32000, "price": "¥4/1M"},
            {"id": "qwen-max", "name": "Qwen Max", "context": 8000, "price": "¥20/1M"},
        ]
    },
    "zhipu": {
        "name": "Zhipu AI",
        "models": [
            {"id": "glm-4", "name": "GLM-4", "context": 128000, "price": "¥1/1M"},
            {"id": "glm-4-flash", "name": "GLM-4 Flash", "context": 128000, "price": "¥0.1/1M"},
            {"id": "glm-4-plus", "name": "GLM-4 Plus", "context": 128000, "price": "¥5/1M"},
        ]
    },
    "openrouter": {
        "name": "OpenRouter",
        "models": [
            {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet", "context": 200000, "price": "$3/1M"},
            {"id": "google/gemini-pro-1.5", "name": "Gemini Pro 1.5", "context": 1000000, "price": "$1.25/1M"},
            {"id": "meta-llama-3.1-405b-instruct", "name": "Llama 3.1 405B", "context": 128000, "price": "$3.5/1M"},
        ]
    },
    "github": {
        "name": "GitHub Copilot",
        "models": [
            {"id": "gpt-4", "name": "GPT-4", "context": 8000, "price": "$10/1M"},
            {"id": "gpt-4o", "name": "GPT-4o", "context": 128000, "price": "$5/1M"},
        ]
    },
    "brave": {
        "name": "Brave Search",
        "models": [
            {"id": "web-search", "name": "Web Search API", "context": 0, "price": "¥5/100次"},
        ]
    }
}

def get_provider(provider_id):
    return PROVIDERS.get(provider_id, {"name": provider_id, "models": []})

def list_providers():
    return [{"id": pid, "name": info["name"], "model_count": len(info["models"])} for pid, info in PROVIDERS.items()]
