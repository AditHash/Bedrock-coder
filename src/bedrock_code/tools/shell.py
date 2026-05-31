from __future__ import annotations

import asyncio
import os
import sys


SAFE_COMMAND_PREFIXES = [
    "ls", "cat", "head", "tail", "grep", "find", "pwd", "echo", "which",
    "git status", "git diff", "git log", "git show", "git branch",
    "python --version", "python3 --version", "node --version", "npm --version",
    "pip list", "pip show", "uv", "rg", "fd", "bat",
    "wc", "sort", "uniq", "diff", "file", "stat", "du", "df",
    "env", "printenv", "type", "where",
]


def is_safe_command(command: str) -> bool:
    cmd = command.strip()
    return any(cmd.startswith(prefix) for prefix in SAFE_COMMAND_PREFIXES)


async def bash_exec(command: str, timeout: int = 30, cwd: str | None = None) -> str:
    work_dir = cwd or os.getcwd()
    if sys.platform == "win32":
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir,
            shell=True,
        )
    else:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir,
            executable="/bin/bash",
        )

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return f"Error: Command timed out after {timeout}s"

    output_parts: list[str] = []
    if stdout:
        output_parts.append(stdout.decode("utf-8", errors="replace").rstrip())
    if stderr:
        output_parts.append("STDERR:\n" + stderr.decode("utf-8", errors="replace").rstrip())

    result = "\n".join(output_parts) if output_parts else ""
    if proc.returncode != 0:
        result = f"Exit code: {proc.returncode}\n{result}" if result else f"Exit code: {proc.returncode}"
    return result or "(no output)"


def register_shell_tools(registry: object) -> None:
    from bedrock_code.tools.registry import ToolSpec

    registry.register(ToolSpec(
        name="bash_exec",
        description=(
            "Execute a shell command and return its output. "
            "Use for running tests, building projects, installing packages, etc. "
            "Always check permissions before executing non-read-only commands."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"},
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30)",
                    "default": 30,
                },
            },
            "required": ["command"],
        },
        handler=bash_exec,
        requires_permission=True,
    ))
