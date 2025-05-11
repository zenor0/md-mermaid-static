"""
配置文件，确保测试可以找到src目录中的包
"""
import sys
import os
from pathlib import Path

# 将src目录添加到Python路径中
project_root = Path(__file__).parent.parent.absolute()
src_dir = os.path.join(project_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir) 