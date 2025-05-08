import pytest
import os
from md_mermaid_static.models import CLIConfig, OutputFormat, Theme, LogLevel


def test_cli_config_with_default_max_workers():
    """Test that CLIConfig can be created with default max_workers"""
    config = CLIConfig(
        output_dir="output",
        output_format=OutputFormat.SVG,
        theme=Theme.DEFAULT,
        width=800,
        height=600,
        background_color="transparent",
        scale=1.0,
        concurrent=True,
        debug=False,
        log_level=LogLevel.INFO,
        use_command="auto",
    )
    assert config.max_workers == 4  # Default value


def test_cli_config_with_none_max_workers():
    """Test that CLIConfig can be created with None max_workers"""
    config = CLIConfig(
        output_dir="output",
        output_format=OutputFormat.SVG,
        theme=Theme.DEFAULT,
        width=800,
        height=600,
        background_color="transparent",
        scale=1.0,
        concurrent=True,
        max_workers=None,
        debug=False,
        log_level=LogLevel.INFO,
        use_command="auto",
    )
    assert config.max_workers is None


def test_cli_config_with_custom_max_workers():
    """Test that CLIConfig can be created with custom max_workers"""
    config = CLIConfig(
        output_dir="output",
        output_format=OutputFormat.SVG,
        theme=Theme.DEFAULT,
        width=800,
        height=600,
        background_color="transparent",
        scale=1.0,
        concurrent=True,
        max_workers=8,
        debug=False,
        log_level=LogLevel.INFO,
        use_command="auto",
    )
    assert config.max_workers == 8


def test_cli_config_with_none_theme():
    """Test that CLIConfig can be created with None theme"""
    config = CLIConfig(
        output_dir="output",
        output_format=OutputFormat.SVG,
        theme=None,
        width=800,
        height=600,
        background_color="transparent",
        scale=1.0,
        concurrent=True,
        max_workers=4,
        debug=False,
        log_level=LogLevel.INFO,
        use_command="auto",
    )
    assert config.theme is None
