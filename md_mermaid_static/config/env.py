"""
环境变量配置模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv(Path(__file__).parents[2] / ".env")

# Mermaid CLI版本
MERMAID_CLI_VERSION = os.getenv("MERMAID_CLI_VERSION", "11.4.2")

# 获取完整的CLI命令
def get_mermaid_cli_package():
    """获取带版本号的mermaid-cli包名"""
    return f"@mermaid-js/mermaid-cli@{MERMAID_CLI_VERSION}"