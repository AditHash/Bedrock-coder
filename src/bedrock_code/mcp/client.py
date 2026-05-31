from __future__ import annotations

from typing import Any


class MCPConnection:
    """Represents an active connection to an MCP server."""

    def __init__(self, name: str, session: Any, tools: list[dict]) -> None:
        self.name = name
        self.session = session
        self.tools = tools  # list of tool dicts from list_tools()

    def bedrock_tool_specs(self) -> list[dict[str, Any]]:
        """Convert MCP tool list to Bedrock toolSpec format, namespaced by server name."""
        specs = []
        for tool in self.tools:
            t = tool if isinstance(tool, dict) else tool.__dict__
            spec = {
                "name": f"{self.name}__{t.get('name', 'unknown')}",
                "description": t.get("description", ""),
                "inputSchema": {"json": t.get("inputSchema", {"type": "object", "properties": {}})},
            }
            specs.append(spec)
        return specs

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        try:
            result = await self.session.call_tool(tool_name, arguments)
            if hasattr(result, "content"):
                parts = []
                for block in result.content:
                    if hasattr(block, "text"):
                        parts.append(block.text)
                    else:
                        parts.append(str(block))
                return "\n".join(parts)
            return str(result)
        except Exception as e:
            return f"MCP tool error: {e}"
