"""
Utility functions and helpers.
"""

from .logger import (
    logger,
    setup_logging,
    LOG_LEVELS,
    display_config,
    display_mermaid_block,
    display_render_command,
    display_summary,
)

from .theme_manager import (
    ThemeManager,
    get_theme_manager,
)

__all__ = [
    "logger",
    "setup_logging",
    "LOG_LEVELS",
    "display_config",
    "display_mermaid_block",
    "display_render_command",
    "display_render_result",
    "display_summary",
    "ThemeManager",
    "get_theme_manager",
]
