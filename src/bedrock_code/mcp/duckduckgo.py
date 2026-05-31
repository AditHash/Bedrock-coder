from __future__ import annotations

from bedrock_code.mcp.manager import MCPManager

SERVER_NAME = "duckduckgo"
DEFAULT_PACKAGE = "mcp-server-duckduckgo"


class DuckDuckGoMCP:
    """On-demand DuckDuckGo web search via uvx MCP server."""

    def __init__(self, manager: MCPManager, package: str = DEFAULT_PACKAGE) -> None:
        self._manager = manager
        self._package = package

    async def ensure_running(self) -> None:
        if not self._manager.is_running(SERVER_NAME):
            await self._manager.start(
                name=SERVER_NAME,
                command="uvx",
                args=[self._package],
            )

    async def search(self, query: str) -> str:
        await self.ensure_running()
        conn = self._manager.get(SERVER_NAME)
        if conn is None:
            return "DuckDuckGo MCP server failed to start."
        # Try common tool names the duckduckgo MCP server might expose
        for tool_name in ("duckduckgo_search", "search", "web_search"):
            tool_names = [
                (t["name"] if isinstance(t, dict) else t.name)
                for t in conn.tools
            ]
            if tool_name in tool_names:
                return await conn.call_tool(tool_name, {"query": query})
        # Fallback: use first available tool
        if conn.tools:
            first = conn.tools[0]
            name = first["name"] if isinstance(first, dict) else first.name
            return await conn.call_tool(name, {"query": query})
        return "DuckDuckGo MCP server has no tools available."

    async def stop(self) -> None:
        await self._manager.stop(SERVER_NAME)
