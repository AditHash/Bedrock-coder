from __future__ import annotations

import asyncio

_bedrock_client: object | None = None
_nova_model_id: str = ""


def init_web_search(bedrock_client: object, nova_model_id: str) -> None:
    global _bedrock_client, _nova_model_id
    _bedrock_client = bedrock_client
    _nova_model_id = nova_model_id


async def web_search(query: str) -> str:
    """Search the web. Uses Nova Pro as a search agent; falls back to DuckDuckGo."""
    if _bedrock_client and _nova_model_id:
        try:
            return await _nova_search(query, _bedrock_client, _nova_model_id)
        except Exception:
            pass
    return await _ddg_search(query)


async def _nova_search(query: str, client: object, nova_model_id: str) -> str:
    """Spin up Nova Pro as a web-search sub-agent via Bedrock converse (two-turn exchange)."""
    loop = asyncio.get_event_loop()

    tool_config = {
        "tools": [{
            "toolSpec": {
                "name": "web_search",
                "description": "Search the internet for current information",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "The search query",
                            }
                        },
                        "required": ["search_query"],
                    }
                },
            }
        }]
    }
    system = [{
        "text": (
            "You are a web search assistant. Search the web for the user's query and "
            "return a clear, accurate, well-sourced summary of the results."
        )
    }]
    messages: list[dict] = [{"role": "user", "content": [{"text": query}]}]
    bedrock = client  # type: ignore[assignment]

    def _call(msgs: list[dict]) -> dict:
        return bedrock._client.converse(  # type: ignore[attr-defined]
            modelId=nova_model_id,
            messages=msgs,
            system=system,
            toolConfig=tool_config,
            inferenceConfig={"maxTokens": 4096},
        )

    resp = await loop.run_in_executor(None, _call, messages)

    if resp["stopReason"] == "tool_use":
        assistant_msg = resp["output"]["message"]
        messages.append(assistant_msg)

        tool_results = []
        for block in assistant_msg.get("content", []):
            if "toolUse" in block:
                tu = block["toolUse"]
                # Empty content — Bedrock/Nova runs the search server-side
                tool_results.append({
                    "toolUseId": tu["toolUseId"],
                    "content": [{"text": ""}],
                })

        if tool_results:
            messages.append({
                "role": "user",
                "content": [{"toolResult": r} for r in tool_results],
            })
            resp = await loop.run_in_executor(None, _call, messages)

    return "".join(
        b.get("text", "")
        for b in resp["output"]["message"].get("content", [])
        if "text" in b
    )


async def _ddg_search(query: str, max_results: int = 8) -> str:
    """Fallback: DuckDuckGo via duckduckgo-search Python package (no subprocess)."""
    try:
        from duckduckgo_search import DDGS  # noqa: PLC0415
    except ImportError:
        return (
            "Web search unavailable: reinstall with `uv tool install -e . --reinstall`"
        )
    try:
        results: list[dict] = await asyncio.to_thread(
            lambda: list(DDGS().text(query, max_results=max_results))
        )
    except Exception as e:
        return f"DuckDuckGo search error: {e}"

    if not results:
        return f"No results found for: {query!r}"

    lines: list[str] = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "(no title)")
        url = r.get("href", "")
        body = r.get("body", "")
        lines.append(f"[{i}] **{title}**\n{url}\n{body}")
    return "\n\n".join(lines)


def register_web_search_tool(
    registry: object,
    bedrock_client: object | None = None,
    nova_model_id: str = "",
) -> None:
    from bedrock_code.tools.registry import ToolSpec

    if bedrock_client:
        init_web_search(bedrock_client, nova_model_id)

    registry.register(ToolSpec(
        name="web_search",
        description=(
            "Search the web for current information. "
            "Use for recent events, news, documentation, library versions, "
            "pricing, or any question requiring up-to-date data."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query — be specific for best results",
                },
            },
            "required": ["query"],
        },
        handler=web_search,
        requires_permission=False,
    ))
