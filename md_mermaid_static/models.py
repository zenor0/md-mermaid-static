from pydantic import BaseModel
from typing import Optional, Dict, Any

class MermaidConfig(BaseModel):
    """Mermaid 图表的配置模型"""
    caption: Optional[str] = None
    render_theme: Optional[str] = None
    
    class Config:
        extra = "allow"  # 允许额外的字段

class MermaidBlock(BaseModel):
    """表示一个 Mermaid 代码块"""
    content: str
    config: MermaidConfig
    line_start: int
    line_end: int
    
    def get_render_options(self) -> Dict[str, Any]:
        """获取渲染选项"""
        return {
            "theme": self.config.render_theme or "default",
            # 可以在这里添加更多渲染选项
        } 