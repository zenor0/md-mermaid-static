import pytest
from pathlib import Path
import tempfile
import shutil
from md_mermaid_static.processor import MarkdownProcessor

@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

@pytest.fixture
def sample_md_file(temp_dir):
    """创建示例 Markdown 文件"""
    content = """# 测试文档

```mermaid
---
caption: 流程图
---
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
```

一些文本内容

```mermaid
sequenceDiagram
    Alice->>John: Hello John
    John-->>Alice: Hi Alice
```
"""
    md_file = temp_dir / "test.md"
    md_file.write_text(content)
    return md_file

def test_processor_initialization(temp_dir, sample_md_file):
    """测试处理器初始化"""
    processor = MarkdownProcessor(str(sample_md_file), str(temp_dir))
    assert processor.input_file == sample_md_file
    assert processor.output_dir == temp_dir

def test_process_markdown_without_mermaid(temp_dir):
    """测试处理不包含 Mermaid 图表的 Markdown"""
    content = "# 测试文档\n\n这是一个普通文档"
    md_file = temp_dir / "no_mermaid.md"
    md_file.write_text(content)
    
    processor = MarkdownProcessor(str(md_file), str(temp_dir))
    output_file = processor.process()
    
    assert output_file.exists()
    assert output_file.read_text() == content

def test_replace_blocks():
    """测试代码块替换逻辑"""
    content = """# 测试

```mermaid
graph TD
    A --> B
```

文本
"""
    processor = MarkdownProcessor("test.md", "output")
    blocks = [(
        MermaidBlock(
            content="graph TD\n    A --> B",
            config=MermaidConfig(caption="测试图"),
            line_start=3,
            line_end=5
        ),
        Path("output/media/test.svg")
    )]
    
    new_content = processor._replace_blocks(content, blocks)
    assert "![测试图](media/test.svg)" in new_content 