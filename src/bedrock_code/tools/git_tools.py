from __future__ import annotations

import os

from bedrock_code.tools.shell import bash_exec


async def git_status(directory: str = ".") -> str:
    return await bash_exec("git status", cwd=directory or os.getcwd())


async def git_diff(
    directory: str = ".",
    staged: bool = False,
    file_path: str | None = None,
) -> str:
    cmd = "git diff --staged" if staged else "git diff"
    if file_path:
        cmd += f" -- {file_path}"
    return await bash_exec(cmd, cwd=directory or os.getcwd())


async def git_log(directory: str = ".", max_count: int = 20, oneline: bool = True) -> str:
    fmt = "--oneline" if oneline else "--format='%h %an %s %ai'"
    return await bash_exec(f"git log {fmt} -n {max_count}", cwd=directory or os.getcwd())


async def git_show(ref: str = "HEAD", directory: str = ".") -> str:
    return await bash_exec(f"git show {ref} --stat", cwd=directory or os.getcwd())


async def git_commit(message: str, directory: str = ".") -> str:
    safe_msg = message.replace('"', '\\"')
    return await bash_exec(f'git commit -m "{safe_msg}"', cwd=directory or os.getcwd())


async def git_add(paths: str = ".", directory: str = ".") -> str:
    return await bash_exec(f"git add {paths}", cwd=directory or os.getcwd())


async def git_branch(directory: str = ".") -> str:
    return await bash_exec("git branch -a", cwd=directory or os.getcwd())


async def git_checkout(branch: str, create: bool = False, directory: str = ".") -> str:
    flag = "-b" if create else ""
    return await bash_exec(f"git checkout {flag} {branch}".strip(), cwd=directory or os.getcwd())


def register_git_tools(registry: object) -> None:
    from bedrock_code.tools.registry import ToolSpec

    registry.register(ToolSpec(
        name="git_status",
        description="Show the working tree status of the git repository.",
        input_schema={"type": "object", "properties": {}},
        handler=git_status,
        requires_permission=False,
    ))

    registry.register(ToolSpec(
        name="git_diff",
        description="Show changes in the working tree or staged changes.",
        input_schema={
            "type": "object",
            "properties": {
                "staged": {"type": "boolean", "description": "Show staged (--staged) diff", "default": False},
                "file_path": {"type": "string", "description": "Limit diff to specific file"},
            },
        },
        handler=git_diff,
        requires_permission=False,
    ))

    registry.register(ToolSpec(
        name="git_log",
        description="Show commit history.",
        input_schema={
            "type": "object",
            "properties": {
                "max_count": {"type": "integer", "description": "Max commits to show", "default": 20},
                "oneline": {"type": "boolean", "description": "Compact one-line format", "default": True},
            },
        },
        handler=git_log,
        requires_permission=False,
    ))

    registry.register(ToolSpec(
        name="git_commit",
        description="Create a git commit with the given message. Requires permission.",
        input_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Commit message"},
            },
            "required": ["message"],
        },
        handler=git_commit,
        requires_permission=True,
    ))

    registry.register(ToolSpec(
        name="git_add",
        description="Stage files for commit. Requires permission.",
        input_schema={
            "type": "object",
            "properties": {
                "paths": {"type": "string", "description": "Paths to stage (space-separated or '.')", "default": "."},
            },
        },
        handler=git_add,
        requires_permission=True,
    ))
