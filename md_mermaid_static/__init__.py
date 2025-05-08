"""
md-mermaid-static - A CLI tool to convert Mermaid diagrams in Markdown to static images with enhanced logging
"""

__version__ = "0.2.0"

# Export core functionality
from .core import MarkdownParser, MermaidRenderer, MarkdownProcessor

# Export models
from .models import (
    MermaidBlock,
    MermaidConfig,
    MermaidRenderOptions,
    OutputFormat,
    Theme,
    CLIConfig,
)

# Export utils
from .utils import logger, setup_logging

__all__ = [
    "MarkdownParser",
    "MermaidRenderer",
    "MarkdownProcessor",
    "MermaidBlock",
    "MermaidConfig",
    "MermaidRenderOptions",
    "OutputFormat",
    "Theme",
    "CLIConfig",
    "logger",
    "setup_logging",
]
