from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

import boto3
from botocore.exceptions import ClientError

from bedrock_code.models.schemas import (
    StreamDone,
    StreamEvent,
    TextChunk,
    TokenUsage,
    ToolCall,
    ToolCallReady,
    ToolInputChunk,
    ToolStartEvent,
)


class BedrockClient:
    def __init__(self, region: str = "ap-south-1", profile: str | None = None) -> None:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self._session = session
        self._region = region
        self._client = session.client("bedrock-runtime", region_name=region)
        self._regional_clients: dict[str, Any] = {region: self._client}

    def _client_for_region(self, region: str) -> Any:
        if region not in self._regional_clients:
            self._regional_clients[region] = self._session.client(
                "bedrock-runtime", region_name=region
            )
        return self._regional_clients[region]

    async def converse_stream(
        self,
        model_id: str,
        messages: list[dict[str, Any]],
        system_prompt: str,
        tool_config: dict[str, Any] | None = None,
        max_tokens: int = 8192,
        temperature: float = 0.0,
        region_override: str | None = None,
    ) -> AsyncGenerator[StreamEvent, None]:
        client = self._client_for_region(region_override) if region_override else self._client
        kwargs: dict[str, Any] = {
            "modelId": model_id,
            "messages": messages,
            "system": [{"text": system_prompt}],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
            },
        }
        if tool_config:
            kwargs["toolConfig"] = tool_config

        try:
            response = client.converse_stream(**kwargs)
        except ClientError as e:
            raise BedrockError(str(e)) from e

        return self._parse_stream(response["stream"])

    async def _parse_stream(
        self, event_stream: Any
    ) -> AsyncGenerator[StreamEvent, None]:
        import asyncio

        tool_input_buffers: dict[str, str] = {}
        tool_names: dict[str, str] = {}
        current_tool_id: str | None = None
        usage = TokenUsage()
        stop_reason = "end_turn"
        pending_done = False

        # boto3 EventStream is synchronous; iterate in thread to avoid blocking event loop
        loop = asyncio.get_event_loop()
        events: list[Any] = await loop.run_in_executor(None, list, event_stream)

        for event in events:
            if "contentBlockStart" in event:
                block_start = event["contentBlockStart"]["start"]
                if "toolUse" in block_start:
                    tool_use = block_start["toolUse"]
                    tool_id = tool_use["toolUseId"]
                    tool_name = tool_use["name"]
                    current_tool_id = tool_id
                    tool_input_buffers[tool_id] = ""
                    tool_names[tool_id] = tool_name
                    yield ToolStartEvent(tool_id, tool_name)

            elif "contentBlockDelta" in event:
                delta = event["contentBlockDelta"]["delta"]
                if "text" in delta:
                    yield TextChunk(delta["text"])
                elif "toolUse" in delta and current_tool_id:
                    partial = delta["toolUse"].get("input", "")
                    tool_input_buffers[current_tool_id] += partial
                    yield ToolInputChunk(current_tool_id, partial)

            elif "contentBlockStop" in event:
                if current_tool_id and current_tool_id in tool_input_buffers:
                    raw = tool_input_buffers.pop(current_tool_id)
                    name = tool_names.pop(current_tool_id, "unknown")
                    try:
                        parsed_input = json.loads(raw) if raw else {}
                    except json.JSONDecodeError:
                        parsed_input = {"raw": raw}
                    yield ToolCallReady(ToolCall(id=current_tool_id, name=name, input=parsed_input))
                    current_tool_id = None

            elif "messageStop" in event:
                stop_reason = event["messageStop"].get("stopReason", "end_turn")
                pending_done = True

            elif "metadata" in event:
                meta = event["metadata"]
                if "usage" in meta:
                    u = meta["usage"]
                    usage = TokenUsage(
                        input_tokens=u.get("inputTokens", 0),
                        output_tokens=u.get("outputTokens", 0),
                        cache_read_tokens=u.get("cacheReadInputTokens", 0),
                        cache_write_tokens=u.get("cacheWriteInputTokens", 0),
                    )

            elif any(
                k in event
                for k in (
                    "internalServerException",
                    "modelStreamErrorException",
                    "validationException",
                    "throttlingException",
                    "serviceUnavailableException",
                )
            ):
                for key in event:
                    raise BedrockError(f"{key}: {event[key].get('message', str(event[key]))}")

        if pending_done:
            yield StreamDone(stop_reason=stop_reason, usage=usage)

    def verify_credentials(self) -> dict[str, str]:
        sts = self._session.client("sts", region_name=self._region)
        return sts.get_caller_identity()


class BedrockError(Exception):
    pass


def build_tool_config(tool_specs: list[dict[str, Any]]) -> dict[str, Any]:
    return {"tools": [{"toolSpec": spec} for spec in tool_specs]}


def build_tool_result_message(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "role": "user",
        "content": [
            {
                "toolResult": {
                    "toolUseId": r["tool_use_id"],
                    "content": [{"text": r["content"]}],
                    **({"status": "error"} if r.get("status") == "error" else {}),
                }
            }
            for r in results
        ],
    }
