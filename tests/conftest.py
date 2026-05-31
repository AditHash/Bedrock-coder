import pytest


@pytest.fixture
def sample_config(tmp_path):
    from bedrock_code.core.config import Config, DEFAULT_CONFIG
    import copy
    return Config(copy.deepcopy(DEFAULT_CONFIG))


@pytest.fixture
def tool_registry():
    from bedrock_code.tools.registry import ToolRegistry
    from bedrock_code.tools.filesystem import register_filesystem_tools
    from bedrock_code.tools.shell import register_shell_tools
    reg = ToolRegistry()
    register_filesystem_tools(reg)
    register_shell_tools(reg)
    return reg
