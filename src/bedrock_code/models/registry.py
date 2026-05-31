from __future__ import annotations

from typing import Any

BEDROCK_MODELS: dict[str, dict[str, Any]] = {

    # ════════════════════════════════════════════════════════════════════════
    # Anthropic Claude — global cross-region inference (Claude 4 series)
    # ════════════════════════════════════════════════════════════════════════
    "claude-sonnet-4-6": {
        "id": "global.anthropic.claude-sonnet-4-6",
        "display_name": "Claude Sonnet 4.6",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 3.00, "output_cost_per_1m": 15.00,
        "context_window": 200_000, "available": True, "default": True,
        "region_prefix": "global",
    },
    "claude-sonnet-4-5": {
        "id": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "display_name": "Claude Sonnet 4.5",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 3.00, "output_cost_per_1m": 15.00,
        "context_window": 200_000, "available": True,
        "region_prefix": "global",
    },
    "claude-haiku-4-5": {
        "id": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
        "display_name": "Claude Haiku 4.5",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 0.80, "output_cost_per_1m": 4.00,
        "context_window": 200_000, "available": True,
        "region_prefix": "global",
    },
    "claude-opus-4-8": {
        "id": "global.anthropic.claude-opus-4-8",
        "display_name": "Claude Opus 4.8",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 15.00, "output_cost_per_1m": 75.00,
        "context_window": 200_000, "available": True,
        "region_prefix": "global",
    },
    "claude-opus-4-7": {
        "id": "global.anthropic.claude-opus-4-7",
        "display_name": "Claude Opus 4.7",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 15.00, "output_cost_per_1m": 75.00,
        "context_window": 200_000, "available": True,
        "region_prefix": "global",
    },
    "claude-opus-4-5": {
        "id": "global.anthropic.claude-opus-4-5-20251101-v1:0",
        "display_name": "Claude Opus 4.5",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 15.00, "output_cost_per_1m": 75.00,
        "context_window": 200_000, "available": True,
        "region_prefix": "global",
    },

    # ════════════════════════════════════════════════════════════════════════
    # Anthropic Claude — APAC cross-region inference (Claude 3.x / 3.5 / 3.7)
    # ════════════════════════════════════════════════════════════════════════
    "claude-sonnet-4": {
        "id": "apac.anthropic.claude-sonnet-4-20250514-v1:0",
        "display_name": "Claude Sonnet 4 (APAC)",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 3.00, "output_cost_per_1m": 15.00,
        "context_window": 200_000, "available": True,
        "region_prefix": "apac",
    },
    "claude-sonnet-3-7": {
        "id": "apac.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "display_name": "Claude Sonnet 3.7 (APAC)",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 3.00, "output_cost_per_1m": 15.00,
        "context_window": 200_000, "available": True,
        "region_prefix": "apac",
    },
    "claude-sonnet-3-5": {
        "id": "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "display_name": "Claude Sonnet 3.5 (APAC)",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 3.00, "output_cost_per_1m": 15.00,
        "context_window": 200_000, "available": True,
        "region_prefix": "apac",
    },
    "claude-sonnet-3-5-v1": {
        "id": "apac.anthropic.claude-3-5-sonnet-20240620-v1:0",
        "display_name": "Claude Sonnet 3.5 v1 (APAC)",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 3.00, "output_cost_per_1m": 15.00,
        "context_window": 200_000, "available": True,
        "region_prefix": "apac",
    },
    "claude-haiku-3": {
        "id": "apac.anthropic.claude-3-haiku-20240307-v1:0",
        "display_name": "Claude Haiku 3 (APAC)",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 0.25, "output_cost_per_1m": 1.25,
        "context_window": 200_000, "available": True,
        "region_prefix": "apac",
    },
    "claude-sonnet-3": {
        "id": "apac.anthropic.claude-3-sonnet-20240229-v1:0",
        "display_name": "Claude Sonnet 3 (APAC)",
        "provider": "Anthropic",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 3.00, "output_cost_per_1m": 15.00,
        "context_window": 200_000, "available": True,
        "region_prefix": "apac",
    },

    # ════════════════════════════════════════════════════════════════════════
    # Amazon Nova — APAC cross-region inference (web search capable)
    # ════════════════════════════════════════════════════════════════════════
    "nova-pro": {
        "id": "apac.amazon.nova-pro-v1:0",
        "display_name": "Amazon Nova Pro (APAC)",
        "provider": "Amazon",
        "tool_use": True, "streaming": True, "vision": True, "web_search": True,
        "input_cost_per_1m": 0.80, "output_cost_per_1m": 3.20,
        "context_window": 300_000, "available": True,
        "region_prefix": "apac",
    },
    "nova-lite": {
        "id": "apac.amazon.nova-lite-v1:0",
        "display_name": "Amazon Nova Lite (APAC)",
        "provider": "Amazon",
        "tool_use": True, "streaming": True, "vision": True, "web_search": True,
        "input_cost_per_1m": 0.06, "output_cost_per_1m": 0.24,
        "context_window": 300_000, "available": True,
        "region_prefix": "apac",
    },
    "nova-micro": {
        "id": "apac.amazon.nova-micro-v1:0",
        "display_name": "Amazon Nova Micro (APAC)",
        "provider": "Amazon",
        "tool_use": False, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.035, "output_cost_per_1m": 0.14,
        "context_window": 128_000, "available": True,
        "region_prefix": "apac",
    },
    "nova-2-lite": {
        "id": "global.amazon.nova-2-lite-v1:0",
        "display_name": "Amazon Nova 2 Lite (Global)",
        "provider": "Amazon",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 0.06, "output_cost_per_1m": 0.24,
        "context_window": 300_000, "available": True,
        "region_prefix": "global",
    },

    # ════════════════════════════════════════════════════════════════════════
    # Qwen3 (Alibaba) — on-demand in ap-south-1
    # ════════════════════════════════════════════════════════════════════════
    "qwen3-235b": {
        "id": "qwen.qwen3-235b-a22b-2507-v1:0",
        "display_name": "Qwen3 235B MoE",
        "provider": "Qwen",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.22, "output_cost_per_1m": 0.88,
        "context_window": 128_000, "available": True,
    },
    "qwen3-coder-480b": {
        "id": "qwen.qwen3-coder-480b-a35b-v1:0",
        "display_name": "Qwen3 Coder 480B MoE",
        "provider": "Qwen",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.50, "output_cost_per_1m": 2.00,
        "context_window": 128_000, "available": True,
    },
    "qwen3-coder-30b": {
        "id": "qwen.qwen3-coder-30b-a3b-v1:0",
        "display_name": "Qwen3 Coder 30B",
        "provider": "Qwen",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.15, "output_cost_per_1m": 0.60,
        "context_window": 128_000, "available": True,
    },
    "qwen3-32b": {
        "id": "qwen.qwen3-32b-v1:0",
        "display_name": "Qwen3 32B",
        "provider": "Qwen",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.12, "output_cost_per_1m": 0.48,
        "context_window": 128_000, "available": True,
    },
    "qwen3-80b": {
        "id": "qwen.qwen3-next-80b-a3b",
        "display_name": "Qwen3 80B",
        "provider": "Qwen",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.20, "output_cost_per_1m": 0.80,
        "context_window": 128_000, "available": True,
    },
    "qwen3-vl-235b": {
        "id": "qwen.qwen3-vl-235b-a22b",
        "display_name": "Qwen3 VL 235B (vision)",
        "provider": "Qwen",
        "tool_use": True, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 0.22, "output_cost_per_1m": 0.88,
        "context_window": 128_000, "available": True,
    },

    # ════════════════════════════════════════════════════════════════════════
    # Z.AI GLM — on-demand in ap-south-1
    # ════════════════════════════════════════════════════════════════════════
    "glm-5": {
        "id": "zai.glm-5",
        "display_name": "GLM-5",
        "provider": "Z.AI",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 1.00, "output_cost_per_1m": 4.00,
        "context_window": 128_000, "available": True,
    },
    "glm-4-7": {
        "id": "zai.glm-4.7",
        "display_name": "GLM-4.7",
        "provider": "Z.AI",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.50, "output_cost_per_1m": 2.00,
        "context_window": 128_000, "available": True,
    },
    "glm-4-7-flash": {
        "id": "zai.glm-4.7-flash",
        "display_name": "GLM-4.7 Flash",
        "provider": "Z.AI",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.10, "output_cost_per_1m": 0.40,
        "context_window": 128_000, "available": True,
    },

    # ════════════════════════════════════════════════════════════════════════
    # DeepSeek — on-demand in ap-south-1
    # ════════════════════════════════════════════════════════════════════════
    "deepseek-v3-2": {
        "id": "deepseek.v3.2",
        "display_name": "DeepSeek V3.2",
        "provider": "DeepSeek",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.27, "output_cost_per_1m": 1.10,
        "context_window": 128_000, "available": True,
    },
    "deepseek-v3": {
        "id": "deepseek.v3-v1:0",
        "display_name": "DeepSeek V3",
        "provider": "DeepSeek",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.27, "output_cost_per_1m": 1.10,
        "context_window": 128_000, "available": True,
    },

    # ════════════════════════════════════════════════════════════════════════
    # Moonshot Kimi — on-demand in ap-south-1
    # ════════════════════════════════════════════════════════════════════════
    "kimi-k2": {
        "id": "moonshotai.kimi-k2.5",
        "display_name": "Kimi K2.5",
        "provider": "Moonshot AI",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.60, "output_cost_per_1m": 2.50,
        "context_window": 128_000, "available": True,
    },
    "kimi-k2-thinking": {
        "id": "moonshot.kimi-k2-thinking",
        "display_name": "Kimi K2 Thinking",
        "provider": "Moonshot AI",
        "tool_use": False, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 2.00, "output_cost_per_1m": 8.00,
        "context_window": 128_000, "available": True,
    },

    # ════════════════════════════════════════════════════════════════════════
    # Mistral AI — on-demand in ap-south-1
    # ════════════════════════════════════════════════════════════════════════
    "mistral-large-3": {
        "id": "mistral.mistral-large-3-675b-instruct",
        "display_name": "Mistral Large 3 (675B)",
        "provider": "Mistral AI",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 2.00, "output_cost_per_1m": 6.00,
        "context_window": 128_000, "available": True,
    },
    "devstral-2": {
        "id": "mistral.devstral-2-123b",
        "display_name": "Devstral 2 (123B)",
        "provider": "Mistral AI",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.40, "output_cost_per_1m": 1.60,
        "context_window": 128_000, "available": True,
    },
    "magistral-small": {
        "id": "mistral.magistral-small-2509",
        "display_name": "Magistral Small",
        "provider": "Mistral AI",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.50, "output_cost_per_1m": 1.50,
        "context_window": 128_000, "available": True,
    },
    "ministral-8b": {
        "id": "mistral.ministral-3-8b-instruct",
        "display_name": "Ministral 8B",
        "provider": "Mistral AI",
        "tool_use": False, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.10, "output_cost_per_1m": 0.10,
        "context_window": 128_000, "available": True,
    },
    "ministral-14b": {
        "id": "mistral.ministral-3-14b-instruct",
        "display_name": "Ministral 14B",
        "provider": "Mistral AI",
        "tool_use": False, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.15, "output_cost_per_1m": 0.15,
        "context_window": 128_000, "available": True,
    },
    "mistral-large-2": {
        "id": "mistral.mistral-large-2402-v1:0",
        "display_name": "Mistral Large 2",
        "provider": "Mistral AI",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 4.00, "output_cost_per_1m": 12.00,
        "context_window": 32_000, "available": True,
    },
    "mixtral-8x7b": {
        "id": "mistral.mixtral-8x7b-instruct-v0:1",
        "display_name": "Mixtral 8x7B",
        "provider": "Mistral AI",
        "tool_use": False, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.45, "output_cost_per_1m": 0.70,
        "context_window": 32_000, "available": True,
    },

    # ════════════════════════════════════════════════════════════════════════
    # NVIDIA Nemotron — on-demand in ap-south-1
    # ════════════════════════════════════════════════════════════════════════
    "nemotron-super-120b": {
        "id": "nvidia.nemotron-super-3-120b",
        "display_name": "Nemotron Super 120B",
        "provider": "NVIDIA",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.40, "output_cost_per_1m": 1.60,
        "context_window": 128_000, "available": True,
    },
    "nemotron-nano-30b": {
        "id": "nvidia.nemotron-nano-3-30b",
        "display_name": "Nemotron Nano 30B",
        "provider": "NVIDIA",
        "tool_use": False, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.15, "output_cost_per_1m": 0.60,
        "context_window": 128_000, "available": True,
    },

    # ════════════════════════════════════════════════════════════════════════
    # MiniMax — on-demand in ap-south-1
    # ════════════════════════════════════════════════════════════════════════
    "minimax-m2-5": {
        "id": "minimax.minimax-m2.5",
        "display_name": "MiniMax M2.5",
        "provider": "MiniMax",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.40, "output_cost_per_1m": 1.60,
        "context_window": 1_000_000, "available": True,
    },
    "minimax-m2": {
        "id": "minimax.minimax-m2",
        "display_name": "MiniMax M2",
        "provider": "MiniMax",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.30, "output_cost_per_1m": 1.10,
        "context_window": 1_000_000, "available": True,
    },

    # ════════════════════════════════════════════════════════════════════════
    # Google Gemma — on-demand in ap-south-1
    # ════════════════════════════════════════════════════════════════════════
    "gemma-3-27b": {
        "id": "google.gemma-3-27b-it",
        "display_name": "Gemma 3 27B",
        "provider": "Google",
        "tool_use": False, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 0.20, "output_cost_per_1m": 0.60,
        "context_window": 128_000, "available": True,
    },
    "gemma-3-12b": {
        "id": "google.gemma-3-12b-it",
        "display_name": "Gemma 3 12B",
        "provider": "Google",
        "tool_use": False, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 0.10, "output_cost_per_1m": 0.30,
        "context_window": 128_000, "available": True,
    },
    "gemma-3-4b": {
        "id": "google.gemma-3-4b-it",
        "display_name": "Gemma 3 4B",
        "provider": "Google",
        "tool_use": False, "streaming": True, "vision": True, "web_search": False,
        "input_cost_per_1m": 0.04, "output_cost_per_1m": 0.12,
        "context_window": 128_000, "available": True,
    },

    # ════════════════════════════════════════════════════════════════════════
    # Meta Llama — on-demand in ap-south-1
    # ════════════════════════════════════════════════════════════════════════
    "llama-3-70b": {
        "id": "meta.llama3-70b-instruct-v1:0",
        "display_name": "Llama 3 70B",
        "provider": "Meta",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.99, "output_cost_per_1m": 0.99,
        "context_window": 8_000, "available": True,
    },
    "llama-3-8b": {
        "id": "meta.llama3-8b-instruct-v1:0",
        "display_name": "Llama 3 8B",
        "provider": "Meta",
        "tool_use": False, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.30, "output_cost_per_1m": 0.60,
        "context_window": 8_000, "available": True,
    },

    # ════════════════════════════════════════════════════════════════════════
    # OpenAI OSS (via Bedrock) — on-demand in ap-south-1
    # ════════════════════════════════════════════════════════════════════════
    "gpt-oss-120b": {
        "id": "openai.gpt-oss-120b-1:0",
        "display_name": "OpenAI OSS 120B",
        "provider": "OpenAI",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 1.00, "output_cost_per_1m": 4.00,
        "context_window": 128_000, "available": True,
    },
    "gpt-oss-20b": {
        "id": "openai.gpt-oss-20b-1:0",
        "display_name": "OpenAI OSS 20B",
        "provider": "OpenAI",
        "tool_use": True, "streaming": True, "vision": False, "web_search": False,
        "input_cost_per_1m": 0.20, "output_cost_per_1m": 0.80,
        "context_window": 128_000, "available": True,
    },
}

DEFAULT_MODEL_ALIAS = "claude-sonnet-4-6"


def get_model_id(alias_or_id: str) -> str | None:
    if alias_or_id in BEDROCK_MODELS:
        return BEDROCK_MODELS[alias_or_id].get("id")
    for info in BEDROCK_MODELS.values():
        if info.get("id") == alias_or_id:
            return alias_or_id
    return None


def get_model_info(alias_or_id: str) -> dict[str, Any] | None:
    if alias_or_id in BEDROCK_MODELS:
        return BEDROCK_MODELS[alias_or_id]
    for info in BEDROCK_MODELS.values():
        if info.get("id") == alias_or_id:
            return info
    return None


def list_available_models() -> list[dict[str, Any]]:
    return [
        {"alias": alias, **info}
        for alias, info in BEDROCK_MODELS.items()
        if info.get("available", False)
    ]


def supports_tool_use(model_id: str) -> bool:
    info = get_model_info(model_id)
    return bool(info and info.get("tool_use"))


def supports_web_search(model_id: str) -> bool:
    info = get_model_info(model_id)
    return bool(info and info.get("web_search"))


def get_default_nova_id() -> str:
    return BEDROCK_MODELS["nova-pro"]["id"]
