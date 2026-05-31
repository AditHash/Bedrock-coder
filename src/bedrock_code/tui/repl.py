from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from bedrock_code.core.agent import AgentLoop
from bedrock_code.core.config import CONFIG_DIR
from bedrock_code.models.registry import get_model_info, list_available_models
from bedrock_code.models.schemas import (
    StreamDone,
    TextChunk,
    ToolCallReady,
    ToolResultEvent,
    ToolStartEvent,
)
from bedrock_code.tui.completer import BedrockCompleter
from bedrock_code.tui.keybindings import build_keybindings
from bedrock_code.tui.renderer import (
    render_markdown,
    render_permission_ask,
    render_streaming_text,
    render_tool_call,
    render_tool_result,
)
from bedrock_code.tui.widgets import (
    render_cost_panel,
    render_help_panel,
    render_models_table,
    render_tools_panel,
    render_welcome_banner,
)
from bedrock_code.utils.cost import calculate_cost, format_cost, format_tokens


class BedrockCodeREPL:
    def __init__(self, agent: AgentLoop, console: Console, config: Any) -> None:
        self._agent = agent
        self._console = console
        self._config = config
        self._interrupted = False

        history_file = CONFIG_DIR / "history"
        history_file.parent.mkdir(parents=True, exist_ok=True)

        self._session: PromptSession = PromptSession(
            history=FileHistory(str(history_file)),
            completer=BedrockCompleter(),
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=build_keybindings(),
            mouse_support=False,
            wrap_lines=True,
        )

        # Wire permission callback to use TUI
        self._agent.set_tool_ask_callback(self._permission_ask)

    def _get_prompt(self) -> HTML:
        model_id = self._agent.get_model()
        info = get_model_info(model_id)
        model_name = info.get("display_name", model_id) if info else model_id[:20]
        is_auto = getattr(self._agent, '_auto_mode', False)
        auto_tag = '<ansiyellow><b>AUTO:</b></ansiyellow> ' if is_auto else ''
        return HTML(
            f'<ansiblue><b> bc </b></ansiblue>'
            f'<ansicyan>[{auto_tag}{model_name}]</ansicyan>'
            f' <b>❯</b> '
        )

    def _permission_ask(self, tool_name: str, inputs: dict) -> bool:
        self._console.print(render_permission_ask(tool_name, inputs))
        try:
            answer = input("Allow? [y/N]: ").strip().lower()
            return answer in ("y", "yes")
        except (EOFError, KeyboardInterrupt):
            return False

    async def run(self, welcome: bool = True) -> None:
        if welcome:
            model_id = self._agent.get_model()
            info = get_model_info(model_id)
            model_name = info.get("display_name", model_id) if info else model_id
            region = self._config.aws_region
            try:
                identity = self._agent._bedrock.verify_credentials().get("Account", "unknown")
            except Exception:
                identity = "unknown"
            self._console.print(render_welcome_banner(model_name, region, identity))

        while True:
            try:
                user_input = await self._session.prompt_async(self._get_prompt())
            except KeyboardInterrupt:
                self._console.print("\n[dim]Use /quit to exit or Ctrl+D[/dim]")
                continue
            except EOFError:
                self._console.print("\n[dim]Goodbye![/dim]")
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            # Shell passthrough
            if user_input.startswith("!"):
                await self._run_shell(user_input[1:].strip())
                continue

            # Slash commands
            if user_input.startswith("/"):
                if not await self._handle_slash(user_input):
                    break
                continue

            # Agent turn
            await self._run_agent_turn(user_input)

    async def _run_agent_turn(self, user_input: str) -> None:
        accumulated_text = ""
        # Map tool_use_id → name so panel titles are correct even when multiple
        # tools fire in the same turn (a shared current_tool variable gets
        # overwritten by the second tool's ToolStartEvent before the first
        # tool's ToolResultEvent arrives).
        tool_name_by_id: dict[str, str] = {}
        self._interrupted = False

        printed_tool_results: list = []

        with Live(
            Text("⠋ Thinking...", style="dim"),
            console=self._console,
            refresh_per_second=15,
            transient=True,   # clears live area on exit; we print the final text ourselves
        ) as live:
            try:
                async for event in self._agent.run(user_input):
                    if self._interrupted:
                        break

                    if isinstance(event, TextChunk):
                        accumulated_text += event.text
                        live.update(render_streaming_text(accumulated_text))

                    elif isinstance(event, ToolStartEvent):
                        if accumulated_text:
                            live.update(render_markdown(accumulated_text))
                        tool_name_by_id[event.tool_use_id] = event.name
                        live.update(Text(f"⚙ Calling {event.name}...", style="yellow"))

                    elif isinstance(event, ToolCallReady):
                        tc = event.tool_call
                        tool_name_by_id[tc.id] = tc.name
                        live.update(render_tool_call(tc.name, tc.input))

                    elif isinstance(event, ToolResultEvent):
                        tc = event.tool_call
                        tool_name = tool_name_by_id.get(tc.id, tc.name or "tool")
                        is_error = event.result.status == "error"
                        result_panel = render_tool_result(
                            tool_name,
                            event.result.content,
                            is_error=is_error,
                        )
                        printed_tool_results.append(result_panel)
                        live.update(result_panel)
                        accumulated_text = ""

            except KeyboardInterrupt:
                self._interrupted = True
                live.update(Text("⚠ Interrupted", style="yellow"))

        # Live has cleared — now print tool results and final text once, cleanly
        for panel in printed_tool_results:
            self._console.print(panel)

        if accumulated_text:
            self._console.print(render_markdown(accumulated_text))

        # Show cost line
        if self._config.show_cost or self._config.show_token_count:
            usage = self._agent._context.session_usage
            cost = self._agent._context.session_cost
            self._console.print(
                Text.assemble(
                    (" ↑", "dim blue"),
                    (f"{usage.input_tokens:,}", "cyan"),
                    (" ↓", "dim blue"),
                    (f"{usage.output_tokens:,}", "cyan"),
                    ("  $", "dim"),
                    (f"{cost:.5f}", "dim green"),
                ),
                end="\n",
            )

    async def _run_shell(self, command: str) -> None:
        from bedrock_code.tools.shell import bash_exec
        self._console.print(f"[dim]$ {command}[/dim]")
        result = await bash_exec(command)
        self._console.print(result)

    async def _handle_slash(self, command: str) -> bool:
        """Returns False if the REPL should exit."""
        parts = command.strip().split(maxsplit=2)
        cmd = parts[0].lower()

        if cmd in ("/quit", "/exit"):
            self._console.print("[dim]Goodbye![/dim]")
            return False

        elif cmd == "/help":
            self._console.print(render_help_panel())

        elif cmd == "/clear":
            self._agent._context.clear()
            self._console.clear()
            self._console.print("[dim]Conversation cleared.[/dim]")

        elif cmd == "/model":
            await self._handle_model_command(parts[1:])

        elif cmd == "/tools":
            await self._handle_tools_command()

        elif cmd == "/config":
            await self._handle_config_command(parts[1:])

        elif cmd == "/memory":
            self._agent.reload_memory()
            mem = self._agent._memory
            if mem:
                self._console.print(Panel(mem, title="[bold cyan]Memory", border_style="cyan"))
            else:
                self._console.print("[dim]No memory loaded.[/dim]")

        elif cmd == "/cost":
            usage = self._agent._context.session_usage
            self._console.print(render_cost_panel(
                session_input=usage.input_tokens,
                session_output=usage.output_tokens,
                session_cost=self._agent._context.session_cost,
                turn_count=self._agent._context._turn_count,
            ))

        elif cmd == "/compact":
            await self._handle_compact()

        else:
            self._console.print(f"[bc.warning]Unknown command: {cmd}[/bc.warning]")
            self._console.print("[dim]Type /help for available commands.[/dim]")

        return True

    async def _handle_model_command(self, args: list[str]) -> None:
        models = list_available_models()
        current_id = self._agent.get_model()
        is_auto = getattr(self._agent, '_auto_mode', False)

        # If called with an arg directly (/model 5, /model qwen3-32b, /model auto)
        if args:
            await self._apply_model_selection(args[0], models)
            return

        # No arg → show table then prompt inline
        self._console.print(render_models_table(models))

        # Show current status
        current_info = get_model_info(current_id)
        current_name = current_info.get("display_name", current_id) if current_info else current_id
        mode_tag = "[cyan]AUTO[/cyan] → " if is_auto else ""
        self._console.print(
            f"\n  Current: {mode_tag}[bold]{current_name}[/bold]  [dim]({current_id})[/dim]"
        )
        self._console.print(
            "  Enter [bold cyan]number[/bold cyan], [bold cyan]alias[/bold cyan], "
            "[bold cyan]model ID[/bold cyan], or [bold cyan]auto[/bold cyan]  "
            "[dim](Enter to keep current)[/dim]"
        )

        try:
            selection = await self._session.prompt_async("  > ")
            selection = selection.strip()
        except (KeyboardInterrupt, EOFError):
            self._console.print("[dim]Cancelled.[/dim]")
            return

        if not selection:
            self._console.print("[dim]No change.[/dim]")
            return

        await self._apply_model_selection(selection, models)

    async def _apply_model_selection(self, selection: str, models: list) -> None:
        selection = selection.strip().lower()

        # Auto mode
        if selection == "auto":
            best = _pick_auto_model(models)
            self._agent.set_model(best["id"])
            self._agent._auto_mode = True
            self._console.print(
                f"[bc.success]AUTO mode[/bc.success] — using [bold]{best['display_name']}[/bold]  "
                f"[dim](bc will pick the best model per task)[/dim]"
            )
            return

        # By number
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(models):
                m = models[idx]
                self._agent.set_model(m["id"])
                self._agent._auto_mode = False
                self._console.print(
                    f"[bc.success]Switched to [bold]{m['display_name']}[/bold][/bc.success]  "
                    f"[dim]({m['id']})[/dim]"
                )
                return
            self._console.print(f"[bc.error]Invalid number — enter 1–{len(models)}.[/bc.error]")
            return

        # By alias (exact or prefix match)
        for m in models:
            if selection in (
                m.get("alias", ""),
                m.get("id", ""),
                m.get("display_name", "").lower(),
            ) or m.get("alias", "").startswith(selection) or m.get("id", "").startswith(selection):
                self._agent.set_model(m["id"])
                self._agent._auto_mode = False
                self._console.print(
                    f"[bc.success]Switched to [bold]{m['display_name']}[/bold][/bc.success]  "
                    f"[dim]({m['id']})[/dim]"
                )
                return

        # Accept any raw model ID (user might type a Bedrock ID not in registry)
        if "." in selection or ":" in selection:
            self._agent.set_model(selection)
            self._agent._auto_mode = False
            self._console.print(f"[bc.success]Switched to [bold]{selection}[/bold][/bc.success]")
            return

        self._console.print(
            f"[bc.error]Not found: '{selection}'[/bc.error]  "
            "[dim]Try a number, alias, or type 'auto'.[/dim]"
        )

    async def _handle_tools_command(self) -> None:
        specs = self._agent._tools.all()
        mcp_connections = self._agent._mcp._connections
        perms = {spec.name: self._config.permission_for(spec.name) for spec in specs}
        self._console.print(render_tools_panel(specs, mcp_connections, perms))

    async def _handle_config_command(self, args: list[str]) -> None:
        if not args:
            import json
            self._console.print(Panel(
                json.dumps(self._config.raw(), indent=2, default=str),
                title="[bold cyan]Config",
                border_style="cyan",
            ))
            return

        if len(args) == 1:
            # /config key — show value
            key = args[0]
            parts = key.split(".")
            val = self._config.get(*parts)
            self._console.print(f"[bold]{key}[/bold] = {val!r}")
        elif len(args) >= 2:
            # /config key value — set value
            key = args[0]
            value = args[1]
            parts = key.split(".")
            # Try to cast to appropriate type
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
            self._config.set(*parts, value=value)
            self._config.save()
            self._console.print(f"[bc.success]Set [bold]{key}[/bold] = {value!r}[/bc.success]")

    async def _handle_compact(self) -> None:
        self._console.print("[dim]Compacting conversation history...[/dim]")
        history_text = "\n".join(
            str(msg.get("content", ""))
            for msg in self._agent._context.messages()
        )
        summary_prompt = (
            "Summarize the conversation so far in a concise but complete way. "
            "Include: what was discussed, what files were edited, what commands were run, "
            "and any important decisions made. This summary will replace the full history."
        )
        try:
            self._agent._context.compact_summary_message(
                f"[Conversation compacted]\n\n{summary_prompt}\n\n"
                f"(Previous {len(self._agent._context.messages())} messages summarized)"
            )
            self._console.print("[bc.success]History compacted.[/bc.success]")
        except Exception as e:
            self._console.print(f"[bc.error]Compact failed: {e}[/bc.error]")


# ── Auto-mode model picker ────────────────────────────────────────────────────

# Priority order for auto selection: prefer latest Claude, then capable open models
_AUTO_PRIORITY = [
    "global.anthropic.claude-sonnet-4-6",
    "global.anthropic.claude-sonnet-4-5",
    "global.anthropic.claude-haiku-4-5",
    "apac.anthropic.claude-3-7-sonnet",
    "apac.anthropic.claude-3-5-sonnet",
    "qwen.qwen3-coder-480b",
    "qwen.qwen3-235b",
    "mistral.mistral-large-3",
    "deepseek.v3",
]


def _pick_auto_model(models: list[dict]) -> dict:
    """Return the best available model for auto mode."""
    # Match by prefix priority
    for prefix in _AUTO_PRIORITY:
        for m in models:
            if m.get("id", "").startswith(prefix) and m.get("tool_use"):
                return m
    # Fallback: first tool-capable model
    for m in models:
        if m.get("tool_use"):
            return m
    return models[0]
