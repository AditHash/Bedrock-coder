import pytest
from pathlib import Path


@pytest.mark.asyncio
async def test_read_file(tmp_path):
    from bedrock_code.tools.filesystem import read_file
    f = tmp_path / "hello.txt"
    f.write_text("Hello, world!")
    result = await read_file(str(f))
    assert "Hello, world!" in result


@pytest.mark.asyncio
async def test_read_missing_file():
    from bedrock_code.tools.filesystem import read_file
    result = await read_file("/nonexistent/path/file.txt")
    assert "Error" in result


@pytest.mark.asyncio
async def test_write_file(tmp_path):
    from bedrock_code.tools.filesystem import write_file
    out = tmp_path / "out.txt"
    result = await write_file(str(out), "content here")
    assert "Written" in result
    assert out.read_text() == "content here"


@pytest.mark.asyncio
async def test_edit_file(tmp_path):
    from bedrock_code.tools.editor import edit_file
    f = tmp_path / "edit.py"
    f.write_text("def foo():\n    pass\n")
    result = await edit_file(str(f), "    pass", "    return 42")
    assert "Edited" in result
    assert "return 42" in f.read_text()


@pytest.mark.asyncio
async def test_edit_file_not_found():
    from bedrock_code.tools.editor import edit_file
    result = await edit_file("/no/such/file.py", "old", "new")
    assert "Error" in result


@pytest.mark.asyncio
async def test_edit_file_string_not_found(tmp_path):
    from bedrock_code.tools.editor import edit_file
    f = tmp_path / "test.py"
    f.write_text("hello world")
    result = await edit_file(str(f), "nonexistent string", "replacement")
    assert "Error" in result


@pytest.mark.asyncio
async def test_bash_exec_simple():
    from bedrock_code.tools.shell import bash_exec
    result = await bash_exec("echo hello")
    assert "hello" in result


@pytest.mark.asyncio
async def test_bash_exec_timeout():
    from bedrock_code.tools.shell import bash_exec
    import sys
    if sys.platform == "win32":
        result = await bash_exec("ping -n 10 127.0.0.1", timeout=1)
    else:
        result = await bash_exec("sleep 10", timeout=1)
    assert "timed out" in result.lower()


def test_safe_command_detection():
    from bedrock_code.tools.shell import is_safe_command
    assert is_safe_command("ls -la") is True
    assert is_safe_command("git status") is True
    assert is_safe_command("rm -rf /") is False
    assert is_safe_command("cat main.py") is True


def test_tool_registry():
    from bedrock_code.tools.registry import ToolRegistry, ToolSpec

    async def dummy(**kwargs):
        return "ok"

    reg = ToolRegistry()
    reg.register(ToolSpec(
        name="dummy",
        description="A dummy tool",
        input_schema={"type": "object", "properties": {}},
        handler=dummy,
    ))
    assert reg.get("dummy") is not None
    assert reg.get("missing") is None
    config = reg.bedrock_tool_config()
    assert len(config["tools"]) == 1


def test_diff_computation():
    from bedrock_code.utils.diff import compute_unified_diff, has_changes
    diff = compute_unified_diff("old\n", "new\n", "test.txt")
    assert "-old" in diff
    assert "+new" in diff
    assert has_changes("a", "b") is True
    assert has_changes("same", "same") is False


def test_config_defaults():
    from bedrock_code.core.config import Config, DEFAULT_CONFIG
    import copy
    c = Config(copy.deepcopy(DEFAULT_CONFIG))
    assert c.aws_region == "ap-south-1"
    assert "claude" in c.default_model
    assert c.max_tokens == 8192
    assert c.permission_for("read_file") == "allow"
    assert c.permission_for("bash_exec") == "ask"
