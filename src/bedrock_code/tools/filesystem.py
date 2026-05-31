from __future__ import annotations

import os
from pathlib import Path

from bedrock_code.utils.file_utils import (
    get_file_tree,
    is_text_file,
    safe_resolve,
    truncate_content,
)

MAX_READ_SIZE = 200_000


async def read_file(path: str) -> str:
    resolved = safe_resolve(path)
    if not resolved.exists():
        return f"Error: File not found: {path}"
    if resolved.is_dir():
        return f"Error: {path} is a directory. Use list_directory instead."
    if not is_text_file(resolved):
        return f"Error: {path} appears to be a binary file."
    try:
        content = resolved.read_text(encoding="utf-8", errors="replace")
        return truncate_content(content, MAX_READ_SIZE)
    except OSError as e:
        return f"Error reading file: {e}"


async def write_file(path: str, content: str) -> str:
    resolved = safe_resolve(path)
    try:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return f"Written {len(content)} characters to {path}"
    except OSError as e:
        return f"Error writing file: {e}"


async def list_directory(path: str = ".", max_depth: int = 2) -> str:
    resolved = safe_resolve(path)
    if not resolved.exists():
        return f"Error: Directory not found: {path}"
    if not resolved.is_dir():
        return f"Error: {path} is not a directory."
    lines = get_file_tree(resolved, max_depth=max_depth)
    return "\n".join(lines)


async def search_files(
    pattern: str,
    directory: str = ".",
    include_content: bool = False,
) -> str:
    import fnmatch

    resolved = safe_resolve(directory)
    matches: list[str] = []
    for root, dirs, files in os.walk(resolved):
        dirs[:] = [
            d
            for d in dirs
            if d not in (".git", "__pycache__", "node_modules", ".venv", "venv")
        ]
        for fname in files:
            if fnmatch.fnmatch(fname, pattern):
                full_path = Path(root) / fname
                rel = full_path.relative_to(resolved)
                if include_content and is_text_file(full_path):
                    try:
                        snippet = full_path.read_text(encoding="utf-8", errors="replace")[:500]
                        matches.append(f"{rel}:\n{snippet}\n---")
                    except OSError:
                        matches.append(str(rel))
                else:
                    matches.append(str(rel))
    if not matches:
        return f"No files matching '{pattern}' in {directory}"
    return "\n".join(matches[:100])


async def grep_files(
    pattern: str,
    directory: str = ".",
    file_pattern: str = "*",
    context_lines: int = 2,
) -> str:
    import fnmatch
    import re

    resolved = safe_resolve(directory)
    results: list[str] = []
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return f"Invalid regex pattern: {e}"

    count = 0
    for root, dirs, files in os.walk(resolved):
        dirs[:] = [
            d
            for d in dirs
            if d not in (".git", "__pycache__", "node_modules", ".venv", "venv")
        ]
        for fname in files:
            if not fnmatch.fnmatch(fname, file_pattern):
                continue
            full_path = Path(root) / fname
            if not is_text_file(full_path):
                continue
            try:
                lines = full_path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines):
                if regex.search(line):
                    rel = full_path.relative_to(resolved)
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    snippet_lines = []
                    for j in range(start, end):
                        prefix = ">" if j == i else " "
                        snippet_lines.append(f"{prefix} {j+1}: {lines[j]}")
                    results.append(f"{rel}:\n" + "\n".join(snippet_lines))
                    count += 1
                    if count >= 50:
                        results.append("... (truncated at 50 matches)")
                        return "\n\n".join(results)
    if not results:
        return f"No matches for '{pattern}' in {directory}"
    return "\n\n".join(results)


def register_filesystem_tools(registry: object) -> None:
    from bedrock_code.tools.registry import ToolSpec

    registry.register(ToolSpec(
        name="read_file",
        description="Read the contents of a file at the given path. Returns the file content as text.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file (absolute or relative to cwd)"},
            },
            "required": ["path"],
        },
        handler=read_file,
        requires_permission=False,
    ))

    registry.register(ToolSpec(
        name="write_file",
        description="Write content to a file, creating it or overwriting it. Ask permission before using.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to write to"},
                "content": {"type": "string", "description": "Full content to write"},
            },
            "required": ["path", "content"],
        },
        handler=write_file,
        requires_permission=True,
    ))

    registry.register(ToolSpec(
        name="list_directory",
        description="List files and directories in a directory tree.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path (default: current directory)", "default": "."},
                "max_depth": {"type": "integer", "description": "Max depth to traverse (default: 2)", "default": 2},
            },
        },
        handler=list_directory,
        requires_permission=False,
    ))

    registry.register(ToolSpec(
        name="search_files",
        description="Search for files matching a glob pattern (e.g. '*.py', '**/*.ts').",
        input_schema={
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern to match filenames"},
                "directory": {"type": "string", "description": "Directory to search in (default: cwd)", "default": "."},
            },
            "required": ["pattern"],
        },
        handler=search_files,
        requires_permission=False,
    ))

    registry.register(ToolSpec(
        name="grep_files",
        description="Search for a regex pattern in file contents. Returns matching lines with context.",
        input_schema={
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern to search for"},
                "directory": {"type": "string", "description": "Directory to search in", "default": "."},
                "file_pattern": {"type": "string", "description": "Glob filter for filenames (e.g. '*.py')", "default": "*"},
                "context_lines": {"type": "integer", "description": "Lines of context around matches", "default": 2},
            },
            "required": ["pattern"],
        },
        handler=grep_files,
        requires_permission=False,
    ))
