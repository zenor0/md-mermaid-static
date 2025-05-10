#!/usr/bin/env python3
"""
生成单个Mermaid主题HTML预览的脚本

此脚本用于为单个主题生成HTML预览，展示该主题的所有SVG预览图像。
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_html_preview(theme_dir):
    """为主题生成HTML预览"""
    theme_dir = Path(theme_dir)
    theme_name = theme_dir.name

    # 检查SVG预览是否存在
    flowchart_preview = theme_dir / "flowchart_preview.svg"
    sequence_preview = theme_dir / "sequence_preview.svg"
    class_preview = theme_dir / "class_preview.svg"

    missing_files = []
    if not flowchart_preview.exists():
        missing_files.append("flowchart_preview.svg")
    if not sequence_preview.exists():
        missing_files.append("sequence_preview.svg")
    if not class_preview.exists():
        missing_files.append("class_preview.svg")

    if missing_files:
        print(f"错误: 主题 {theme_name} 缺少以下预览文件: {', '.join(missing_files)}")
        print("请先运行generate_single_preview.py生成所有必要的预览文件")
        return False

    # 创建HTML内容
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

    # 写入HTML文件
    html_file = theme_dir / "preview.html"
    try:
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"成功为 {theme_name} 主题生成HTML预览: {html_file}")
        return True
    except IOError as e:
        print(f"写入HTML文件时出错: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="为Mermaid主题生成HTML预览")
    parser.add_argument("--theme-dir", type=str, required=True, help="主题目录路径")

    args = parser.parse_args()

    theme_dir = Path(args.theme_dir)
    if not theme_dir.exists():
        print(f"错误: 主题目录 {theme_dir} 不存在")
        return 1

    if generate_html_preview(theme_dir):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
