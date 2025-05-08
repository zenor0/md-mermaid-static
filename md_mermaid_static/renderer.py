import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
import pymupdf

from rich.console import Console
from .models import MermaidBlock

console = Console()

class MermaidRenderer:
    """Mermaid 图表渲染器"""
    
    def __init__(self, output_dir: str, enhance_svg: bool = False):
        self.output_dir = Path(output_dir)
        self.enhance_svg = enhance_svg
        self.media_dir = self.output_dir / "media"
        self.media_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_mermaid_cli_cmd(self) -> str:
        """获取可用的 mermaid-cli 命令"""
        if self._check_command_exists("pnpx"):
            return "pnpx"
        return "npx"
        
    def _check_command_exists(self, cmd: str) -> bool:
        """检查命令是否存在"""
        try:
            subprocess.run([cmd, "--version"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False
            
    def render_block(self, block: MermaidBlock, index: int) -> Optional[Path]:
        """渲染单个 Mermaid 代码块"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建临时的 mermaid 文件
            mermaid_file = Path(temp_dir) / "diagram.mmd"
            mermaid_file.write_text(block.content)
            
            # 确定输出格式和文件
            output_format = "pdf" if self.enhance_svg else "svg"
            temp_output = Path(temp_dir) / f"output.{output_format}"
            
            # 构建渲染命令
            cli_cmd = self._get_mermaid_cli_cmd()
            cmd = [
                cli_cmd, "@mermaid-js/mermaid-cli",
                "-i", str(mermaid_file),
                "-o", str(temp_output)
            ]
            
            # 添加主题配置
            if block.config.render_theme:
                theme_dir = Path("themes") / block.config.render_theme
                if theme_dir.exists():
                    config_file = theme_dir / "config.json"
                    css_file = theme_dir / "style.css"
                    if config_file.exists():
                        cmd.extend(["-c", str(config_file)])
                    if css_file.exists():
                        cmd.extend(["--cssFile", str(css_file)])
            
            try:
                # 执行渲染命令
                result = subprocess.run(cmd, 
                                     capture_output=True, 
                                     text=True)
                if result.returncode != 0:
                    console.print(f"[red]渲染失败: {result.stderr}[/red]")
                    return None
                
                # 如果需要增强 SVG
                if self.enhance_svg:
                    final_output = self.media_dir / f"diagram_{index}.svg"
                    self._convert_pdf_to_svg(temp_output, final_output)
                else:
                    final_output = self.media_dir / f"diagram_{index}.svg"
                    temp_output.rename(final_output)
                
                return final_output
                
            except Exception as e:
                console.print(f"[red]渲染过程出错: {str(e)}[/red]")
                return None
                
    def _convert_pdf_to_svg(self, pdf_path: Path, svg_path: Path):
        """将 PDF 转换为 SVG"""
        doc = pymupdf.open(str(pdf_path))
        page = doc[0]  # 获取第一页
        svg_data = page.get_svg_image()
        svg_path.write_text(svg_data, encoding="utf-8")
        doc.close() 