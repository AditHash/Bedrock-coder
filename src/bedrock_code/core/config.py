from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import tomli_w

CONFIG_DIR = Path.home() / ".bedrock-code"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG: dict[str, Any] = {
    "core": {
        "default_model": "global.anthropic.claude-sonnet-4-6",
        "theme": "dark",
        "max_tokens": 8192,
        "temperature": 0.0,
        "context_window_budget": 0.85,
        "memory_file": "MEMORY.md",
    },
    "aws": {
        "region": "ap-south-1",
        "profile": None,
    },
    "permissions": {
        "read_file": "allow",
        "list_directory": "allow",
        "search_files": "allow",
        "grep_files": "allow",
        "git_status": "allow",
        "git_diff": "allow",
        "git_log": "allow",
        "todo_read": "allow",
        "todo_write": "allow",
        "todo_update": "allow",
        "web_search": "allow",
        "bash_exec": "ask",
        "write_file": "ask",
        "edit_file": "ask",
        "git_commit": "ask",
        "git_add": "ask",
        "safe_commands": [
            "ls", "cat", "head", "tail", "grep", "find", "pwd", "echo", "which",
            "git status", "git diff", "git log", "git show", "git branch",
            "python --version", "python3 --version", "node --version",
            "pip list", "pip show", "rg", "fd",
        ],
    },
    "web_search": {
        "strategy": "nova_first",
        "nova_model": "apac.amazon.nova-pro-v1:0",  # APAC cross-region inference, no region override needed
        "duckduckgo_package": "mcp-server-duckduckgo",
    },
    "mcp": {
        "servers": {},
    },
    "ui": {
        "show_token_count": True,
        "show_cost": True,
        "compact_mode": False,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def get(self, *keys: str, default: Any = None) -> Any:
        d = self._data
        for k in keys:
            if not isinstance(d, dict) or k not in d:
                return default
            d = d[k]
        return d

    def set(self, *keys: str, value: Any) -> None:
        d = self._data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    @property
    def default_model(self) -> str:
        return self.get("core", "default_model", default=DEFAULT_CONFIG["core"]["default_model"])

    @property
    def aws_region(self) -> str:
        return self.get("aws", "region", default="us-east-1")

    @property
    def aws_profile(self) -> str | None:
        return self.get("aws", "profile", default=None)

    @property
    def max_tokens(self) -> int:
        return self.get("core", "max_tokens", default=8192)

    @property
    def temperature(self) -> float:
        return self.get("core", "temperature", default=0.0)

    @property
    def theme(self) -> str:
        return self.get("core", "theme", default="dark")

    @property
    def show_cost(self) -> bool:
        return self.get("ui", "show_cost", default=True)

    @property
    def show_token_count(self) -> bool:
        return self.get("ui", "show_token_count", default=True)

    @property
    def web_search_strategy(self) -> str:
        return self.get("web_search", "strategy", default="nova_first")

    @property
    def nova_model_id(self) -> str:
        return self.get("web_search", "nova_model", default="apac.amazon.nova-pro-v1:0")

    @property
    def duckduckgo_package(self) -> str:
        return self.get("web_search", "duckduckgo_package", default="mcp-server-duckduckgo")

    def permission_for(self, tool_name: str) -> str:
        return self.get("permissions", tool_name, default="ask")

    def safe_commands(self) -> list[str]:
        return self.get("permissions", "safe_commands", default=[])

    def raw(self) -> dict[str, Any]:
        return self._data

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_bytes(tomli_w.dumps(_strip_none(self._data)).encode())


def _strip_none(obj: Any) -> Any:
    """Recursively remove None values — TOML doesn't support null."""
    if isinstance(obj, dict):
        return {k: _strip_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_none(v) for v in obj if v is not None]
    return obj


def load_config() -> Config:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            user_data = tomllib.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            merged = _deep_merge(DEFAULT_CONFIG, user_data)
            return Config(merged)
        except Exception:
            pass
    config = Config(_deep_merge({}, DEFAULT_CONFIG))
    config.save()
    return config
