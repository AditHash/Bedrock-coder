from __future__ import annotations

import json
from typing import Any

from rich.columns import Columns
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text


def render_markdown(text: str) -> Markdown:
    return Markdown(text, code_theme="one-dark")


def render_streaming_text(text: str) -> Markdown:
    return Markdown(text + "▌", code_theme="one-dark")


def render_tool_call(name: str, inputs: dict[str, Any]) -> Panel:
    header = Text()
    header.append("⚙ Tool: ", style="dim")
    header.append(name, style="bc.tool_name")

    if inputs:
        try:
            body = json.dumps(inputs, indent=2, ensure_ascii=False)
            content = Syntax(body, "json", theme="one-dark", word_wrap=True)
        except Exception:
            content = Text(str(inputs), style="bc.tool_input")
    else:
        content = Text("(no inputs)", style="dim")

    return Panel(
        Group(header, content),
        border_style="yellow",
        padding=(0, 1),
        expand=False,
    )


def render_tool_result(name: str, result: str, is_error: bool = False) -> Panel:
    style = "bc.tool_error" if is_error else "bc.tool_result"
    border = "red" if is_error else "green"
    icon = "✗" if is_error else "✓"

    truncated = result
    if len(result) > 2000:
        truncated = result[:1000] + f"\n... [{len(result) - 1000} chars truncated] ...\n" + result[-200:]

    return Panel(
        Text(truncated, style=style),
        title=Text(f"{icon} {name}", style=style),
        border_style=border,
        padding=(0, 1),
        expand=False,
    )


def render_diff(diff_text: str, filename: str = "") -> Panel:
    if not diff_text.strip():
        return Panel(Text("(no changes)", style="dim"), border_style="dim")
    return Panel(
        Syntax(diff_text, "diff", theme="one-dark", word_wrap=False, line_numbers=False),
        title=f"[bc.diff_header]Diff: {filename}" if filename else "[bc.diff_header]Diff",
        border_style="cyan",
        padding=(0, 1),
    )


def render_permission_ask(tool_name: str, inputs: dict[str, Any]) -> Panel:
    header = Text()
    header.append("⚠ Permission required\n", style="bc.permission_ask bold")
    header.append(f"Tool: ", style="dim")
    header.append(tool_name, style="bc.tool_name")

    if inputs:
        try:
            body = json.dumps(inputs, indent=2, ensure_ascii=False)
            content_syn = Syntax(body, "json", theme="one-dark", word_wrap=True)
            content: Any = Group(header, content_syn)
        except Exception:
            content = Group(header, Text(str(inputs)))
    else:
        content = header

    return Panel(
        content,
        border_style="yellow",
        title="[bc.permission_ask]Allow this action? [y/N]",
        padding=(0, 1),
    )


def render_cost_line(input_tokens: int, output_tokens: int, cost: float) -> Text:
    t = Text()
    t.append(" ↑", style="dim blue")
    t.append(f"{input_tokens:,}", style="bc.tokens")
    t.append(" ↓", style="dim blue")
    t.append(f"{output_tokens:,}", style="bc.tokens")
    t.append("  $", style="dim")
    t.append(f"{cost:.5f}", style="bc.cost")
    return t


def render_model_badge(display_name: str, provider: str = "") -> Text:
    t = Text()
    t.append(f" {display_name} ", style="bc.model_badge")
    return t
