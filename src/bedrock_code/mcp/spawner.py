from __future__ import annotations

import asyncio
import contextlib
from typing import Any

from bedrock_code.mcp.client import MCPConnection


class MCPSpawner:
    """Spawns MCP servers as subprocesses using stdio transport."""

    async def spawn(
        self,
        name: str,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
    ) -> MCPConnection:
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError as e:
            raise RuntimeError(
                "The 'mcp' package is required for MCP server support. "
                "Install it with: pip install mcp"
            ) from e

        params = StdioServerParameters(command=command, args=args, env=env)

        # We need to keep the context managers alive for the lifetime of the connection.
        # Store the exit stack on the connection object.
        stack = contextlib.AsyncExitStack()
        try:
            read, write = await stack.enter_async_context(stdio_client(params))
            session: ClientSession = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            tools_response = await session.list_tools()
            tools = tools_response.tools if hasattr(tools_response, "tools") else []
        except Exception:
            await stack.aclose()
            raise

        conn = MCPConnection(name=name, session=session, tools=tools)
        conn._stack = stack  # type: ignore[attr-defined]
        return conn

    async def close(self, conn: MCPConnection) -> None:
        stack = getattr(conn, "_stack", None)
        if stack:
            await stack.aclose()
