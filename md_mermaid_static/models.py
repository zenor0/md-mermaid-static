from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from enum import Enum

class OutputFormat(str, Enum):
    """支持的输出格式"""
    SVG = "svg"
    PNG = "png"
    PDF = "pdf"

class Theme(str, Enum):
    """Mermaid 支持的主题"""
    DEFAULT = "default"
    FOREST = "forest"
    DARK = "dark"
    NEUTRAL = "neutral"

class MermaidConfig(BaseModel):
    """Mermaid 图表的配置模型"""
    caption: Optional[str] = None
    render_theme: Optional[Theme] = None
    background_color: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    scale: Optional[float] = None
    css_file: Optional[str] = None
    
    class Config:
        extra = "allow"  # 允许额外的字段

class MermaidRenderOptions(BaseModel):
    """Mermaid 渲染选项"""
    theme: Theme = Theme.DEFAULT
    width: int = 800
    height: int = 600
    background_color: str = "white"
    output_format: OutputFormat = OutputFormat.SVG
    scale: float = 1.0
    css_file: Optional[str] = None
    config_file: Optional[str] = None
    pdf_fit: bool = False
    svg_id: Optional[str] = None

class MermaidBlock(BaseModel):
    """表示一个 Mermaid 代码块"""
    content: str
    config: MermaidConfig
    line_start: int
    line_end: int
    
    def get_render_options(self) -> MermaidRenderOptions:
        """获取渲染选项"""
        return MermaidRenderOptions(
            theme=self.config.render_theme or Theme.DEFAULT,
            background_color=self.config.background_color or "white",
            width=self.config.width or 800,
            height=self.config.height or 600,
            scale=self.config.scale or 1.0,
            css_file=self.config.css_file,
        )

class CLIConfig(BaseModel):
    """CLI 全局配置"""
    output_dir: str
    output_format: OutputFormat = OutputFormat.SVG
    concurrent: bool = False
    max_workers: int = 4
    theme: Theme = Theme.DEFAULT
    width: int = 800
    height: int = 600
    background_color: str = "transparent"
    scale: float = 1.0
    config_file: Optional[str] = None
    css_file: Optional[str] = None
    pdf_fit: bool = False 