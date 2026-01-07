"""Services Package - Core PPT Generation Services"""

from .engine import PPTXEngine, generate_pptx
from .overflow import TextOverflowEngine, BoundingBox, FontMetrics, TextHeightEstimator
from .renderer_pro import SlideRendererPro
from .metrics import LayoutQualityEvaluator, MetricsResult
from .themes import COLOR_SCHEMES, ThemeColorScheme, get_theme, list_themes

__version__ = "1.0.0"

__all__ = [
    'PPTXEngine', 'generate_pptx',
    'TextOverflowEngine', 'BoundingBox', 'FontMetrics', 'TextHeightEstimator',
    'SlideRendererPro',
    'LayoutQualityEvaluator', 'MetricsResult',
    'COLOR_SCHEMES', 'ThemeColorScheme', 'get_theme', 'list_themes',
]