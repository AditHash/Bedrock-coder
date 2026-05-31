# Slash command dispatcher — thin re-export; actual logic lives in tui/repl.py
# This module exists as an extension point for future plugin-style commands.

from __future__ import annotations

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
