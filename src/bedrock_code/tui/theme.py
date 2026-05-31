from __future__ import annotations

from rich.theme import Theme


DARK_THEME = Theme({
    "bc.prompt": "bold cyan",
    "bc.model_badge": "bold white on dark_cyan",
    "bc.tool_name": "bold yellow",
    "bc.tool_input": "dim white",
    "bc.tool_result": "dim green",
    "bc.tool_error": "bold red",
    "bc.cost": "dim cyan",
    "bc.tokens": "dim blue",
    "bc.permission_ask": "bold yellow",
    "bc.permission_deny": "bold red",
    "bc.permission_allow": "bold green",
    "bc.info": "dim white",
    "bc.success": "bold green",
    "bc.error": "bold red",
    "bc.warning": "bold yellow",
    "bc.header": "bold cyan",
    "bc.separator": "dim white",
    "bc.diff_add": "green",
    "bc.diff_remove": "red",
    "bc.diff_header": "cyan",
    "bc.provider_anthropic": "bold #FF6B35",
    "bc.provider_amazon": "bold #FF9900",
    "bc.provider_mistral": "bold #7C3AED",
    "bc.provider_meta": "bold #0078FF",
    "bc.provider_cohere": "bold #39D353",
})

LIGHT_THEME = Theme({
    "bc.prompt": "bold blue",
    "bc.model_badge": "bold black on cyan",
    "bc.tool_name": "bold yellow",
    "bc.tool_input": "bright_black",
    "bc.tool_result": "green",
    "bc.tool_error": "bold red",
    "bc.cost": "cyan",
    "bc.tokens": "blue",
    "bc.permission_ask": "bold yellow",
    "bc.permission_deny": "bold red",
    "bc.permission_allow": "bold green",
    "bc.info": "bright_black",
    "bc.success": "bold green",
    "bc.error": "bold red",
    "bc.warning": "bold yellow",
    "bc.header": "bold blue",
    "bc.separator": "bright_black",
})


def get_theme(name: str) -> Theme:
    return LIGHT_THEME if name == "light" else DARK_THEME
