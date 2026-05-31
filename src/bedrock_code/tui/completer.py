from __future__ import annotations

import os
from pathlib import Path

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document


SLASH_COMMANDS = [
    "/help",
    "/clear",
    "/model",
    "/tools",
    "/config",
    "/memory",
    "/cost",
    "/compact",
    "/quit",
    "/exit",
]


class BedrockCompleter(Completer):
    def get_completions(self, document: Document, complete_event: CompleteEvent):
        text = document.text_before_cursor
        word = document.get_word_before_cursor(WORD=True)

        # Slash command completion
        if text.startswith("/"):
            for cmd in SLASH_COMMANDS:
                if cmd.startswith(text):
                    yield Completion(cmd[len(text):], start_position=0, display=cmd)
            return

        # @file completion
        if "@" in text:
            at_idx = text.rfind("@")
            partial_path = text[at_idx + 1:]
            yield from self._complete_path(partial_path, at_idx)
            return

    def _complete_path(self, partial: str, at_idx: int):
        directory = Path(".") if "/" not in partial and "\\" not in partial else Path(partial).parent
        prefix = Path(partial).name if partial else ""
        try:
            entries = sorted(directory.iterdir())
        except (OSError, PermissionError):
            return
        for entry in entries:
            if entry.name.startswith("."):
                continue
            if entry.name.lower().startswith(prefix.lower()):
                suffix = "/" if entry.is_dir() else ""
                display = entry.name + suffix
                completion_text = str(entry)[len(partial):]
                yield Completion(completion_text, start_position=0, display=display)
