"""
Mermaid configuration models.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict

from .enums import Theme, OutputFormat


class MermaidConfig(BaseModel):
    """Configuration model for Mermaid diagrams"""
    
    model_config = ConfigDict(extra="allow")

    caption: Optional[str] = None
    render_theme: Optional[Theme] = None
    background_color: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    scale: Optional[float] = None
    css_file: Optional[str] = None


class MermaidRenderOptions(BaseModel):
    """Mermaid rendering options"""

    theme: Theme = Theme.DEFAULT
    width: Optional[int] = None
    height: Optional[int] = None
    background_color: Optional[str] = None
    output_format: OutputFormat = OutputFormat.SVG
    scale: Optional[float] = None
    css_file: Optional[str] = None
    config_file: Optional[str] = None
    pdf_fit: bool = False
    svg_id: Optional[str] = None
