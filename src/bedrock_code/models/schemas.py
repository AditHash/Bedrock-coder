from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ToolCall(BaseModel):
    id: str
    name: str
    input: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    tool_use_id: str
    content: str
    status: Literal["success", "error"] = "success"


class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0

    def add(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_read_tokens=self.cache_read_tokens + other.cache_read_tokens,
            cache_write_tokens=self.cache_write_tokens + other.cache_write_tokens,
        )

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens


class StreamEvent:
    pass


class TextChunk(StreamEvent):
    def __init__(self, text: str) -> None:
        self.text = text


class ToolStartEvent(StreamEvent):
    def __init__(self, tool_use_id: str, name: str) -> None:
        self.tool_use_id = tool_use_id
        self.name = name


class ToolInputChunk(StreamEvent):
    def __init__(self, tool_use_id: str, partial: str) -> None:
        self.tool_use_id = tool_use_id
        self.partial = partial


class ToolCallReady(StreamEvent):
    def __init__(self, tool_call: ToolCall) -> None:
        self.tool_call = tool_call


class ToolResultEvent(StreamEvent):
    def __init__(self, tool_call: ToolCall, result: ToolResult) -> None:
        self.tool_call = tool_call
        self.result = result


class StreamDone(StreamEvent):
    def __init__(self, stop_reason: str, usage: TokenUsage) -> None:
        self.stop_reason = stop_reason
        self.usage = usage
