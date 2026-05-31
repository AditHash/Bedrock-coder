from __future__ import annotations

import sys
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from bedrock_code import __version__
from bedrock_code.core.config import CONFIG_FILE, load_config
from bedrock_code.tui.theme import get_theme

# Bedrock-enabled regions with friendly names
BEDROCK_REGIONS: list[tuple[str, str]] = [
    ("ap-south-1",      "Asia Pacific — Mumbai       (your current login)"),
    ("ap-southeast-1",  "Asia Pacific — Singapore"),
    ("ap-southeast-2",  "Asia Pacific — Sydney"),
    ("ap-northeast-1",  "Asia Pacific — Tokyo"),
    ("us-east-1",       "US East       — N. Virginia"),
    ("us-west-2",       "US West       — Oregon"),
    ("eu-west-1",       "Europe        — Ireland"),
    ("eu-central-1",    "Europe        — Frankfurt"),
    ("eu-west-3",       "Europe        — Paris"),
    ("ca-central-1",    "Canada        — Central"),
    ("sa-east-1",       "South America — São Paulo"),
]

# Priority order for auto model selection (provider preference)
AUTO_PRIORITY = [
    "global.anthropic.",
    "apac.anthropic.",
    "ap.anthropic.",
    "us.anthropic.",
    "qwen.",
    "mistral.",
    "deepseek.",
    "meta.",
    "openai.",
    "minimax.",
    "nvidia.",
    "google.",
    "zai.",
]


def run_wizard(console: Console | None = None, force: bool = False) -> bool:
    """
    Run the interactive setup wizard.
    Returns True if setup completed, False if skipped/cancelled.
    """
    theme = get_theme("dark")
    con = console or Console(theme=theme)

    _print_banner(con)

    # Skip if config already exists and not forced
    if CONFIG_FILE.exists() and not force:
        con.print("[dim]Config already exists at[/dim] "
                  f"[cyan]{CONFIG_FILE}[/cyan]")
        if not Confirm.ask("Re-run setup wizard?", default=False, console=con):
            return False

    con.print()

    # ── Step 1: verify AWS credentials ──────────────────────────────────────
    con.print("[bold cyan]Step 1/3 — AWS Credentials[/bold cyan]")
    identity = _check_credentials(con)
    if identity is None:
        return False
    con.print(f"  [green]Logged in as:[/green] {identity['Arn']}")
    con.print()

    # ── Step 2: choose region ────────────────────────────────────────────────
    con.print("[bold cyan]Step 2/3 — AWS Region[/bold cyan]")
    region = _choose_region(con)
    con.print(f"  [green]Region:[/green] {region}")
    con.print()

    # ── Step 3: choose model ─────────────────────────────────────────────────
    con.print("[bold cyan]Step 3/3 — Default Model[/bold cyan]")
    available_models = _fetch_models(con, region)
    model_id, model_display, is_auto = _choose_model(con, available_models, region)
    con.print(f"  [green]Model:[/green] {model_display} [dim]({model_id})[/dim]")
    con.print()

    # ── Save config ───────────────────────────────────────────────────────────
    config = load_config()
    config.set("aws", "region", value=region)
    config.set("core", "default_model", value=model_id)
    config.set("core", "auto_model", value=is_auto)

    # Update Nova model to correct region prefix
    nova_id = _best_nova(available_models, region)
    if nova_id:
        config.set("web_search", "nova_model", value=nova_id)

    config.save()

    con.print(Panel(
        f"[green]Setup complete![/green]\n\n"
        f"  Config saved to [cyan]{CONFIG_FILE}[/cyan]\n"
        f"  Region:  [bold]{region}[/bold]\n"
        f"  Model:   [bold]{model_display}[/bold]\n\n"
        f"  Run [bold cyan]bc[/bold cyan] to start.",
        border_style="green",
        padding=(0, 2),
    ))
    return True


def _print_banner(con: Console) -> None:
    con.print(Panel(
        Text.assemble(
            ("  bedrock-code ", "bold cyan"),
            (f"v{__version__}\n", "dim cyan"),
            ("  Setup Wizard\n\n", "bold white"),
            ("  Configure your AWS region and default model.", "dim"),
        ),
        border_style="cyan",
        padding=(0, 1),
    ))


def _check_credentials(con: Console) -> dict | None:
    con.print("  Checking AWS credentials...", end=" ")
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        con.print("[green]OK[/green]")
        return identity
    except Exception as e:
        con.print("[red]FAILED[/red]")
        con.print(f"\n  [red]Could not authenticate with AWS:[/red] {e}\n")
        con.print("  Run [bold]aws configure[/bold] or [bold]aws login[/bold] first.")
        return None


def _choose_region(con: Console) -> str:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Num", style="bold cyan", width=4)
    table.add_column("Region ID", style="bold")
    table.add_column("Description", style="dim")

    for i, (rid, desc) in enumerate(BEDROCK_REGIONS, 1):
        table.add_row(str(i), rid, desc)

    con.print(table)
    con.print()

    while True:
        answer = Prompt.ask(
            "  [bold]Choose region[/bold] [dim](number or region id)[/dim]",
            default="1",
            console=con,
        ).strip()

        if answer.isdigit():
            idx = int(answer) - 1
            if 0 <= idx < len(BEDROCK_REGIONS):
                return BEDROCK_REGIONS[idx][0]
            con.print(f"  [red]Invalid number. Enter 1–{len(BEDROCK_REGIONS)}.[/red]")
        else:
            # Accept raw region ID
            if answer in {r for r, _ in BEDROCK_REGIONS} or answer.startswith("ap-") or answer.startswith("us-") or answer.startswith("eu-"):
                return answer
            con.print(f"  [red]Unknown region '{answer}'. Enter a number or a valid region ID.[/red]")


def _fetch_models(con: Console, region: str) -> list[dict[str, Any]]:
    con.print(f"  Fetching available models in [bold]{region}[/bold]...", end=" ")
    try:
        client = boto3.client("bedrock", region_name=region)
        resp = client.list_foundation_models(byOutputModality="TEXT")
        direct = resp.get("modelSummaries", [])

        inf_resp = client.list_inference_profiles(typeEquals="SYSTEM_DEFINED")
        profiles = inf_resp.get("inferenceProfileSummaries", [])

        con.print(f"[green]{len(direct)} direct + {len(profiles)} inference profiles[/green]")
        return direct, profiles
    except Exception as e:
        con.print(f"[yellow]Warning: {e}[/yellow]")
        return [], []


def _choose_model(
    con: Console,
    fetched: tuple,
    region: str,
) -> tuple[str, str, bool]:
    direct_models, inf_profiles = fetched

    # Build a unified list of on-demand-capable entries
    entries: list[dict[str, Any]] = []

    # On-demand direct models
    for m in direct_models:
        if "ON_DEMAND" in m.get("inferenceTypesSupported", []):
            entries.append({
                "id": m["modelId"],
                "display": f"{m['providerName']} — {m['modelId'].split('.')[-1].replace('-instruct','').replace('-v1:0','').replace('-v2:0','').upper()}",
                "provider": m["providerName"],
                "source": "direct",
            })

    # Cross-region inference profiles (always on-demand)
    for p in inf_profiles:
        pid = p["inferenceProfileId"]
        entries.append({
            "id": pid,
            "display": f"{pid.split('.', 1)[-1].replace('anthropic.', 'Anthropic ').replace('amazon.', 'Amazon ').replace('meta.', 'Meta ')}",
            "provider": pid.split(".")[0].upper() + " inference",
            "source": "profile",
        })

    if not entries:
        con.print("  [yellow]Could not list models. Using default.[/yellow]")
        from bedrock_code.models.registry import DEFAULT_MODEL_ALIAS, BEDROCK_MODELS
        fallback_id = BEDROCK_MODELS[DEFAULT_MODEL_ALIAS]["id"]
        return fallback_id, DEFAULT_MODEL_ALIAS, False

    # Sort: inference profiles first, then by provider priority
    def sort_key(e: dict) -> tuple:
        pid = e["id"]
        for i, prefix in enumerate(AUTO_PRIORITY):
            if pid.startswith(prefix):
                return (0 if e["source"] == "profile" else 1, i, pid)
        return (1, 999, pid)

    entries.sort(key=sort_key)

    # Display table
    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    table.add_column("#", style="bold cyan", width=4)
    table.add_column("Model ID")
    table.add_column("Type", style="dim", width=12)

    for i, e in enumerate(entries[:40], 1):  # cap display at 40
        src_label = "[cyan]profile[/cyan]" if e["source"] == "profile" else "direct"
        table.add_row(str(i), e["id"], src_label)

    con.print(table)
    if len(entries) > 40:
        con.print(f"  [dim]... and {len(entries) - 40} more[/dim]")
    con.print()
    con.print("  [bold]auto[/bold] — let bedrock-code pick the best available model automatically")
    con.print()

    while True:
        answer = Prompt.ask(
            "  [bold]Choose model[/bold] [dim](number, model ID, or 'auto')[/dim]",
            default="auto",
            console=con,
        ).strip().lower()

        if answer == "auto":
            best = entries[0]  # already sorted by priority
            return best["id"], best["id"], True

        if answer.isdigit():
            idx = int(answer) - 1
            if 0 <= idx < len(entries):
                e = entries[idx]
                return e["id"], e["id"], False
            con.print(f"  [red]Invalid number. Enter 1–{min(len(entries), 40)} or 'auto'.[/red]")
            continue

        # Accept raw model ID
        for e in entries:
            if answer in e["id"].lower() or answer == e["id"]:
                return e["id"], e["id"], False

        # Accept any string as custom model ID
        if "." in answer or ":" in answer:
            return answer, answer, False

        con.print("  [red]Not found. Enter a number, a model ID, or 'auto'.[/red]")


def _best_nova(fetched: tuple, region: str) -> str | None:
    _, inf_profiles = fetched
    for p in inf_profiles:
        pid = p["inferenceProfileId"]
        if "nova-pro" in pid:
            return pid
    for p in inf_profiles:
        pid = p["inferenceProfileId"]
        if "nova-lite" in pid:
            return pid
    return None
