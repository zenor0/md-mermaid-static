"""
Theme management utilities for md-mermaid-static.
"""

from pathlib import Path
from typing import Optional, Dict, Tuple, List
import os
import importlib.resources
import sys
import importlib

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
            themes_dir: Path to the themes directory. If None, uses the default locations.
        """
        self.themes_dirs: List[Path] = []
        
        # If themes_dir is explicitly provided, use it as first priority
        if themes_dir:
            self.themes_dirs.append(themes_dir)
        
        # Always try to find the package-installed themes
        try:
            # For Python 3.9+
            if sys.version_info >= (3, 9):
                # Try to find the themes directory in the package itself
                logger.debug("Trying to find package themes directory")
                logger.debug(importlib.resources.files("md_mermaid_static"))
                with importlib.resources.files("md_mermaid_static").joinpath(
                    "../../themes"
                ) as pkg_themes_path:
                    if pkg_themes_path.exists():
                        self.themes_dirs.append(pkg_themes_path)
                        logger.debug(f"Found package themes directory: {pkg_themes_path}")
            else:
                # For Python 3.8 compatibility
                import importlib_resources
                
                package_root = str(
                    importlib_resources.files("md_mermaid_static")
                ).rsplit("md_mermaid_static", 1)[0]
                pkg_themes_path = Path(package_root) / "themes"
                if pkg_themes_path.exists():
                    self.themes_dirs.append(pkg_themes_path)
                    logger.debug(f"Found package themes directory: {pkg_themes_path}")
        except (ImportError, ModuleNotFoundError) as e:
            logger.debug(f"Error finding package themes: {e}")
        
        # If no themes directory was found, fall back to current directory
        if not self.themes_dirs:
            local_themes = Path("themes")
            if local_themes.exists():
                self.themes_dirs.append(local_themes)
                logger.debug(f"Using local themes directory: {local_themes}")
        
        # Cache theme information
        self.themes_cache: Dict[str, Dict[str, Path]] = {}
        self._load_themes()

    def _load_themes(self) -> None:
        """Load available themes from all theme directories."""
        self.themes_cache.clear()
        
        for themes_dir in self.themes_dirs:
            if not themes_dir.exists():
                logger.debug(f"Themes directory not found: {themes_dir}")
                continue

            logger.debug(f"Loading themes from {themes_dir}")

            # Scan for theme directories
            for theme_dir in themes_dir.iterdir():
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
                    # Only add if not already in cache (prioritize earlier directories)
                    if theme_name not in self.themes_cache:
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

    def add_themes_dir(self, themes_dir: Path) -> None:
        """
        Add a themes directory and reload themes.

        Args:
            themes_dir: New themes directory path
        """
        if themes_dir not in self.themes_dirs:
            # Insert at the beginning for highest priority
            self.themes_dirs.insert(0, themes_dir)
            self._load_themes()

    @property
    def themes_dir(self) -> Path:
        """
        Get the primary themes directory (for backwards compatibility).

        Returns:
            The first themes directory in the list
        """
        return self.themes_dirs[0] if self.themes_dirs else Path("themes")
    
    @themes_dir.setter
    def themes_dir(self, value: Path) -> None:
        """
        Set the primary themes directory (for backwards compatibility).
        
        Args:
            value: The new themes directory path
        """
        if self.themes_dirs:
            self.themes_dirs[0] = value
        else:
            self.themes_dirs.append(value)
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
    elif themes_dir is not None:
        # Add the directory with highest priority
        _instance.add_themes_dir(themes_dir)
    return _instance
