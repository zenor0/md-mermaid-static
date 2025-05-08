import click
from pathlib import Path
from rich.console import Console

from .processor import MarkdownProcessor

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
    '--enhance-svg',
    is_flag=True,
    help='是否通过 PDF 转换增强 SVG 质量'
)
def main(input_file: str, output_dir: str, enhance_svg: bool):
    """将 Markdown 文件中的 Mermaid 图表转换为静态图片。
    
    INPUT_FILE: 输入的 Markdown 文件路径
    """
    try:
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 处理文件
        processor = MarkdownProcessor(input_file, output_dir, enhance_svg)
        output_file = processor.process()
        
        console.print(f"[green]处理完成！输出文件：{output_file}[/green]")
        
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        raise click.Abort()

if __name__ == '__main__':
    main() 