#!/usr/bin/env python3
"""
生成主题预览图库的脚本。

此脚本会生成一个HTML页面，展示所有主题的预览图像。
假设所有主题的预览SVG和HTML已经由Makefile生成。
"""

import os
import sys
import argparse
from pathlib import Path
import json

# 添加项目根目录到路径，以便导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from md_mermaid_static.utils.theme_manager import get_theme_manager


def generate_theme_gallery(themes_dir: Path, output_file: Path):
    """生成主题预览图库"""
    theme_manager = get_theme_manager(themes_dir)
    themes = theme_manager.get_available_themes()

    if not themes:
        print(f"在 {themes_dir} 中未找到任何主题")
        return False

    print(f"找到 {len(themes)} 个主题，开始生成图库...")

    # 预览文件检查标志
    all_previews_exist = True
    
    # 检查所有主题的预览文件是否存在
    for theme_name, theme_files in themes.items():
        theme_dir = themes_dir / theme_name
        flowchart_preview = theme_dir / "flowchart_preview.svg"
        preview_html = theme_dir / "preview.html"
        
        # 如果任何一个预览文件不存在，设置标志为False
        if not flowchart_preview.exists() or not preview_html.exists():
            print(f"警告: {theme_name} 主题没有所有必要的预览文件")
            print(f"  - 流程图预览: {'存在' if flowchart_preview.exists() else '缺失'}")
            print(f"  - HTML预览: {'存在' if preview_html.exists() else '缺失'}")
            all_previews_exist = False

    if not all_previews_exist:
        print("有主题缺少预览文件，请先运行 make previews 生成所有预览")
        return False

    # 创建HTML内容
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid 主题图库</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .theme-card {
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .theme-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .theme-header {
            padding: 15px;
            background-color: #f0f0f0;
            border-bottom: 1px solid #ddd;
        }
        .theme-header h2 {
            margin: 0;
            font-size: 1.2em;
            color: #444;
        }
        .theme-preview {
            padding: 15px;
        }
        .theme-preview img {
            width: 100%;
            height: auto;
            border: 1px solid #eee;
        }
        .theme-footer {
            padding: 10px 15px;
            background-color: #f9f9f9;
            border-top: 1px solid #eee;
            text-align: center;
        }
        .theme-footer a {
            color: #0066cc;
            text-decoration: none;
            font-size: 0.9em;
        }
        .theme-footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Mermaid 主题图库</h1>
    
    <div class="gallery">
"""

    # 添加每个主题的卡片
    for theme_name, theme_files in sorted(themes.items()):
        theme_dir = themes_dir / theme_name
        flowchart_preview = theme_dir / "flowchart_preview.svg"
        preview_html = theme_dir / "preview.html"

        # 获取主题配置信息
        theme_info = "自定义主题"
        if "config" in theme_files:
            try:
                with open(theme_files["config"], "r", encoding="utf-8") as f:
                    config = json.load(f)
                    base_theme = config.get("theme", "base")
                    dark_mode = config.get("themeVariables", {}).get("darkMode", False)
                    theme_info = (
                        f"基于 {base_theme} 主题{'，深色模式' if dark_mode else ''}"
                    )
            except (json.JSONDecodeError, IOError) as e:
                print(f"警告: 无法读取 {theme_name} 的配置: {e}")

        # 添加主题卡片
        html_content += f"""
        <div class="theme-card">
            <div class="theme-header">
                <h2>{theme_name}</h2>
                <small>{theme_info}</small>
            </div>
            <div class="theme-preview">
                <img src="{flowchart_preview.relative_to(output_file.parent)}" alt="{theme_name} 预览">
            </div>
            <div class="theme-footer">
                <a href="{preview_html.relative_to(output_file.parent)}" target="_blank">查看完整预览</a>
            </div>
        </div>
"""

    # 完成HTML内容
    html_content += """
    </div>
</body>
</html>
"""

    # 写入输出文件
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"主题图库已生成: {output_file}")
    return True


def main():
    parser = argparse.ArgumentParser(description="生成Mermaid主题预览图库")
    parser.add_argument(
        "--themes-dir",
        type=Path,
        default=Path("themes"),
        help="主题目录的路径 (默认: ./themes)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("themes/gallery.html"),
        help="输出HTML文件的路径 (默认: ./themes/gallery.html)",
    )

    args = parser.parse_args()

    if not args.themes_dir.exists():
        print(f"错误: 主题目录 {args.themes_dir} 不存在")
        return 1

    if not generate_theme_gallery(args.themes_dir, args.output):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
