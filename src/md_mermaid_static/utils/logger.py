"""
Logging utilities for md_mermaid_static.
"""

from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
import logging
from rich.traceback import install as install_rich_traceback
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

# Import models (avoid circular import by using absolute path)
from md_mermaid_static.models import CLIConfig, MermaidBlock

# Install Rich's better exception handling
install_rich_traceback(show_locals=True)

# Configure console
console = Console()
error_console = Console(stderr=True)

# Log level mapping
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

# Create logger
logger = logging.getLogger("md-mermaid-static")
# Prevent logs from propagating to root logger
logger.propagate = False


def setup_logging(debug_mode: bool = False, log_file: Optional[str] = None):
    """
    Setup logging system

    Args:
        debug_mode: Enable debug mode
        log_file: Log file path
    """
    # Set log level
    log_level = logging.DEBUG if debug_mode else logging.INFO
    logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate output
    if logger.handlers:
        logger.handlers.clear()

    # Create Rich handler
    handler = RichHandler(
        rich_tracebacks=True,
        console=console,
        show_time=True,
        show_path=debug_mode,
        markup=True,
    )
    handler.setLevel(log_level)
    logger.addHandler(handler)

    # Add file handler if log file provided
    if log_file:
        log_path = Path(log_file)
        # Ensure log directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

    if debug_mode:
        logger.debug("Debug mode enabled")


def display_config(config: CLIConfig):
    """
    Display CLI configuration

    Args:
        config: CLI config object
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return

    table = Table(title="Runtime Config")
    table.add_column("Option", style="cyan")
    table.add_column("Value", style="green")

    for field_name, field_value in config.model_dump().items():
        table.add_row(field_name, str(field_value))

    console.print(
        Panel(table, title="[bold blue]Configuration[/bold blue]", border_style="blue")
    )


def display_mermaid_block(block: MermaidBlock, index: int):
    """
    Display Mermaid block info in debug mode

    Args:
        block: Mermaid code block
        index: Block index
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return

    try:
        # Get brief description
        brief_desc = block.get_brief()

        # Use string formatting directly
        console.print(
            f"[bold blue]Mermaid Block #{index + 1}[/bold blue] (lines {block.line_start}-{block.line_end})"
        )
        console.print(f"[cyan]Type: {brief_desc}[/cyan]")

        # Show code content
        console.print(
            Syntax(
                block.content,
                "mermaid",
                theme="monokai",
                line_numbers=True,
                start_line=block.line_start,
            )
        )

        # Show config info
        console.print("[bold cyan]Block Config[/bold cyan]")
        for k, v in block.config.model_dump().items():
            if v is not None:
                console.print(f"[yellow]{k}[/yellow]: [green]{v}[/green]")

        # Add separator
        console.print("─" * 50)
    except Exception as e:
        # Handle render errors safely
        logger.debug(f"Error displaying Mermaid block: {str(e)}")
        # Use simpler display
        console.print(
            f"[bold blue]Mermaid Block #{index + 1}[/bold blue] (lines {block.line_start}-{block.line_end})"
        )
        console.print(f"[cyan]Type: {block.get_brief()}[/cyan]")
        for k, v in block.config.model_dump().items():
            if v is not None:
                console.print(f"[yellow]{k}[/yellow]: [green]{v}[/green]")


def display_render_command(cmd: list, index: int):
    """
    Display render command

    Args:
        cmd: Render command list
        index: Block index
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return

    logger.debug(cmd)
    command_str = " ".join(cmd)
    console.print(
        Panel(
            Syntax(command_str, "bash", theme="monokai"),
            title=f"[bold blue]Render Command #{index + 1}[/bold blue]",
            border_style="blue",
        )
    )


def display_summary(
    total_blocks: int, success_count: int, failed_count: int, output_file: Path
):
    """
    Display processing summary

    Args:
        total_blocks: Total block count
        success_count: Successfully rendered count
        failed_count: Failed count
        output_file: Output file path
    """
    if not logger.isEnabledFor(logging.INFO):
        return

    console.print(
        Panel(
            f"""[bold]Processing Summary[/bold]
Total Mermaid blocks: {total_blocks}
Successfully rendered: {success_count}
Failed: {failed_count}
Output file: {output_file}""",
            title="[bold blue]Summary[/bold blue]",
            border_style="blue",
        )
    )
