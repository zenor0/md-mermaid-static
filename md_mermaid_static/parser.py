import re
import yaml
from typing import List, Tuple
from .models import MermaidBlock, MermaidConfig

class MarkdownParser:
    """Markdown 解析器"""
    
    MERMAID_BLOCK_PATTERN = re.compile(
        r"```mermaid\n(.*?)\n```",
        re.DOTALL
    )
    
    @staticmethod
    def parse_frontmatter(content: str) -> Tuple[dict, str]:
        """解析 frontmatter 和实际内容"""
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                try:
                    config = yaml.safe_load(parts[1])
                    return config or {}, parts[2]
                except yaml.YAMLError:
                    return {}, content
        return {}, content
    
    @classmethod
    def find_mermaid_blocks(cls, markdown_content: str) -> List[MermaidBlock]:
        """在 Markdown 内容中查找所有 Mermaid 代码块"""
        blocks = []
        
        for match in cls.MERMAID_BLOCK_PATTERN.finditer(markdown_content):
            content = match.group(1)
            config_dict, mermaid_content = cls.parse_frontmatter(content)
            
            block = MermaidBlock(
                content=mermaid_content.strip(),
                config=MermaidConfig(**config_dict),
                line_start=markdown_content.count('\n', 0, match.start()) + 1,
                line_end=markdown_content.count('\n', 0, match.end()) + 1
            )
            blocks.append(block)
            
        return blocks 