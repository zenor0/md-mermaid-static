from pathlib import Path
from typing import List, Tuple
from rich.console import Console
from rich.progress import Progress

from .parser import MarkdownParser
from .renderer import MermaidRenderer
from .models import MermaidBlock, CLIConfig

console = Console()

class MarkdownProcessor:
    """Markdown 处理器"""
    
    def __init__(self, input_file: str, cli_config: CLIConfig):
        self.input_file = Path(input_file)
        self.output_dir = Path(cli_config.output_dir)
        self.cli_config = cli_config
        self.renderer = MermaidRenderer(cli_config.output_dir, cli_config)
        
    def process(self) -> Path:
        """处理 Markdown 文件"""
        console.print(f"[blue]开始处理文件: {self.input_file}[/blue]")
        
        # 读取输入文件
        content = self.input_file.read_text(encoding="utf-8")
        
        # 解析 Mermaid 代码块
        parser = MarkdownParser()
        blocks = parser.find_mermaid_blocks(content)
        
        if not blocks:
            console.print("[yellow]未找到 Mermaid 代码块[/yellow]")
            return self._save_output(content)
            
        console.print(f"[green]找到 {len(blocks)} 个 Mermaid 代码块[/green]")
        
        # 渲染所有代码块
        with Progress() as progress:
            task = progress.add_task("[cyan]渲染图表...", total=len(blocks))
            
            # 并发或顺序处理所有代码块
            rendered_blocks = self.renderer.render_blocks(blocks)
            
            # 更新进度条
            progress.update(task, completed=len(blocks))
        
        # 更新 Markdown 内容
        new_content = self._replace_blocks(content, rendered_blocks)
        
        # 保存输出文件
        output_file = self._save_output(new_content)
        console.print(f"[green]处理完成! 输出文件: {output_file}[/green]")
        
        return output_file
        
    def _replace_blocks(self, content: str, rendered_blocks: List[Tuple[MermaidBlock, Path]]) -> str:
        """替换 Markdown 中的 Mermaid 代码块"""
        lines = content.split('\n')
        offset = 0
        
        for block, image_path in rendered_blocks:
            # 检查图像路径是否为空
            if image_path is None:
                console.print(f"[yellow]警告: 第 {block.line_start} 行的图表渲染失败，保留原始代码块[/yellow]")
                continue
                
            # 计算相对路径
            rel_path = image_path.relative_to(self.output_dir)
            
            # 创建新的图片引用
            image_ref = f"![{block.config.caption or ''}]({rel_path})"
            
            # 替换原始代码块
            start_idx = block.line_start - 1 + offset
            end_idx = block.line_end - 1 + offset
            lines[start_idx:end_idx + 1] = [image_ref]
            
            # 更新偏移量
            offset += 1 - (end_idx - start_idx + 1)
            
        return '\n'.join(lines)
        
    def _save_output(self, content: str) -> Path:
        """保存输出文件"""
        output_file = self.output_dir / self.input_file.name
        output_file.write_text(content, encoding="utf-8")
        return output_file 