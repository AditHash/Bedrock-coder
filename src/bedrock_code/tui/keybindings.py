from __future__ import annotations

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys


def build_keybindings() -> KeyBindings:
    kb = KeyBindings()

    @kb.add("c-l")
    def _clear_screen(event):
        event.app.renderer.clear()

    # Alt+Enter — insert newline for multi-line input (works cross-platform)
    @kb.add("escape", "enter")
    def _newline(event):
        event.current_buffer.insert_text("\n")

    # c-j is Ctrl+J (same bytes as Enter on some terminals) — also insert newline
    @kb.add("c-j")
    def _newline_ctrl_j(event):
        event.current_buffer.insert_text("\n")

    @kb.add("c-k")
    def _clear_line(event):
        buf = event.current_buffer
        buf.delete_before_cursor(count=len(buf.document.current_line_before_cursor))

    return kb
