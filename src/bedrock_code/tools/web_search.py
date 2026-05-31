from __future__ import annotations

import asyncio
import re
import warnings

_bedrock_client: object | None = None
_nova_model_id: str = ""


def init_web_search(bedrock_client: object, nova_model_id: str) -> None:
    global _bedrock_client, _nova_model_id
    _bedrock_client = bedrock_client
    _nova_model_id = nova_model_id


async def web_search(query: str) -> str:
    """Search the web.

    Pipeline:
    1. ddgs (DuckDuckGo) for real-time results
    2. Nova Pro synthesizes the snippets into a clean answer (optional)
    Falls back to raw DDG output if Nova is unavailable or fails.
    """
    raw = await _ddg_search(query)

    if (
        _bedrock_client
        and _nova_model_id
        and raw
        and not raw.startswith("No results")
        and not raw.startswith("DuckDuckGo")
        and not raw.startswith("Web search unavailable")
    ):
        try:
            synthesized = await _nova_synthesize(query, raw, _bedrock_client, _nova_model_id)
            if synthesized:
                return synthesized
        except Exception:
            pass

    return raw


def _run_ddg(query: str, max_results: int) -> list[dict]:
    """Run DuckDuckGo search synchronously (called in a thread)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        # Try new package name (ddgs) first, fall back to duckduckgo_search
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS  # type: ignore[no-redef]

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(r)
    return results


async def _ddg_search(query: str, max_results: int = 8) -> str:
    try:
        results: list[dict] = await asyncio.to_thread(_run_ddg, query, max_results)
    except ImportError:
        return "Web search unavailable: run `uv tool install -e . --reinstall` to get ddgs"
    except Exception as e:
        return f"DuckDuckGo search error: {e}"

    if not results:
        return f"No results found for: {query!r}"

    lines: list[str] = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "(no title)")
        url = r.get("href", "")
        body = r.get("body", "")
        lines.append(f"[{i}] {title}\n{url}\n{body}")
    return "\n\n".join(lines)


async def _nova_synthesize(
    query: str, raw_results: str, client: object, nova_model_id: str
) -> str:
    """Use Nova Pro to synthesize raw DDG snippets into a clean answer."""
    loop = asyncio.get_event_loop()

    system = [{
        "text": (
            "You are a search result analyst. Given a user query and raw search snippets, "
            "produce a concise, accurate, well-organized answer. "
            "Cite relevant URLs inline. Do not pad with filler. "
            "Only output the final answer — no thinking, no reasoning steps."
        )
    }]
    prompt = (
        f"Query: {query}\n\n"
        f"Search results:\n{raw_results}\n\n"
        "Summarize the key findings into a clear answer with sources."
    )

    def _call() -> dict:
        return client._client.converse(  # type: ignore[attr-defined]
            modelId=nova_model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            system=system,
            inferenceConfig={"maxTokens": 2048, "temperature": 0.1},
        )

    resp = await loop.run_in_executor(None, _call)
    text = "".join(
        b.get("text", "")
        for b in resp["output"]["message"].get("content", [])
        if "text" in b
    )
    # Strip <thinking>...</thinking> blocks that extended-reasoning models emit
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL).strip()
    return text


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
            "pricing, sports scores, or any question requiring up-to-date data."
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
