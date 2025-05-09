"""
Theme management utilities for md-mermaid-static.
"""

from pathlib import Path
from typing import Optional, Dict, Tuple
import os

from md_mermaid_static.utils.logger import logger


class ThemeManager:
    """
    Manages themes for Mermaid rendering.

    Themes are stored in a directory structure where each theme has its own folder
    containing config files and CSS files.
    """

    def __init__(self, themes_dir: Optional[Path] = None):
        """
        Initialize the theme manager.

        Args:
            themes_dir: Path to the themes directory. If None, uses the default location.
        """
        # Default themes directory is "themes" in the current working directory
        self.themes_dir = themes_dir or Path("themes")
        self.themes_cache: Dict[str, Dict[str, Path]] = {}
        self._load_themes()

    def _load_themes(self) -> None:
        """Load available themes from the themes directory."""
        if not self.themes_dir.exists():
            logger.debug(f"Themes directory not found: {self.themes_dir}")
            return

        logger.debug(f"Loading themes from {self.themes_dir}")

        # Scan for theme directories
        for theme_dir in self.themes_dir.iterdir():
            if not theme_dir.is_dir():
                continue

            theme_name = theme_dir.name
            theme_files = {}

            # Look for config and CSS files
            for file in theme_dir.iterdir():
                if file.is_file():
                    if file.suffix == ".json":
                        theme_files["config"] = file
                    elif file.suffix == ".css":
                        theme_files["css"] = file

            if theme_files:
                self.themes_cache[theme_name] = theme_files
                logger.debug(f"Found theme: {theme_name} with files: {theme_files}")

    def get_theme_files(self, theme_name: str) -> Tuple[Optional[Path], Optional[Path]]:
        """
        Get the config and CSS files for a theme.

        Args:
            theme_name: Name of the theme to get files for

        Returns:
            Tuple of (config_file, css_file) paths. Either may be None if not found.
        """
        if not theme_name or theme_name not in self.themes_cache:
            return None, None

        theme_files = self.themes_cache.get(theme_name, {})
        return theme_files.get("config"), theme_files.get("css")

    def theme_exists(self, theme_name: str) -> bool:
        """
        Check if a theme exists.

        Args:
            theme_name: Name of the theme to check

        Returns:
            True if the theme exists, False otherwise
        """
        return theme_name in self.themes_cache

    def get_available_themes(self) -> Dict[str, Dict[str, Path]]:
        """
        Get all available themes.

        Returns:
            Dictionary of theme names to their files
        """
        return self.themes_cache

    def set_themes_dir(self, themes_dir: Path) -> None:
        """
        Set the themes directory and reload themes.

        Args:
            themes_dir: New themes directory path
        """
        self.themes_dir = themes_dir
        self.themes_cache.clear()
        self._load_themes()


# Create a singleton instance
_instance: Optional[ThemeManager] = None


def get_theme_manager(themes_dir: Optional[Path] = None) -> ThemeManager:
    """
    Get the singleton theme manager instance.

    Args:
        themes_dir: Optional themes directory to use

    Returns:
        ThemeManager instance
    """
    global _instance
    if _instance is None:
        _instance = ThemeManager(themes_dir)
    elif themes_dir is not None and themes_dir != _instance.themes_dir:
        _instance.set_themes_dir(themes_dir)
    return _instance
