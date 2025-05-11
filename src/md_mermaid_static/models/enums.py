"""
Enum definitions for md_mermaid_static.
"""

from enum import Enum


class OutputFormat(str, Enum):
    """Supported output formats"""

    SVG = "svg"
    PNG = "png"
    PDF = "pdf"
    ENHANCED_SVG = "enhanced-svg"


class Theme(str, Enum):
    """Mermaid supported themes"""

    DEFAULT = "default"
    FOREST = "forest"
    DARK = "dark"
    NEUTRAL = "neutral"


class LogLevel(str, Enum):
    """Log levels"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
