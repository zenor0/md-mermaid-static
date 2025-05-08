import os
import subprocess
import tempfile
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import pymupdf
from concurrent.futures import ThreadPoolExecutor

from rich.console import Console
from .models import MermaidBlock, MermaidRenderOptions, OutputFormat, Theme, CLIConfig

console = Console()

class MermaidRenderer:
    """Mermaid 图表渲染器"""
    
    def __init__(self, output_dir: str, cli_config: CLIConfig):
        self.output_dir = Path(output_dir)
        self.cli_config = cli_config
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
    
    def render_blocks(self, blocks: List[MermaidBlock]) -> List[Tuple[MermaidBlock, Optional[Path]]]:
        """渲染多个 Mermaid 代码块，支持并发处理"""
        if not blocks:
            return []
            
        if self.cli_config.concurrent and len(blocks) > 1:
            console.print(f"[blue]使用并发模式渲染 {len(blocks)} 个图表，最大并发数: {self.cli_config.max_workers}[/blue]")
            with ThreadPoolExecutor(max_workers=self.cli_config.max_workers) as executor:
                # 创建任务列表
                futures = []
                for i, block in enumerate(blocks):
                    futures.append(executor.submit(self.render_block, block, i))
                
                # 收集结果
                results = []
                for i, future in enumerate(futures):
                    try:
                        output_path = future.result()
                        results.append((blocks[i], output_path))
                    except Exception as e:
                        console.print(f"[red]并发渲染第 {i+1} 个图表时出错: {str(e)}[/red]")
                        results.append((blocks[i], None))
                        
                return results
        else:
            # 顺序处理
            results = []
            for i, block in enumerate(blocks):
                try:
                    output_path = self.render_block(block, i)
                    results.append((block, output_path))
                except Exception as e:
                    console.print(f"[red]渲染第 {i+1} 个图表时出错: {str(e)}[/red]")
                    results.append((block, None))
            return results
            
    def render_block(self, block: MermaidBlock, index: int) -> Optional[Path]:
        """渲染单个 Mermaid 代码块"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建临时的 mermaid 文件
            mermaid_file = Path(temp_dir) / "diagram.mmd"
            mermaid_file.write_text(block.content)
            
            # 生成MD5哈希作为文件名
            md5_hash = hashlib.md5(block.content.encode('utf-8')).hexdigest()
            
            # 获取渲染选项，优先使用块级配置，然后使用CLI全局配置
            render_options = block.get_render_options()
            
            # 合并CLI全局配置中的缺失项
            if not render_options.theme and self.cli_config.theme:
                render_options.theme = self.cli_config.theme
            if not render_options.config_file and self.cli_config.config_file:
                render_options.config_file = self.cli_config.config_file
            if not render_options.css_file and self.cli_config.css_file:
                render_options.css_file = self.cli_config.css_file
                
            # 确定输出格式
            output_format = self.cli_config.output_format
            
            # 临时输出文件
            temp_output = Path(temp_dir) / f"output.{output_format.value}"
            
            # 构建渲染命令
            cmd = self._build_render_command(mermaid_file, temp_output, render_options)
            
            try:
                # 执行渲染命令
                result = subprocess.run(cmd, 
                                     capture_output=True, 
                                     text=True)
                if result.returncode != 0:
                    console.print(f"[red]渲染失败: {result.stderr}[/red]")
                    return None
                
                # 最终输出文件
                final_output = self.media_dir / f"mermaid_{md5_hash}.{output_format.value}"
                
                # 处理PDF到其他格式的转换（如果需要）
                if output_format == OutputFormat.PDF and self.cli_config.output_format != OutputFormat.PDF:
                    self._convert_pdf_to_other_format(temp_output, final_output, self.cli_config.output_format)
                else:
                    # 直接复制文件
                    import shutil
                    shutil.copy2(temp_output, final_output)
                
                return final_output
                
            except Exception as e:
                console.print(f"[red]渲染过程出错: {str(e)}[/red]")
                return None
                
    def _build_render_command(self, input_file: Path, output_file: Path, options: MermaidRenderOptions) -> List[str]:
        """构建 mermaid-cli 命令"""
        cli_cmd = self._get_mermaid_cli_cmd()
        cmd = [
            cli_cmd, "@mermaid-js/mermaid-cli",
            "-i", str(input_file),
            "-o", str(output_file)
        ]
        
        # 添加主题
        if options.theme:
            cmd.extend(["-t", options.theme.value])
            
        # 添加尺寸
        if options.width:
            cmd.extend(["-w", str(options.width)])
        if options.height:
            cmd.extend(["-H", str(options.height)])
            
        # 添加背景色
        if options.background_color:
            cmd.extend(["-b", options.background_color])
            
        # 添加配置文件
        if options.config_file:
            config_path = Path(options.config_file)
            if config_path.exists():
                cmd.extend(["-c", str(config_path)])
                
        # 添加CSS文件
        if options.css_file:
            css_path = Path(options.css_file)
            if css_path.exists():
                cmd.extend(["-C", str(css_path)])
                
        # 添加缩放比例
        if options.scale:
            cmd.extend(["-s", str(options.scale)])
            
        # 添加PDF适配选项
        if options.pdf_fit:
            cmd.append("-f")
            
        # 添加SVG ID
        if options.svg_id:
            cmd.extend(["-I", options.svg_id])
            
        return cmd
                
    def _convert_pdf_to_svg(self, pdf_path: Path, svg_path: Path):
        """将 PDF 转换为 SVG"""
        doc = pymupdf.open(str(pdf_path))
        page = doc[0]  # 获取第一页
        svg_data = page.get_svg_image()
        svg_path.write_text(svg_data, encoding="utf-8")
        doc.close()
        
    def _convert_pdf_to_png(self, pdf_path: Path, png_path: Path, dpi: int = 300):
        """将 PDF 转换为 PNG"""
        doc = pymupdf.open(str(pdf_path))
        page = doc[0]  # 获取第一页
        pix = page.get_pixmap(dpi=dpi)
        pix.save(str(png_path))
        doc.close()
        
    def _convert_pdf_to_other_format(self, pdf_path: Path, output_path: Path, format: OutputFormat):
        """将 PDF 转换为其他格式"""
        if format == OutputFormat.SVG:
            self._convert_pdf_to_svg(pdf_path, output_path)
        elif format == OutputFormat.PNG:
            self._convert_pdf_to_png(pdf_path, output_path)
        else:
            # 直接复制
            import shutil
            shutil.copy2(pdf_path, output_path) 