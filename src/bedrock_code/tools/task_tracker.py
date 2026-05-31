from __future__ import annotations

import json
from pathlib import Path

_SESSION_TODOS: list[dict] = []
_PERSISTENT_FILE: Path | None = None


def set_persistent_file(path: Path) -> None:
    global _PERSISTENT_FILE
    _PERSISTENT_FILE = path
    if path.exists():
        try:
            _SESSION_TODOS.clear()
            _SESSION_TODOS.extend(json.loads(path.read_text()))
        except (json.JSONDecodeError, OSError):
            pass


def _save() -> None:
    if _PERSISTENT_FILE:
        try:
            _PERSISTENT_FILE.write_text(json.dumps(_SESSION_TODOS, indent=2))
        except OSError:
            pass


async def todo_read() -> str:
    if not _SESSION_TODOS:
        return "No todos yet."
    lines = []
    for i, todo in enumerate(_SESSION_TODOS, 1):
        status = todo.get("status", "pending")
        icon = {"pending": "○", "in_progress": "◐", "completed": "●"}.get(status, "○")
        lines.append(f"{icon} [{i}] {todo.get('title', '?')} — {status}")
    return "\n".join(lines)


async def todo_write(todos: list[dict]) -> str:
    _SESSION_TODOS.clear()
    _SESSION_TODOS.extend(todos)
    _save()
    return f"Updated {len(todos)} todos."


async def todo_update(index: int, status: str) -> str:
    if index < 1 or index > len(_SESSION_TODOS):
        return f"Error: Todo index {index} out of range."
    valid = ("pending", "in_progress", "completed")
    if status not in valid:
        return f"Error: status must be one of {valid}"
    _SESSION_TODOS[index - 1]["status"] = status
    _save()
    return f"Todo {index} updated to {status}."


def register_task_tools(registry: object) -> None:
    from bedrock_code.tools.registry import ToolSpec

    registry.register(ToolSpec(
        name="todo_read",
        description="Read the current session todo list.",
        input_schema={"type": "object", "properties": {}},
        handler=todo_read,
        requires_permission=False,
    ))

    registry.register(ToolSpec(
        name="todo_write",
        description="Overwrite the todo list with a new list of tasks.",
        input_schema={
            "type": "object",
            "properties": {
                "todos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                            },
                        },
                        "required": ["title", "status"],
                    },
                    "description": "List of todo items",
                }
            },
            "required": ["todos"],
        },
        handler=todo_write,
        requires_permission=False,
    ))

    registry.register(ToolSpec(
        name="todo_update",
        description="Update the status of a specific todo item by its 1-based index.",
        input_schema={
            "type": "object",
            "properties": {
                "index": {"type": "integer", "description": "1-based index of the todo"},
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed"],
                    "description": "New status",
                },
            },
            "required": ["index", "status"],
        },
        handler=todo_update,
        requires_permission=False,
    ))
