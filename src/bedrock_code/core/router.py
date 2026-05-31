from __future__ import annotations

from bedrock_code.models.registry import supports_web_search


WEB_SEARCH_KEYWORDS = [
    "search the web", "search web", "look up", "look it up",
    "find online", "google", "what is the latest", "current price",
    "news about", "recent", "today", "right now", "up to date",
]


class ModelRouter:
    def __init__(self, config: object) -> None:
        self._config = config

    def select_model(self, model_id: str, message: str, tool_names: list[str]) -> str:
        strategy = self._config.web_search_strategy

        # Only route based on message content — checking if 'web_search' is in tool_names
        # would always be True since the tool is always registered, causing every query
        # to hit Nova regardless of whether web search is actually needed.
        needs_web = self._message_needs_web_search(message)

        if needs_web and strategy == "nova_first":
            nova_id = self._config.nova_model_id
            if supports_web_search(nova_id):
                return nova_id

        return model_id

    def _message_needs_web_search(self, message: str) -> bool:
        lower = message.lower()
        return any(kw in lower for kw in WEB_SEARCH_KEYWORDS)

    def should_use_duckduckgo(self, model_id: str) -> bool:
        strategy = self._config.web_search_strategy
        if strategy == "duckduckgo_only":
            return True
        if strategy == "nova_first" and not supports_web_search(model_id):
            return True
        return False
