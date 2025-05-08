import click
from pathlib import Path
from rich.console import Console
import os
import multiprocessing

from .processor import MarkdownProcessor
from .models import CLIConfig, OutputFormat, Theme

console = Console()

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option(
    '--output-dir', '-o',
    type=click.Path(),
    default='output',
    help='输出目录路径'
)
@click.option(
    '--output-format', '-e',
    type=click.Choice(['svg', 'png', 'pdf']),
    default='svg',
    help='输出图片格式 (svg, png, pdf)'
)
@click.option(
    '--theme', '-t',
    type=click.Choice(['default', 'forest', 'dark', 'neutral']),
    default='default',
    help='Mermaid 主题'
)
@click.option(
    '--width', '-w',
    type=int,
    default=800,
    help='图表宽度（像素）'
)
@click.option(
    '--height', '-H',
    type=int,
    default=600,
    help='图表高度（像素）'
)
@click.option(
    '--background-color', '-b',
    type=str,
    default='white',
    help='背景颜色（如transparent, red, #F0F0F0）'
)
@click.option(
    '--scale', '-s',
    type=float,
    default=1.0,
    help='缩放比例'
)
@click.option(
    '--config-file', '-c',
    type=click.Path(exists=True),
    help='Mermaid JSON配置文件路径'
)
@click.option(
    '--css-file', '-C',
    type=click.Path(exists=True),
    help='自定义CSS文件路径'
)
@click.option(
    '--pdf-fit', '-f',
    is_flag=True,
    help='将PDF缩放到适合图表大小'
)
@click.option(
    '--concurrent', '-p',
    is_flag=True,
    help='启用并发渲染以加速处理'
)
@click.option(
    '--max-workers', '-j',
    type=int,
    default=0,
    help='并发渲染的最大工作进程数（默认为CPU核心数）'
)
def main(
    input_file: str, 
    output_dir: str, 
    output_format: str, 
    theme: str, 
    width: int, 
    height: int,
    background_color: str, 
    scale: float, 
    config_file: str, 
    css_file: str, 
    pdf_fit: bool,
    concurrent: bool,
    max_workers: int
):
    """将 Markdown 文件中的 Mermaid 图表转换为静态图片。
    
    INPUT_FILE: 输入的 Markdown 文件路径
    """
    try:
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 如果max_workers为0，使用CPU数量
        if max_workers <= 0:
            max_workers = os.cpu_count() or 4
        
        # 创建CLI配置
        cli_config = CLIConfig(
            output_dir=output_dir,
            output_format=OutputFormat(output_format),
            theme=Theme(theme),
            width=width,
            height=height,
            background_color=background_color,
            scale=scale,
            config_file=config_file,
            css_file=css_file,
            pdf_fit=pdf_fit,
            concurrent=concurrent,
            max_workers=max_workers
        )
        
        # 处理文件
        processor = MarkdownProcessor(input_file, cli_config)
        output_file = processor.process()
        
        console.print(f"[green]处理完成！输出文件：{output_file}[/green]")
        
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        raise click.Abort()

if __name__ == '__main__':
    main() 