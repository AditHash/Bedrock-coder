from __future__ import annotations

import difflib


def compute_unified_diff(
    old_text: str,
    new_text: str,
    filename: str = "file",
    context_lines: int = 3,
) -> str:
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=context_lines,
    )
    return "".join(diff)


def has_changes(old_text: str, new_text: str) -> bool:
    return old_text != new_text
