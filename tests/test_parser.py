import pytest
from md_mermaid_static.core.parser import MarkdownParser
from md_mermaid_static.models import MermaidBlock, MermaidConfig


def test_parse_frontmatter():
    """测试 frontmatter 解析"""
    parser = MarkdownParser()
    content = """---
caption: 测试图表
render-theme: dark
---
graph TD
    A --> B"""

    config, mermaid_content = parser.parse_frontmatter(content)
    assert config == {"caption": "测试图表", "render-theme": "dark"}
    assert mermaid_content.strip() == "graph TD\n    A --> B"


def test_find_mermaid_blocks():
    """测试 Mermaid 代码块查找"""
    markdown_content = """# 测试文档

```mermaid
---
caption: 图表1
---
graph TD
    A --> B
```

一些文本

```mermaid
sequenceDiagram
    Alice->>John: Hello John
```
"""

    parser = MarkdownParser()
    blocks = parser.find_mermaid_blocks(markdown_content)

    assert len(blocks) == 2
    assert isinstance(blocks[0], MermaidBlock)
    assert blocks[0].config.caption == "图表1"
    assert "graph TD" in blocks[0].content
    assert "sequenceDiagram" in blocks[1].content


def test_empty_markdown():
    """测试空 Markdown 文件"""
    parser = MarkdownParser()
    blocks = parser.find_mermaid_blocks("")
    assert len(blocks) == 0
