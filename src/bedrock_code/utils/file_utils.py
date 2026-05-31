from __future__ import annotations

import os
from pathlib import Path


def safe_resolve(path: str, base: Path | None = None) -> Path:
    """Resolve a path safely, relative to base (cwd if not provided)."""
    p = Path(path)
    if not p.is_absolute():
        p = (base or Path.cwd()) / p
    return p.resolve()


def is_text_file(path: Path, sample_bytes: int = 8192) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(sample_bytes)
        chunk.decode("utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False


def read_gitignore_patterns(directory: Path) -> list[str]:
    gitignore = directory / ".gitignore"
    if not gitignore.exists():
        return []
    patterns: list[str] = []
    for line in gitignore.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def truncate_content(content: str, max_chars: int = 100_000) -> str:
    if len(content) <= max_chars:
        return content
    half = max_chars // 2
    return (
        content[:half]
        + f"\n\n... [truncated {len(content) - max_chars} chars] ...\n\n"
        + content[-half:]
    )


def get_file_tree(directory: Path, max_depth: int = 3, max_files: int = 200) -> list[str]:
    lines: list[str] = []
    count = 0

    def _walk(d: Path, prefix: str, depth: int) -> None:
        nonlocal count
        if depth > max_depth or count >= max_files:
            return
        try:
            entries = sorted(d.iterdir(), key=lambda e: (e.is_file(), e.name))
        except PermissionError:
            return
        for i, entry in enumerate(entries):
            if entry.name.startswith(".") or entry.name in ("__pycache__", "node_modules", ".git"):
                continue
            connector = "└── " if i == len(entries) - 1 else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            count += 1
            if count >= max_files:
                lines.append(f"{prefix}    ... (truncated)")
                return
            if entry.is_dir():
                extension = "    " if i == len(entries) - 1 else "│   "
                _walk(entry, prefix + extension, depth + 1)

    lines.append(str(directory))
    _walk(directory, "", 1)
    return lines
