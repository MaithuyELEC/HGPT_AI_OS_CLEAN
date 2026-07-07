"""Contract-only provider adapter skeletons."""

from hgpt_ai_os.providers.adapters.claude_adapter import ClaudeAdapter
from hgpt_ai_os.providers.adapters.deepseek_adapter import DeepSeekAdapter
from hgpt_ai_os.providers.adapters.gemini_adapter import GeminiAdapter
from hgpt_ai_os.providers.adapters.ollama_adapter import OllamaAdapter
from hgpt_ai_os.providers.adapters.openai_adapter import OpenAIAdapter
from hgpt_ai_os.providers.adapters.openrouter_adapter import OpenRouterAdapter
from hgpt_ai_os.providers.adapters.qwen_adapter import QwenAdapter

__all__ = [
    "ClaudeAdapter",
    "DeepSeekAdapter",
    "GeminiAdapter",
    "OllamaAdapter",
    "OpenAIAdapter",
    "OpenRouterAdapter",
    "QwenAdapter",
]
