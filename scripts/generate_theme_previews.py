#!/usr/bin/env python3
"""
生成Mermaid主题预览图像的脚本
"""

import argparse
import concurrent.futures
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_mermaid_static.config.env import get_mermaid_cli_package
from md_mermaid_static.utils.theme_manager import get_theme_manager

# 示例图表内容
FLOWCHART_EXAMPLE = """
graph TD
    A[开始] --> B{是否继续?}
    B -->|是| C[处理]
    B -->|否| D[结束]
    C --> B
"""

SEQUENCE_EXAMPLE = """
sequenceDiagram
    participant 用户
    participant 系统
    用户->>系统: 请求数据
    系统-->>用户: 返回数据
    用户->>系统: 处理数据
    系统-->>用户: 确认处理完成
"""

CLASS_EXAMPLE = """
classDiagram
    class Animal {
        +name: string
        +age: int
        +makeSound(): void
    }
    class Dog {
        +breed: string
        +bark(): void
    }
    class Cat {
        +color: string
        +meow(): void
    }
    Animal <|-- Dog
    Animal <|-- Cat
"""

# 预览图像的宽度和高度
PREVIEW_WIDTH = 800
PREVIEW_HEIGHT = 600
PREIVEW_BACKGROUND_COLOR = "transparent"


def create_temp_mermaid_file(content, theme_name, theme_files):
    """创建临时的Mermaid文件"""
    config_file = theme_files.get("config")
    css_file = theme_files.get("css")

    with tempfile.NamedTemporaryFile(
        suffix=".mmd", delete=False, mode="w", encoding="utf-8"
    ) as f:
        f.write(content)
        temp_file = f.name

    return temp_file, config_file, css_file


def render_mermaid(mermaid_file, output_file, config_file=None, css_file=None):
    """使用mermaid-cli渲染Mermaid图表"""
    cmd = [
        "pnpx",
        get_mermaid_cli_package(),
        "-i",
        mermaid_file,
        "-o",
        output_file,
    ]

    # 添加配置文件
    if config_file:
        cmd.extend(["-c", str(config_file)])

    # 添加CSS文件
    if css_file:
        cmd.extend(["-C", str(css_file)])

    # 添加宽度和高度
    cmd.extend(["-w", str(PREVIEW_WIDTH), "-H", str(PREVIEW_HEIGHT)])
    cmd.extend(["-b", PREIVEW_BACKGROUND_COLOR])

    # 执行渲染命令
    try:
        print(cmd)
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"渲染错误: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def generate_preview_for_theme(theme_name, theme_files, output_dir):
    """为主题生成预览图像"""
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成流程图预览
    flowchart_file, config_file, css_file = create_temp_mermaid_file(
        FLOWCHART_EXAMPLE, theme_name, theme_files
    )
    flowchart_output = output_dir / "flowchart_preview.svg"
    render_mermaid(flowchart_file, str(flowchart_output), config_file, css_file)
    os.unlink(flowchart_file)

    # 生成序列图预览
    sequence_file, config_file, css_file = create_temp_mermaid_file(
        SEQUENCE_EXAMPLE, theme_name, theme_files
    )
    sequence_output = output_dir / "sequence_preview.svg"
    render_mermaid(sequence_file, str(sequence_output), config_file, css_file)
    os.unlink(sequence_file)

    # 生成类图预览
    class_file, config_file, css_file = create_temp_mermaid_file(
        CLASS_EXAMPLE, theme_name, theme_files
    )
    class_output = output_dir / "class_preview.svg"
    render_mermaid(class_file, str(class_output), config_file, css_file)
    os.unlink(class_file)

    # 生成组合预览图像（HTML文件）
    create_combined_preview(theme_name, output_dir)

    print(f"已完成 {theme_name} 主题的预览生成")

    return {
        "theme": theme_name,
        "flowchart": flowchart_output,
        "sequence": sequence_output,
        "class": class_output,
        "combined": output_dir / "preview.html",
    }


def create_combined_preview(theme_name, output_dir):
    """创建组合预览HTML文件"""
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{theme_name} - 主题预览</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }}
        .preview-container {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }}
        .preview-item {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h2 {{
            margin-top: 0;
            color: #444;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        .preview-image {{
            width: 100%;
            height: auto;
            border: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <h1>{theme_name} 主题预览</h1>
    
    <div class="preview-container">
        <div class="preview-item">
            <h2>流程图</h2>
            <img src="flowchart_preview.svg" alt="流程图预览" class="preview-image">
        </div>
        
        <div class="preview-item">
            <h2>序列图</h2>
            <img src="sequence_preview.svg" alt="序列图预览" class="preview-image">
        </div>
        
        <div class="preview-item">
            <h2>类图</h2>
            <img src="class_preview.svg" alt="类图预览" class="preview-image">
        </div>
    </div>
</body>
</html>
"""

    with open(output_dir / "preview.html", "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_all_previews(themes_dir, max_workers=None):
    """为所有主题并行生成预览图像"""
    theme_manager = get_theme_manager(themes_dir)
    themes = theme_manager.get_available_themes()

    if not themes:
        print(f"在 {themes_dir} 中未找到任何主题")
        return

    print(f"找到 {len(themes)} 个主题，开始并行生成预览...")

    # 使用线程池并行处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 创建任务列表
        future_to_theme = {
            executor.submit(
                generate_preview_for_theme,
                theme_name,
                theme_files,
                themes_dir / theme_name,
            ): theme_name
            for theme_name, theme_files in themes.items()
        }

        # 收集结果
        results = []
        for future in concurrent.futures.as_completed(future_to_theme):
            theme_name = future_to_theme[future]
            try:
                preview_files = future.result()
                results.append(preview_files)
                print(f"已成功生成 {theme_name} 的预览")
            except Exception as exc:
                print(f"{theme_name} 生成预览时出错: {exc}")

    print("所有预览生成完成！")
    return results


def main():
    parser = argparse.ArgumentParser(description="为Mermaid主题生成预览图像")
    parser.add_argument(
        "--themes-dir",
        type=Path,
        default=Path("themes"),
        help="主题目录的路径 (默认: ./themes)",
    )
    parser.add_argument(
        "--workers", type=int, default=None, help="并行工作的线程数 (默认: CPU核心数)"
    )

    args = parser.parse_args()

    if not args.themes_dir.exists():
        print(f"错误: 主题目录 {args.themes_dir} 不存在")
        return 1

    generate_all_previews(args.themes_dir, args.workers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
