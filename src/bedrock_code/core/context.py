from __future__ import annotations

from typing import Any

from bedrock_code.models.schemas import TokenUsage


class ConversationContext:
    def __init__(self, context_window: int = 200_000, budget_ratio: float = 0.85) -> None:
        self._messages: list[dict[str, Any]] = []
        self._context_window = context_window
        self._budget = int(context_window * budget_ratio)
        self.session_usage = TokenUsage()
        self.session_cost = 0.0
        self._turn_count = 0

    def append(self, message: dict[str, Any]) -> None:
        self._messages.append(message)

    def messages(self) -> list[dict[str, Any]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()
        self._turn_count = 0

    def update_usage(self, usage: TokenUsage, cost: float = 0.0) -> None:
        self.session_usage = self.session_usage.add(usage)
        self.session_cost += cost
        self._turn_count += 1

    def should_compact(self, estimated_tokens: int) -> bool:
        return estimated_tokens > self._budget

    def compact_summary_message(self, summary: str) -> None:
        """Replace full history with a summary message."""
        self._messages = [
            {
                "role": "user",
                "content": [{"text": f"[Previous conversation summary]\n\n{summary}"}],
            }
        ]

    def build_user_message(self, text: str, attachments: list[str] | None = None) -> dict[str, Any]:
        content: list[dict[str, Any]] = []
        if attachments:
            for attachment in attachments:
                content.append({"text": f"[Attached file content]\n{attachment}"})
        content.append({"text": text})
        return {"role": "user", "content": content}

    @staticmethod
    def build_assistant_message(
        text_parts: list[str],
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        content: list[dict[str, Any]] = []
        full_text = "".join(text_parts)
        if full_text:
            content.append({"text": full_text})
        for tc in tool_calls or []:
            content.append({
                "toolUse": {
                    "toolUseId": tc["id"],
                    "name": tc["name"],
                    "input": tc["input"],
                }
            })
        return {"role": "assistant", "content": content}

    @staticmethod
    def build_tool_results_message(results: list[dict[str, Any]]) -> dict[str, Any]:
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
