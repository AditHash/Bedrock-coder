from __future__ import annotations

from pathlib import Path


GLOBAL_MEMORY_FILE = Path.home() / ".bedrock-code" / "MEMORY.md"


def load_memory(project_dir: Path | None = None) -> str:
    """Load MEMORY.md from project dir (and parents) and global ~/.bedrock-code/MEMORY.md."""
    sections: list[str] = []

    global_content = _read_file(GLOBAL_MEMORY_FILE)
    if global_content:
        sections.append(f"## Global Memory\n\n{global_content}")

    if project_dir:
        project_content = _find_project_memory(project_dir)
        if project_content:
            sections.append(f"## Project Memory\n\n{project_content}")

    return "\n\n".join(sections)


def _read_file(path: Path) -> str:
    try:
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
    except OSError:
        pass
    return ""


def _find_project_memory(start: Path) -> str:
    """Walk up directory tree to find MEMORY.md."""
    current = start.resolve()
    home = Path.home()
    while current >= home:
        candidate = current / "MEMORY.md"
        content = _read_file(candidate)
        if content:
            return content
        if current == current.parent:
            break
        current = current.parent
    return ""


def build_system_prompt(
    memory: str,
    cwd: str,
    model_id: str,
    git_info: str = "",
    platform: str = "",
) -> str:
    memory_section = f"\n\n{memory}" if memory else ""

    return f"""You are bedrock-code, an AI coding assistant powered by AWS Bedrock.
You help with software engineering tasks: reading and editing files, running shell commands, \
explaining code, debugging, searching the web, and answering technical questions.{memory_section}

## Environment
- Working directory: {cwd}
- Platform: {platform}
- Git repository: {git_info or 'unknown'}
- Active model: {model_id}

## Behaviour rules — follow these strictly

**Be direct. Act immediately.**
- Never narrate your reasoning or describe what you are about to do. Just do it.
- Never say "I will now call the tool" or "The user wants me to...". Call the tool.
- Never ask for permission before using read-only tools (read_file, list_directory, git_status, web_search).
- For write/edit/shell: show what you will do and proceed unless it is clearly destructive.

**Use tools proactively.**
- When asked about files or code → call read_file or list_directory immediately.
- When asked to search the web → call web_search immediately with the query.
- When asked to "read the codebase" → call list_directory then read the relevant files.
- Chain multiple tool calls in one turn when needed.

**Keep responses concise.**
- Use markdown and fenced code blocks for code.
- Don't repeat what the tool already returned — summarise or highlight key points.
- Prefer short answers unless depth is explicitly asked for.

**Multi-step tasks:** use todo_write to track steps, mark each completed as you go.
"""
