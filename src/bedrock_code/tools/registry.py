from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

ToolHandler = Callable[..., Awaitable[str]]


class ToolSpec:
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: ToolHandler,
        requires_permission: bool = True,
    ) -> None:
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler
        self.requires_permission = requires_permission

    def to_bedrock_spec(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {"json": self.input_schema},
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def all(self) -> list[ToolSpec]:
        return list(self._tools.values())

    def bedrock_tool_config(self) -> dict[str, Any]:
        return {
            "tools": [
                {"toolSpec": spec.to_bedrock_spec()} for spec in self._tools.values()
            ]
        }

    async def execute(self, name: str, inputs: dict[str, Any]) -> str:
        spec = self._tools.get(name)
        if spec is None:
            return f"Unknown tool: {name}"
        try:
            return await spec.handler(**inputs)
        except Exception as e:
            return f"Tool error: {e}"
