"""
Mermaid code block model.
"""

from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Tuple

from .mermaid_config import MermaidConfig, MermaidRenderOptions
from .enums import Theme
from .cli_config import CLIConfig


class MermaidBlock(BaseModel):
    """Represents a Mermaid code block"""

    content: str
    config: MermaidConfig
    line_start: int
    line_end: int

    def get_render_options(self) -> MermaidRenderOptions:
        """Get rendering options"""
        # Get global CLI config if available
        cli_config = CLIConfig.get_instance()

        # Use CLI config for defaults when available
        default_theme = Theme.DEFAULT
        default_bg = None
        default_width = None
        default_height = None
        default_scale = None
        default_css = None
        default_config_file = None
        default_pdf_fit = False

        # Override defaults with CLI config if available
        if cli_config:
            default_theme = cli_config.theme or default_theme
            default_bg = cli_config.background_color or default_bg
            default_width = cli_config.width or default_width
            default_height = cli_config.height or default_height
            default_scale = cli_config.scale or default_scale
            default_css = cli_config.css_file or default_css
            default_config_file = cli_config.config_file or default_config_file
            default_pdf_fit = cli_config.pdf_fit or default_pdf_fit

        # Check for custom theme
        custom_theme = self.config.custom_theme
        config_file, css_file = None, None

        # If custom theme is specified, try to load theme files
        if custom_theme:
            # Import here to avoid circular imports
            from md_mermaid_static.utils.theme_manager import get_theme_manager

            # Get theme manager and theme files
            if cli_config and cli_config.themes_dir:
                theme_manager = get_theme_manager(Path(cli_config.themes_dir))
            else:
                theme_manager = get_theme_manager()

            config_file, css_file = theme_manager.get_theme_files(custom_theme)

            # If theme files are found, they override the defaults
            if config_file:
                default_config_file = str(config_file)
            if css_file:
                default_css = str(css_file)

        # Block config overrides CLI config when specified
        return MermaidRenderOptions(
            theme=self.config.render_theme or default_theme,
            background_color=self.config.background_color or default_bg,
            width=self.config.width or default_width,
            height=self.config.height or default_height,
            scale=self.config.scale or default_scale,
            css_file=self.config.css_file or default_css,
            config_file=default_config_file,
            pdf_fit=default_pdf_fit,
            custom_theme=custom_theme,
        )

    def get_brief(self) -> str:
        """Get a brief description of the code block"""
        lines = self.content.split("\n")
        # Use first line as brief description
        first_line = lines[0] if lines else ""
        # Clean common chart type markers
        brief = (
            first_line.lstrip("graph ")
            .lstrip("sequenceDiagram")
            .lstrip("classDiagram")
            .strip()
        )

        # Truncate if too long
        if len(brief) > 50:
            brief = brief[:47] + "..."

        # Use chart type if no valid brief
        if not brief:
            if "graph" in first_line:
                return "Flow Chart"
            elif "sequenceDiagram" in first_line:
                return "Sequence Diagram"
            elif "classDiagram" in first_line:
                return "Class Diagram"
            elif "gantt" in first_line:
                return "Gantt Chart"
            elif "pie" in first_line:
                return "Pie Chart"
            else:
                return "Mermaid Diagram"

        return brief
