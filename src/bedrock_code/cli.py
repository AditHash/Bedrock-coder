from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from bedrock_code import __version__
from bedrock_code.tui.theme import get_theme

app = typer.Typer(
    name="bc",
    help="bedrock-code: A Claude Code-like CLI powered by AWS Bedrock",
    add_completion=False,
    no_args_is_help=False,
    invoke_without_command=True,
)


def _build_app(
    model: str | None,
    region: str | None,
    profile: str | None,
    no_color: bool,
    compact: bool,
) -> tuple:
    """Build all app components and return (agent, repl, console, config)."""
    from bedrock_code.core.agent import AgentLoop
    from bedrock_code.core.config import load_config
    from bedrock_code.core.context import ConversationContext
    from bedrock_code.core.permissions import PermissionManager
    from bedrock_code.core.router import ModelRouter
    from bedrock_code.mcp.duckduckgo import DuckDuckGoMCP
    from bedrock_code.mcp.manager import MCPManager
    from bedrock_code.models.bedrock import BedrockClient, BedrockError
    from bedrock_code.models.registry import get_model_id, list_available_models
    from bedrock_code.tools.editor import register_editor_tools
    from bedrock_code.tools.filesystem import register_filesystem_tools
    from bedrock_code.tools.git_tools import register_git_tools
    from bedrock_code.tools.registry import ToolRegistry
    from bedrock_code.tools.shell import register_shell_tools
    from bedrock_code.tools.task_tracker import register_task_tools, set_persistent_file
    from bedrock_code.tools.web_search import register_web_search_tool
    from bedrock_code.tui.repl import BedrockCodeREPL

    config = load_config()

    if region:
        config.set("aws", "region", value=region)
    if profile:
        config.set("aws", "profile", value=profile)

    theme = get_theme(config.theme)
    console = Console(theme=theme, highlight=True, force_terminal=not no_color)

    # Override model
    effective_model = config.default_model
    if model:
        resolved_id = get_model_id(model) or model
        effective_model = resolved_id

    # AWS client
    try:
        bedrock = BedrockClient(
            region=config.aws_region,
            profile=config.aws_profile,
        )
    except Exception as e:
        console.print(f"[bc.error]Failed to create Bedrock client: {e}[/bc.error]")
        raise typer.Exit(1)

    # Tool registry
    tool_registry = ToolRegistry()
    register_filesystem_tools(tool_registry)
    register_editor_tools(tool_registry)
    register_shell_tools(tool_registry)
    register_git_tools(tool_registry)
    register_task_tools(tool_registry)
    register_web_search_tool(
        tool_registry,
        bedrock_client=bedrock,
        nova_model_id=config.nova_model_id,
    )

    # Todo persistence
    from bedrock_code.core.config import CONFIG_DIR
    set_persistent_file(CONFIG_DIR / "todos.json")

    # MCP manager + DuckDuckGo (kept for user-configured MCP servers)
    mcp_manager = MCPManager()
    ddg = DuckDuckGoMCP(mcp_manager, package=config.duckduckgo_package)

    # Spawn any pre-configured MCP servers
    mcp_servers = config.get("mcp", "servers", default={})
    # (started lazily on demand — don't block startup)

    # Core components
    permissions = PermissionManager(config)
    router = ModelRouter(config)
    context = ConversationContext(context_window=200_000, budget_ratio=0.85)

    agent = AgentLoop(
        config=config,
        bedrock=bedrock,
        tool_registry=tool_registry,
        mcp_manager=mcp_manager,
        permissions=permissions,
        router=router,
        context=context,
        ddg=ddg,
    )
    agent.set_model(effective_model)

    repl = BedrockCodeREPL(agent=agent, console=console, config=config)
    return agent, repl, console, config


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model alias or ID to use"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output"),
    compact: bool = typer.Option(False, "--compact", help="Compact mode (less verbose output)"),
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
    prompt: Optional[str] = typer.Argument(None, help="One-shot prompt (non-interactive)"),
) -> None:
    """
    bedrock-code: An AI coding assistant powered by AWS Bedrock.

    Run without arguments to start the interactive REPL.
    Pass a prompt as an argument for one-shot mode.
    """
    if version:
        typer.echo(f"bedrock-code v{__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is not None:
        return

    # Check AWS credentials early
    _check_aws_credentials()

    # First-run setup wizard: runs automatically when no config exists yet
    from bedrock_code.core.config import CONFIG_FILE
    if not CONFIG_FILE.exists():
        from bedrock_code.setup_wizard import run_wizard
        from rich.console import Console as RichConsole
        from bedrock_code.tui.theme import get_theme as _get_theme
        from bedrock_code.core.config import load_config as _reload
        _con = RichConsole(theme=_get_theme("dark"))
        if not run_wizard(console=_con):
            raise typer.Exit(0)
        typer.echo("")  # blank line before REPL starts

    try:
        agent, repl, console, config = _build_app(model, region, profile, no_color, compact)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    if prompt:
        # One-shot mode
        asyncio.run(_oneshot(agent, console, prompt))
    else:
        # Interactive REPL
        try:
            asyncio.run(repl.run(welcome=True))
        except KeyboardInterrupt:
            pass
        finally:
            asyncio.run(agent._mcp.stop_all())


async def _oneshot(agent: object, console: object, prompt: str) -> None:
    from bedrock_code.models.schemas import StreamDone, TextChunk, ToolCallReady, ToolResultEvent
    from bedrock_code.tui.renderer import render_markdown, render_tool_call, render_tool_result

    accumulated = ""
    async for event in agent.run(prompt):
        if isinstance(event, TextChunk):
            accumulated += event.text
        elif isinstance(event, ToolCallReady):
            if accumulated:
                console.print(render_markdown(accumulated))
                accumulated = ""
            console.print(render_tool_call(event.tool_call.name, event.tool_call.input))
        elif isinstance(event, ToolResultEvent):
            console.print(render_tool_result(
                event.tool_call.name,
                event.result.content,
                is_error=event.result.status == "error",
            ))

    if accumulated:
        console.print(render_markdown(accumulated))


def _check_aws_credentials() -> None:
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, PartialCredentialsError
        boto3.client("sts").get_caller_identity()
    except Exception as e:
        err_str = str(e)
        if "credentials" in err_str.lower() or "NoCredentials" in err_str:
            typer.echo(
                "⚠ No AWS credentials found.\n"
                "  Run: aws configure\n"
                "  Or set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION\n"
                "  Or use: --profile <profile-name>",
                err=True,
            )
            raise typer.Exit(1)
        # Non-credential errors (network, etc.) — warn but continue
        typer.echo(f"⚠ AWS credential check failed: {e}", err=True)


@app.command("setup")
def setup_cmd(
    force: bool = typer.Option(False, "--force", "-f", help="Re-run even if config already exists"),
) -> None:
    """Interactive setup wizard: choose region and default model."""
    from bedrock_code.setup_wizard import run_wizard
    from bedrock_code.tui.theme import get_theme

    console = Console(theme=get_theme("dark"))
    run_wizard(console=console, force=True)


@app.command("models")
def list_models_cmd() -> None:
    """List all available Bedrock models."""
    from bedrock_code.models.registry import list_available_models
    from bedrock_code.tui.theme import get_theme
    from bedrock_code.core.config import load_config

    config = load_config()
    console = Console(theme=get_theme(config.theme))
    from bedrock_code.tui.widgets import render_models_table
    models = list_available_models()
    console.print(render_models_table(models))


@app.command("config")
def show_config_cmd() -> None:
    """Show current configuration."""
    import json
    from bedrock_code.core.config import load_config
    from bedrock_code.tui.theme import get_theme

    config = load_config()
    console = Console(theme=get_theme(config.theme))
    from rich.panel import Panel
    console.print(Panel(
        json.dumps(config.raw(), indent=2, default=str),
        title="[bold cyan]bedrock-code config",
        border_style="cyan",
    ))


@app.command("version")
def version_cmd() -> None:
    """Show version information."""
    typer.echo(f"bedrock-code v{__version__}")
