#!/usr/bin/env python3
"""
生成单个Mermaid主题预览图像的脚本

此脚本用于生成指定主题的单个类型(流程图、序列图或类图)的预览SVG。
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_mermaid_static.config.env import get_mermaid_cli_package

# 示例图表内容
CHART_EXAMPLES = {
    "flowchart": """
graph TD
    A[开始] --> B{是否继续?}
    B -->|是| C[处理]
    B -->|否| D[结束]
    C --> B
""",
    "sequence": """
sequenceDiagram
    participant 用户
    participant 系统
    用户->>系统: 请求数据
    系统-->>用户: 返回数据
    用户->>系统: 处理数据
    系统-->>用户: 确认处理完成
""",
    "class": """
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
}

# 预览图像的宽度和高度
PREVIEW_WIDTH = 800
PREVIEW_HEIGHT = 600
PREIVEW_BACKGROUND_COLOR = "transparent"


def create_temp_mermaid_file(content):
    """创建临时的Mermaid文件"""
    with tempfile.NamedTemporaryFile(
        suffix=".mmd", delete=False, mode="w", encoding="utf-8"
    ) as f:
        f.write(content)
        temp_file = f.name

    return temp_file


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
        print(f"执行命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"渲染错误: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def generate_single_preview(theme_dir, chart_type):
    """为主题生成指定类型的预览图像"""
    theme_dir = Path(theme_dir)
    theme_name = theme_dir.name
    
    # 检查主题文件是否存在
    config_file = theme_dir / "theme.json"
    css_file = theme_dir / "style.css"
    
    if not config_file.exists():
        print(f"错误: 未找到主题配置文件 {config_file}")
        return False
        
    if not css_file.exists():
        print(f"错误: 未找到主题样式文件 {css_file}")
        return False
    
    # 检查图表类型是否有效
    if chart_type not in CHART_EXAMPLES:
        print(f"错误: 无效的图表类型 {chart_type}，有效类型: {', '.join(CHART_EXAMPLES.keys())}")
        return False
    
    # 获取图表内容
    chart_content = CHART_EXAMPLES[chart_type]
    
    # 创建临时文件
    temp_file = create_temp_mermaid_file(chart_content)
    
    # 输出文件
    output_file = theme_dir / f"{chart_type}_preview.svg"
    
    # 渲染图表
    success = render_mermaid(temp_file, str(output_file), config_file, css_file)
    
    # 删除临时文件
    os.unlink(temp_file)
    
    if success:
        print(f"成功生成 {theme_name} 主题的 {chart_type} 预览")
        return True
    else:
        print(f"生成 {theme_name} 主题的 {chart_type} 预览失败")
        return False


def main():
    parser = argparse.ArgumentParser(description="为Mermaid主题生成单个预览图像")
    parser.add_argument(
        "--theme-dir",
        type=str,
        required=True,
        help="主题目录路径"
    )
    parser.add_argument(
        "--type",
        choices=["flowchart", "sequence", "class"],
        required=True,
        help="预览类型: flowchart, sequence, class"
    )

    args = parser.parse_args()
    
    if not Path(args.theme_dir).exists():
        print(f"错误: 主题目录 {args.theme_dir} 不存在")
        return 1

    if generate_single_preview(args.theme_dir, args.type):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main()) 