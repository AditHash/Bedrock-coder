from __future__ import annotations

from typing import Any

from bedrock_code.mcp.client import MCPConnection
from bedrock_code.mcp.spawner import MCPSpawner


class MCPManager:
    """Manages the lifecycle of multiple MCP server connections."""

    def __init__(self) -> None:
        self._spawner = MCPSpawner()
        self._connections: dict[str, MCPConnection] = {}

    async def start(
        self,
        name: str,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
    ) -> MCPConnection:
        if name in self._connections:
            return self._connections[name]
        conn = await self._spawner.spawn(name=name, command=command, args=args, env=env)
        self._connections[name] = conn
        return conn

    async def stop(self, name: str) -> None:
        conn = self._connections.pop(name, None)
        if conn:
            await self._spawner.close(conn)

    async def stop_all(self) -> None:
        for name in list(self._connections):
            await self.stop(name)

    def get(self, name: str) -> MCPConnection | None:
        return self._connections.get(name)

    def is_running(self, name: str) -> bool:
        return name in self._connections

    def all_tool_specs(self) -> list[dict[str, Any]]:
        specs: list[dict[str, Any]] = []
        for conn in self._connections.values():
            specs.extend(conn.bedrock_tool_specs())
        return specs

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any]) -> str:
        conn = self._connections.get(server_name)
        if conn is None:
            return f"MCP server '{server_name}' is not running."
        return await conn.call_tool(tool_name, arguments)
