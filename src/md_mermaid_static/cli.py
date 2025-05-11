import click
from pathlib import Path
import os
import traceback

from .core.processor import MarkdownProcessor
from .models import CLIConfig, OutputFormat, Theme, LogLevel
from .utils.logger import setup_logging, logger, display_config


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="output",
    help="Output directory path",
)
@click.option(
    "--output-format",
    "-e",
    type=click.Choice(["svg", "png", "pdf", "enhanced-svg"]),
    default="svg",
    help="Output image format (svg, png, pdf, enhanced-svg)",
)
@click.option(
    "--theme",
    "-t",
    type=str,
    default="default",
    help="Mermaid theme (built-in: default, forest, dark, neutral, or custom theme name)",
)
@click.option("--width", "-w", type=int, default=None, help="Chart width (pixels)")
@click.option("--height", "-H", type=int, default=None, help="Chart height (pixels)")
@click.option(
    "--background-color",
    "-b",
    type=str,
    default=None,
    help="Background color (e.g., transparent, white, black, red, #F0F0F0)",
)
@click.option("--scale", "-s", type=float, default=None, help="Scale factor")
@click.option(
    "--config-file",
    "-c",
    type=click.Path(exists=True),
    help="Mermaid JSON config file path",
)
@click.option(
    "--css-file", "-C", type=click.Path(exists=True), help="Custom CSS file path"
)
@click.option("--pdf-fit", "-f", is_flag=True, help="Scale PDF to fit chart size")
@click.option(
    "--concurrent",
    "-p",
    is_flag=True,
    help="Enable concurrent rendering to speed up processing",
)
@click.option(
    "--max-workers",
    "-j",
    type=int,
    default=0,
    help="Maximum number of worker processes for concurrent rendering (default is CPU core count)",
)
@click.option(
    "--debug", "-d", is_flag=True, help="Enable debug mode with detailed logs"
)
@click.option(
    "--log-level",
    "-L",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical"], case_sensitive=False
    ),
    default="info",
    help="Log level",
)
@click.option("--log-file", "-l", type=click.Path(), help="Log file path")
@click.option(
    "--use-command",
    type=click.Choice(["auto", "npx", "pnpx"]),
    default="auto",
    help="Specify whether to use npx or pnpx command (default is auto-detect)",
)
@click.option(
    "--themes-dir",
    type=click.Path(exists=True),
    help="Directory containing theme folders",
)
@click.version_option()
def main(
    input_file: str,
    output_dir: str,
    output_format: str,
    theme: str,
    width: int,
    height: int,
    background_color: str,
    scale: float,
    config_file: str,
    css_file: str,
    pdf_fit: bool,
    concurrent: bool,
    max_workers: int,
    debug: bool,
    log_level: str,
    log_file: str,
    use_command: str,
    themes_dir: str,
):
    """Convert Mermaid code blocks in Markdown to static images."""
    try:
        # Setup logging
        setup_logging(debug_mode=debug, log_file=log_file)

        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Handle max_workers - ensure it's always an integer
        if max_workers <= 0:
            max_workers = os.cpu_count() or 4

        # If output format is enhanced-svg, set pdf_fit to True by default
        if output_format == "enhanced-svg":
            pdf_fit = True

        # Handle theme validation and custom themes
        theme_obj = None
        try:
            # Try as built-in theme first
            theme_obj = Theme(theme)
        except ValueError:
            # Not a built-in theme, check if it's a custom theme
            from .utils.theme_manager import get_theme_manager

            theme_manager = get_theme_manager(Path(themes_dir) if themes_dir else None)
            if theme_manager.theme_exists(theme):
                # Custom theme exists, will be handled by get_render_options
                logger.info(f"Using custom theme: {theme}")
                # theme_obj stays None, will be handled as custom_theme
            else:
                # Theme doesn't exist, fall back to default
                logger.warning(
                    f"Theme '{theme}' not found. Falling back to default theme. "
                    f"Available built-in themes: {', '.join([t.value for t in Theme])}"
                )
                if theme_manager.themes_cache:
                    logger.warning(
                        f"Available custom themes: {', '.join(theme_manager.themes_cache.keys())}"
                    )
                theme = "default"
                theme_obj = Theme.DEFAULT

        # Create CLI config
        cli_config = CLIConfig(
            output_dir=output_dir,
            output_format=OutputFormat(output_format),
            theme=theme_obj,
            custom_theme=None
            if theme_obj
            else theme,  # Set custom_theme if not a built-in theme
            width=width,
            height=height,
            background_color=background_color,
            scale=scale,
            config_file=config_file,
            css_file=css_file,
            pdf_fit=pdf_fit,
            concurrent=concurrent,
            max_workers=max_workers,
            debug=debug,
            log_file=log_file,
            log_level=LogLevel(log_level),
            use_command=use_command,
            themes_dir=themes_dir,
        )

        # Set the global singleton instance
        CLIConfig.set_instance(cli_config)

        # Display config in debug mode
        display_config(cli_config)

        # Process file
        processor = MarkdownProcessor(input_file, cli_config)
        output_file = processor.process()

        logger.info(f"Processing complete! Output file: {output_file}")

    except Exception as e:
        if "logger" in locals():
            logger.error(f"Error: {str(e)}", exc_info=debug)
            if debug:
                # Add full traceback for debugging
                tb = traceback.format_exc()
                logger.error(f"Traceback:\n{tb}")
        else:
            print(f"Error: {str(e)}")
            if debug:
                tb = traceback.format_exc()
                print(f"Traceback:\n{tb}")
        raise click.Abort()


if __name__ == "__main__":
    main()
