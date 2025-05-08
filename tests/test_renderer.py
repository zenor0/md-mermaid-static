import pytest
from pathlib import Path
import tempfile
from md_mermaid_static.core.renderer import MermaidRenderer
from md_mermaid_static.models import MermaidBlock, MermaidConfig


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def renderer(temp_dir):
    """创建渲染器实例"""
    return MermaidRenderer(str(temp_dir))


def test_renderer_initialization(temp_dir):
    """测试渲染器初始化"""
    renderer = MermaidRenderer(str(temp_dir))
    assert renderer.output_dir == temp_dir
    assert renderer.media_dir.exists()
    assert renderer.media_dir == temp_dir / "media"


def test_get_mermaid_cli_cmd(renderer):
    """测试获取 mermaid-cli 命令"""
    cmd = renderer._get_mermaid_cli_cmd()
    assert cmd in ["pnpx", "npx"]


def test_check_command_exists(renderer):
    """测试命令存在检查"""
    # 测试一个一定存在的命令
    assert renderer._check_command_exists("python")
    # 测试一个不存在的命令
    assert not renderer._check_command_exists("nonexistentcommand123")
