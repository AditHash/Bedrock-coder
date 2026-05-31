from __future__ import annotations

from enum import Enum
from typing import Any, Callable


class Permission(str, Enum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


class PermissionManager:
    def __init__(self, config: Any) -> None:
        self._config = config
        self._session_allow: set[str] = set()
        self._ask_callback: Callable[[str, dict], bool] | None = None

    def set_ask_callback(self, callback: Callable[[str, dict], bool]) -> None:
        self._ask_callback = callback

    def session_allow(self, tool_name: str) -> None:
        self._session_allow.add(tool_name)

    def check_level(self, tool_name: str, tool_input: dict[str, Any]) -> Permission:
        if tool_name in self._session_allow:
            return Permission.ALLOW

        level_str = self._config.permission_for(tool_name)
        level = Permission(level_str) if level_str in Permission._value2member_map_ else Permission.ASK

        if level == Permission.ALLOW:
            return Permission.ALLOW
        if level == Permission.DENY:
            return Permission.DENY

        # ASK — auto-allow safe bash commands
        if tool_name == "bash_exec":
            cmd = tool_input.get("command", "")
            if self._is_safe_command(cmd):
                return Permission.ALLOW

        return Permission.ASK

    def _is_safe_command(self, command: str) -> bool:
        safe = self._config.safe_commands()
        cmd = command.strip()
        return any(cmd.startswith(prefix) for prefix in safe)

    async def request(self, tool_name: str, tool_input: dict[str, Any]) -> bool:
        level = self.check_level(tool_name, tool_input)
        if level == Permission.ALLOW:
            return True
        if level == Permission.DENY:
            return False
        if self._ask_callback:
            return self._ask_callback(tool_name, tool_input)
        return True
