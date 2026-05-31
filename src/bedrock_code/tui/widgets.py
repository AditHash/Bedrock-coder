from __future__ import annotations

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bedrock_code import __version__


def render_welcome_banner(model_name: str, region: str, identity: str) -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_column(justify="right")

    grid.add_row(
        Text.assemble(
            ("⬡ bedrock-code ", "bold cyan"),
            (f"v{__version__}", "dim cyan"),
        ),
        Text.assemble(
            ("AWS ", "dim"),
            (region, "cyan"),
        ),
    )
    grid.add_row(
        Text.assemble(
            ("Model: ", "dim"),
            (model_name, "bold white"),
        ),
        Text.assemble(
            ("Account: ", "dim"),
            (identity[:20] + "..." if len(identity) > 20 else identity, "dim white"),
        ),
    )
    grid.add_row(
        Text.assemble(("Type ", "dim"), ("/help", "bold cyan"), (" for commands", "dim")),
        Text.assemble(("Ctrl+D", "bold"), (" to exit", "dim")),
    )

    return Panel(
        grid,
        border_style="cyan",
        padding=(0, 1),
    )


def render_help_panel() -> Panel:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Command", style="bold cyan", no_wrap=True)
    table.add_column("Description")

    commands = [
        ("/help", "Show this help"),
        ("/clear", "Clear conversation history"),
        ("/model [name]", "Show or switch model"),
        ("/tools", "List active tools and permissions"),
        ("/config [key] [value]", "View or set config"),
        ("/memory", "Show loaded memory"),
        ("/cost", "Show session cost breakdown"),
        ("/compact", "Summarize history to save context"),
        ("/quit or /exit", "Exit bedrock-code"),
        ("", ""),
        ("@file", "Attach file to next message"),
        ("!cmd", "Quick shell command (bypasses agent)"),
        ("Alt+Enter / Ctrl+J", "New line in input"),
        ("Ctrl+L", "Clear screen"),
        ("Ctrl+R", "Search history"),
    ]
    for cmd, desc in commands:
        table.add_row(cmd, desc)

    return Panel(table, title="[bold cyan]bedrock-code commands", border_style="cyan", padding=(1, 2))


def render_tools_panel(tool_specs: list, mcp_connections: dict, permissions_config: dict) -> Panel:
    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    table.add_column("Tool", style="bold", no_wrap=True)
    table.add_column("Permission")
    table.add_column("Source")

    perm_styles = {"allow": "green", "ask": "yellow", "deny": "red"}

    for spec in tool_specs:
        perm = permissions_config.get(spec.name, "ask")
        style = perm_styles.get(perm, "white")
        table.add_row(spec.name, Text(perm, style=style), "local")

    for server_name, conn in mcp_connections.items():
        for tool in conn.tools:
            tname = tool["name"] if isinstance(tool, dict) else tool.name
            table.add_row(f"{server_name}__{tname}", Text("allow", style="green"), f"mcp:{server_name}")

    return Panel(table, title="[bold cyan]Active Tools", border_style="cyan", padding=(0, 1))


def render_cost_panel(
    session_input: int,
    session_output: int,
    session_cost: float,
    turn_count: int,
) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left")
    table.add_column(justify="right")

    table.add_row("[dim]Input tokens[/dim]", f"[cyan]{session_input:,}[/cyan]")
    table.add_row("[dim]Output tokens[/dim]", f"[cyan]{session_output:,}[/cyan]")
    table.add_row("[dim]Total turns[/dim]", f"[white]{turn_count}[/white]")
    table.add_row("[dim]Estimated cost[/dim]", f"[bold green]${session_cost:.5f}[/bold green]")

    return Panel(table, title="[bold cyan]Session Cost", border_style="cyan", padding=(0, 1))


def render_models_table(models: list[dict]) -> Panel:
    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    table.add_column("#", style="dim", width=3)
    table.add_column("Alias", style="bold")
    table.add_column("Display Name")
    table.add_column("Provider")
    table.add_column("Tools", justify="center")
    table.add_column("Web Search", justify="center")
    table.add_column("Input $/1M", justify="right")

    provider_styles = {
        "Anthropic": "bold #FF6B35",
        "Amazon": "bold #FF9900",
        "Mistral": "bold #7C3AED",
        "Meta": "bold #0078FF",
        "Cohere": "bold #39D353",
    }

    for i, m in enumerate(models, 1):
        pstyle = provider_styles.get(m.get("provider", ""), "white")
        tools_icon = "✓" if m.get("tool_use") else "✗"
        ws_icon = "✓" if m.get("web_search") else "✗"
        tools_style = "green" if m.get("tool_use") else "red"
        ws_style = "green" if m.get("web_search") else "dim"
        cost = f"${m.get('input_cost_per_1m', 0):.2f}" if m.get("input_cost_per_1m") else "N/A"

        table.add_row(
            str(i),
            m.get("alias", ""),
            m.get("display_name", ""),
            Text(m.get("provider", ""), style=pstyle),
            Text(tools_icon, style=tools_style),
            Text(ws_icon, style=ws_style),
            cost,
        )

    return Panel(table, title="[bold cyan]Available Models", border_style="cyan", padding=(0, 1))
