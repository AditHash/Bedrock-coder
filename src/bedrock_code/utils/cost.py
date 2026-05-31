from __future__ import annotations

from bedrock_code.models.schemas import TokenUsage


def calculate_cost(model_id: str, usage: TokenUsage) -> float:
    from bedrock_code.models.registry import BEDROCK_MODELS

    for model_info in BEDROCK_MODELS.values():
        if model_info.get("id") == model_id:
            input_cost = model_info.get("input_cost_per_1m", 0.0)
            output_cost = model_info.get("output_cost_per_1m", 0.0)
            total = (usage.input_tokens / 1_000_000) * input_cost
            total += (usage.output_tokens / 1_000_000) * output_cost
            return total
    return 0.0


def format_cost(cost: float) -> str:
    if cost < 0.001:
        return f"${cost * 1000:.4f}m"
    return f"${cost:.4f}"


def format_tokens(usage: TokenUsage) -> str:
    return f"↑{usage.input_tokens:,} ↓{usage.output_tokens:,}"
