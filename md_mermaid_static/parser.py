import re
import yaml
from typing import List, Tuple, Dict, Any
from .models import MermaidBlock, MermaidConfig, Theme

class MarkdownParser:
    """Markdown 解析器"""
    
    # 支持标准的 ```mermaid 格式
    MERMAID_BLOCK_PATTERN = re.compile(
        r"```mermaid\n(.*?)\n```",
        re.DOTALL
    )
    
    # 支持 GitHub 风格的 ```mermaid 格式，带有额外的缩进
    GITHUB_MERMAID_PATTERN = re.compile(
        r"```mermaid\s*\n(.*?)\n\s*```",
        re.DOTALL
    )
    
    # 支持 Mermaid 的 directive 语法
    MERMAID_DIRECTIVE_PATTERN = re.compile(
        r":::mermaid\s*\n(.*?)\n:::",
        re.DOTALL
    )
    
    @staticmethod
    def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
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
    
    @staticmethod
    def _normalize_config_keys(config: Dict[str, Any]) -> Dict[str, Any]:
        """标准化配置键名（将连字符转换为下划线）"""
        normalized_config = {}
        for key, value in config.items():
            # 将连字符转换为下划线（例如 render-theme -> render_theme）
            normalized_key = key.replace('-', '_')
            
            # 特殊处理 theme 字段名称
            if normalized_key == 'theme':
                normalized_key = 'render_theme'
                
            # 如果是主题，确保使用枚举值
            if normalized_key == 'render_theme' and isinstance(value, str):
                try:
                    value = Theme(value.lower())
                except ValueError:
                    # 如果不是有效的主题，使用默认主题
                    value = Theme.DEFAULT
                    
            normalized_config[normalized_key] = value
            
        return normalized_config
    
    def _extract_blocks(self, pattern: re.Pattern, markdown_content: str) -> List[MermaidBlock]:
        """从 Markdown 内容中提取 Mermaid 代码块"""
        blocks = []
        
        for match in pattern.finditer(markdown_content):
            content = match.group(1)
            config_dict, mermaid_content = self.parse_frontmatter(content)
            
            # 标准化配置键
            normalized_config = self._normalize_config_keys(config_dict)
            
            block = MermaidBlock(
                content=mermaid_content.strip(),
                config=MermaidConfig(**normalized_config),
                line_start=markdown_content.count('\n', 0, match.start()) + 1,
                line_end=markdown_content.count('\n', 0, match.end()) + 1
            )
            blocks.append(block)
            
        return blocks
    
    def find_mermaid_blocks(self, markdown_content: str) -> List[MermaidBlock]:
        """在 Markdown 内容中查找所有 Mermaid 代码块"""
        blocks = []
        
        # 查找标准格式的代码块
        standard_blocks = self._extract_blocks(self.MERMAID_BLOCK_PATTERN, markdown_content)
        blocks.extend(standard_blocks)
        
        # 查找 GitHub 风格的代码块
        github_blocks = self._extract_blocks(self.GITHUB_MERMAID_PATTERN, markdown_content)
        # 排除已经匹配的块（避免重复）
        github_blocks = [b for b in github_blocks if b not in blocks]
        blocks.extend(github_blocks)
        
        # 查找 directive 风格的代码块
        directive_blocks = self._extract_blocks(self.MERMAID_DIRECTIVE_PATTERN, markdown_content)
        blocks.extend(directive_blocks)
        
        return blocks 