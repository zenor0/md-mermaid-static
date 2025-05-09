"""
CLI Configuration model.
"""

from typing import Optional, ClassVar
from pydantic import BaseModel

from .enums import OutputFormat, Theme, LogLevel


class CLIConfig(BaseModel):
    """CLI global configuration"""
    
    # Singleton instance
    _instance: ClassVar[Optional["CLIConfig"]] = None

    output_dir: str = "output"
    output_format: OutputFormat = OutputFormat.SVG
    concurrent: bool = False
    max_workers: Optional[int] = 4
    theme: Optional[Theme] = Theme.DEFAULT
    width: Optional[int] = None
    height: Optional[int] = None
    background_color: Optional[str] = None
    scale: Optional[float] = None
    config_file: Optional[str] = None
    css_file: Optional[str] = None
    pdf_fit: bool = False  # Whether to fit chart to PDF page
    debug: bool = False  # Debug mode
    log_file: Optional[str] = None  # Log file path
    log_level: LogLevel = LogLevel.INFO  # Log level
    use_command: str = "auto"  # Which command to use for mermaid-cli: auto, npx, pnpx
    themes_dir: Optional[str] = None  # Directory containing theme folders
    
    @classmethod
    def set_instance(cls, instance: "CLIConfig") -> None:
        """Set global CLI config instance"""
        cls._instance = instance
    
    @classmethod
    def get_instance(cls) -> Optional["CLIConfig"]:
        """Get global CLI config instance"""
        return cls._instance
