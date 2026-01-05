"""
Slide Schema Definitions - 接口契约
"""

from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class SlideType(str, Enum):
    """幻灯片类型枚举"""
    TITLE = "title"
    CONTENT = "content"
    SECTION = "section"
    TWO_COLUMN = "two_column"
    COMPARISON = "comparison"
    CLOSING = "closing"


class ThemeColor(str, Enum):
    """主题配色枚举"""
    CORPORATE_BLUE = "corporate_blue"
    MODERN_GREEN = "modern_green"
    ELEGANT_PURPLE = "elegant_purple"
    WARM_ORANGE = "warm_orange"
    TECH_DARK = "tech_dark"


class ContentPriority(str, Enum):
    """内容优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class BulletPointSchema(BaseModel):
    """单个Bullet Point的Schema"""
    text: str = Field(..., min_length=1, max_length=500)
    level: int = Field(default=0, ge=0, le=2)
    priority: ContentPriority = Field(default=ContentPriority.NORMAL)
    
    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()


class TableSchema(BaseModel):
    """表格Schema"""
    headers: List[str]
    rows: List[List[str]]
    caption: Optional[str] = None


class CodeBlockSchema(BaseModel):
    """代码块Schema"""
    code: str
    language: str = "python"
    show_line_numbers: bool = False


class SlideContentSchema(BaseModel):
    """单页幻灯片内容Schema"""
    slide_type: SlideType
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    body_points: List[BulletPointSchema] = Field(default_factory=list)
    speaker_notes: Optional[str] = Field(default=None, max_length=2000)
    table: Optional[TableSchema] = None
    code_block: Optional[CodeBlockSchema] = None
    left_column: Optional[List[BulletPointSchema]] = None
    right_column: Optional[List[BulletPointSchema]] = None
    
    @field_validator('body_points')
    @classmethod
    def limit_body_points(cls, v):
        if len(v) > 10:
            raise ValueError('Too many body points (max 10)')
        return v


class PresentationMetadataSchema(BaseModel):
    """演示文稿元数据Schema"""
    title: str
    author: Optional[str] = None
    created_date: Optional[str] = None
    theme: ThemeColor = ThemeColor.CORPORATE_BLUE
    language: str = "en"
    aspect_ratio: Literal["16:9", "4:3"] = "16:9"


class SlidedeckSchema(BaseModel):
    """完整演示文稿Schema"""
    metadata: PresentationMetadataSchema
    slides: List[SlideContentSchema] = Field(..., min_length=1, max_length=50)
    
    @field_validator('slides')
    @classmethod
    def validate_slides(cls, v):
        has_title = any(s.slide_type == SlideType.TITLE for s in v)
        if not has_title:
            raise ValueError('Must have at least one title slide')
        return v


class GenerationResultSchema(BaseModel):
    """PPTX生成结果Schema"""
    success: bool
    output_path: Optional[str] = None
    num_slides: int = 0
    elapsed_time: Optional[float] = None
    metrics: Optional[Dict[str, float]] = None
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


def validate_slide_json(json_data: Dict[str, Any]) -> SlidedeckSchema:
    """验证JSON是否符合Schema"""
    return SlidedeckSchema(**json_data)


def create_example_slidedeck() -> Dict[str, Any]:
    """创建示例Slidedeck JSON"""
    return {
        "metadata": {
            "title": "Example Presentation",
            "author": "Team",
            "theme": "corporate_blue",
            "language": "en",
            "aspect_ratio": "16:9"
        },
        "slides": [
            {
                "slide_type": "title",
                "title": "Welcome to Our Presentation",
                "subtitle": "A Comprehensive Overview"
            },
            {
                "slide_type": "content",
                "title": "Key Points",
                "body_points": [
                    {"text": "First important point", "level": 0, "priority": "high"},
                    {"text": "Supporting detail", "level": 1},
                    {"text": "Second important point", "level": 0}
                ],
                "speaker_notes": "Remember to elaborate on each point."
            },
            {
                "slide_type": "closing",
                "title": "Thank You",
                "subtitle": "Questions & Discussion"
            }
        ]
    }


__all__ = [
    'SlideType', 'ThemeColor', 'ContentPriority',
    'BulletPointSchema', 'TableSchema', 'CodeBlockSchema',
    'SlideContentSchema', 'PresentationMetadataSchema',
    'SlidedeckSchema', 'GenerationResultSchema',
    'validate_slide_json', 'create_example_slidedeck',
]