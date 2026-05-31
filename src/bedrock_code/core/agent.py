from __future__ import annotations

import os
import platform
from collections.abc import AsyncGenerator
from typing import Any, Callable

from bedrock_code.core.context import ConversationContext
from bedrock_code.core.memory import build_system_prompt, load_memory
from bedrock_code.core.permissions import PermissionManager
from bedrock_code.core.router import ModelRouter
from bedrock_code.mcp.duckduckgo import DuckDuckGoMCP
from bedrock_code.mcp.manager import MCPManager
from bedrock_code.models.bedrock import BedrockClient
from bedrock_code.models.schemas import (
    StreamDone,
    StreamEvent,
    TextChunk,
    ToolCallReady,
    ToolResult,
    ToolResultEvent,
    ToolStartEvent,
)
from bedrock_code.tools.registry import ToolRegistry
from bedrock_code.utils.cost import calculate_cost


class AgentLoop:
    def __init__(
        self,
        config: Any,
        bedrock: BedrockClient,
        tool_registry: ToolRegistry,
        mcp_manager: MCPManager,
        permissions: PermissionManager,
        router: ModelRouter,
        context: ConversationContext,
        ddg: DuckDuckGoMCP,
    ) -> None:
        self._config = config
        self._bedrock = bedrock
        self._tools = tool_registry
        self._mcp = mcp_manager
        self._permissions = permissions
        self._router = router
        self._context = context
        self._ddg = ddg
        self._model_id = config.default_model
        self._auto_mode: bool = config.get("core", "auto_model", default=False)
        self._on_tool_ask: Callable[[str, dict], bool] | None = None
        self._memory = load_memory(project_dir=_cwd())

    def set_model(self, model_id: str) -> None:
        self._model_id = model_id

    def get_model(self) -> str:
        return self._model_id

    def set_tool_ask_callback(self, cb: Callable[[str, dict], bool]) -> None:
        self._on_tool_ask = cb
        self._permissions.set_ask_callback(cb)

    async def run(self, user_message: str) -> AsyncGenerator[StreamEvent, None]:
        user_msg = self._context.build_user_message(user_message)
        self._context.append(user_msg)

        while True:
            system_prompt = self._build_system_prompt()
            model_id = self._router.select_model(
                self._model_id, user_message, list(self._tools._tools.keys())
            )

            tool_config = self._build_tool_config(model_id)

            text_parts: list[str] = []
            pending_tools: dict[str, dict[str, Any]] = {}
            tool_order: list[str] = []
            stop_reason = "end_turn"
            last_usage = None

            # Nova web-search model may live in a different region (e.g. us-east-1)
            nova_id = self._config.nova_model_id
            region_override = (
                self._config.get("web_search", "nova_region", default=None)
                if model_id == nova_id
                else None
            )

            stream = await self._bedrock.converse_stream(
                model_id=model_id,
                messages=self._context.messages(),
                system_prompt=system_prompt,
                tool_config=tool_config if tool_config["tools"] else None,
                max_tokens=self._config.max_tokens,
                temperature=self._config.temperature,
                region_override=region_override,
            )

            async for event in stream:
                if isinstance(event, TextChunk):
                    text_parts.append(event.text)
                    yield event

                elif isinstance(event, ToolStartEvent):
                    pending_tools[event.tool_use_id] = {"id": event.tool_use_id, "name": event.name}
                    tool_order.append(event.tool_use_id)
                    yield event

                elif isinstance(event, ToolCallReady):
                    tc = event.tool_call
                    pending_tools[tc.id] = {"id": tc.id, "name": tc.name, "input": tc.input}
                    yield event

                elif isinstance(event, StreamDone):
                    stop_reason = event.stop_reason
                    last_usage = event.usage
                    break

            # Save assistant message with tool calls
            tool_call_list = [pending_tools[tid] for tid in tool_order if tid in pending_tools]
            assistant_msg = self._context.build_assistant_message(text_parts, tool_call_list)
            self._context.append(assistant_msg)

            if stop_reason != "tool_use" or not tool_call_list:
                if last_usage:
                    cost = calculate_cost(model_id, last_usage)
                    self._context.update_usage(last_usage, cost)
                break

            # Execute tool calls
            tool_results: list[dict[str, Any]] = []
            for tc_dict in tool_call_list:
                tc_id = tc_dict["id"]
                tc_name = tc_dict["name"]
                tc_input = tc_dict.get("input", {})

                result = await self._execute_tool(tc_name, tc_input)
                tool_results.append({
                    "tool_use_id": tc_id,
                    "content": result.content,
                    "status": result.status,
                })
                yield ToolResultEvent(
                    tool_call=type("TC", (), {"id": tc_id, "name": tc_name, "input": tc_input})(),
                    result=result,
                )

            results_msg = self._context.build_tool_results_message(tool_results)
            self._context.append(results_msg)

    async def _execute_tool(self, name: str, inputs: dict[str, Any]) -> ToolResult:
        # Check permissions
        tool_spec = self._tools.get(name)
        requires_perm = tool_spec.requires_permission if tool_spec else True

        if requires_perm:
            allowed = await self._permissions.request(name, inputs)
            if not allowed:
                return ToolResult(tool_use_id="", content="Permission denied by user.", status="error")

        # Check if it's an MCP namespaced tool (server__tool)
        if "__" in name:
            server_name, tool_name = name.split("__", 1)
            content = await self._mcp.call_tool(server_name, tool_name, inputs)
            return ToolResult(tool_use_id="", content=content)

        # Local tool
        content = await self._tools.execute(name, inputs)
        return ToolResult(tool_use_id="", content=content)

    def _build_system_prompt(self) -> str:
        git_info = _git_info()
        return build_system_prompt(
            memory=self._memory,
            cwd=str(_cwd()),
            model_id=self._model_id,
            git_info=git_info,
            platform=platform.system(),
        )

    def _build_tool_config(self, model_id: str) -> dict[str, Any]:
        from bedrock_code.models.registry import supports_tool_use

        if not supports_tool_use(model_id):
            return {"tools": []}

        specs = [s.to_bedrock_spec() for s in self._tools.all()]
        specs.extend(self._mcp.all_tool_specs())
        return {"tools": [{"toolSpec": s} for s in specs]}

    def reload_memory(self) -> None:
        self._memory = load_memory(project_dir=_cwd())


def _cwd() -> Any:
    return __import__("pathlib").Path(os.getcwd())


def _git_info() -> str:
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            return f"branch: {result.stdout.strip()}"
    except Exception:
        pass
    return "not a git repo"
