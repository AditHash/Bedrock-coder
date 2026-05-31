from __future__ import annotations

from pathlib import Path

from bedrock_code.utils.diff import compute_unified_diff, has_changes
from bedrock_code.utils.file_utils import safe_resolve


async def edit_file(path: str, old_string: str, new_string: str) -> str:
    """Replace old_string with new_string in file. The old_string must match exactly."""
    resolved = safe_resolve(path)
    if not resolved.exists():
        return f"Error: File not found: {path}"
    try:
        content = resolved.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return f"Error reading file: {e}"

    if old_string not in content:
        return f"Error: The specified text was not found in {path}. Make sure it matches exactly (including whitespace)."

    count = content.count(old_string)
    if count > 1:
        return f"Error: The text appears {count} times in {path}. Provide more surrounding context to make it unique."

    new_content = content.replace(old_string, new_string, 1)
    diff = compute_unified_diff(content, new_content, filename=Path(path).name)

    try:
        resolved.write_text(new_content, encoding="utf-8")
    except OSError as e:
        return f"Error writing file: {e}"

    lines_changed = diff.count("\n+") + diff.count("\n-")
    return f"Edited {path} ({lines_changed} line changes)\n\nDiff:\n{diff}"


async def replace_file_section(path: str, start_line: int, end_line: int, new_content: str) -> str:
    """Replace lines start_line to end_line (1-indexed, inclusive) with new_content."""
    resolved = safe_resolve(path)
    if not resolved.exists():
        return f"Error: File not found: {path}"
    try:
        lines = resolved.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    except OSError as e:
        return f"Error reading file: {e}"

    if start_line < 1 or end_line > len(lines) or start_line > end_line:
        return f"Error: Line range {start_line}-{end_line} is invalid for file with {len(lines)} lines."

    new_lines = new_content.splitlines(keepends=True)
    if new_content and not new_content.endswith("\n"):
        new_lines[-1] += "\n"

    updated = lines[: start_line - 1] + new_lines + lines[end_line:]
    old_text = "".join(lines)
    new_text = "".join(updated)
    diff = compute_unified_diff(old_text, new_text, filename=Path(path).name)

    try:
        resolved.write_text(new_text, encoding="utf-8")
    except OSError as e:
        return f"Error writing file: {e}"

    return f"Replaced lines {start_line}-{end_line} in {path}\n\nDiff:\n{diff}"


def register_editor_tools(registry: object) -> None:
    from bedrock_code.tools.registry import ToolSpec

    registry.register(ToolSpec(
        name="edit_file",
        description=(
            "Edit a file by replacing an exact string with a new string. "
            "The old_string must match exactly (including whitespace and indentation). "
            "Always read the file first to get the exact text."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to edit"},
                "old_string": {"type": "string", "description": "Exact text to find and replace"},
                "new_string": {"type": "string", "description": "Text to replace it with"},
            },
            "required": ["path", "old_string", "new_string"],
        },
        handler=edit_file,
        requires_permission=True,
    ))
