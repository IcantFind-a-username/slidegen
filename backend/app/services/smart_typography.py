"""
Smart Typography Engine - 智能排版引擎

Features:
1. Width AND height overflow detection
2. Smart font size adjustment based on content density
3. Automatic line breaking
4. Content-aware sizing

Author: SlideGen Team
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from .overflow import BoundingBox, FontMetrics, TextHeightEstimator


@dataclass
class TypographyConfig:
    """Typography configuration for different contexts."""
    min_font_size: float = 14.0
    max_font_size: float = 48.0
    preferred_font_size: float = 24.0
    line_spacing: float = 1.2
    min_chars_per_line: int = 20
    max_chars_per_line: int = 60


# Presets for different slide elements
TYPOGRAPHY_PRESETS = {
    'hero_title': TypographyConfig(
        min_font_size=32, max_font_size=56, preferred_font_size=48,
        line_spacing=1.1, min_chars_per_line=15, max_chars_per_line=40
    ),
    'slide_title': TypographyConfig(
        min_font_size=22, max_font_size=36, preferred_font_size=28,
        line_spacing=1.15, min_chars_per_line=20, max_chars_per_line=50
    ),
    'subtitle': TypographyConfig(
        min_font_size=16, max_font_size=26, preferred_font_size=20,
        line_spacing=1.2, min_chars_per_line=25, max_chars_per_line=70
    ),
    'body': TypographyConfig(
        min_font_size=14, max_font_size=22, preferred_font_size=18,
        line_spacing=1.4, min_chars_per_line=30, max_chars_per_line=80
    ),
    'caption': TypographyConfig(
        min_font_size=10, max_font_size=14, preferred_font_size=12,
        line_spacing=1.3, min_chars_per_line=40, max_chars_per_line=100
    ),
}


class SmartTypographyEngine:
    """
    Intelligent typography engine that adjusts font size based on:
    - Available space (width and height)
    - Content length
    - Content type (title, body, etc.)
    - Readability requirements
    """
    
    def __init__(self):
        self.height_estimator = TextHeightEstimator()
    
    def calculate_optimal_font_size(
        self,
        text: str,
        box: BoundingBox,
        config: TypographyConfig = None,
        preset: str = 'body'
    ) -> Dict[str, Any]:
        """
        Calculate the optimal font size for text to fit in a box.
        
        Returns:
            {
                'font_size': float,
                'text': str,
                'lines': int,
                'strategy': str
            }
        """
        if not text:
            return {
                'font_size': config.preferred_font_size if config else 18,
                'text': '',
                'lines': 0,
                'strategy': 'empty'
            }
        
        # Get config
        if config is None:
            config = TYPOGRAPHY_PRESETS.get(preset, TYPOGRAPHY_PRESETS['body'])
        
        # Try preferred size first
        font_size = config.preferred_font_size
        
        # Check if text fits at preferred size
        if self._text_fits(text, box, font_size, config.line_spacing):
            return {
                'font_size': font_size,
                'text': text,
                'lines': self._count_lines(text, box.width, font_size),
                'strategy': 'preferred_fit'
            }
        
        # Binary search for optimal font size
        font_size = self._find_optimal_size(text, box, config)
        
        if font_size >= config.min_font_size:
            return {
                'font_size': font_size,
                'text': text,
                'lines': self._count_lines(text, box.width, font_size),
                'strategy': 'size_adjusted'
            }
        
        # Text still doesn't fit, need to truncate
        truncated = self._smart_truncate(text, box, config.min_font_size, config.line_spacing)
        return {
            'font_size': config.min_font_size,
            'text': truncated,
            'lines': self._count_lines(truncated, box.width, config.min_font_size),
            'strategy': 'truncated'
        }
    
    def fit_text_smart(
        self,
        text: str,
        box: BoundingBox,
        base_font_size: float = 24.0,
        min_font_size: float = 14.0,
        max_font_size: float = 48.0
    ) -> Dict[str, Any]:
        """
        Fit text to box with smart font size adjustment.
        Simpler interface for common use cases.
        """
        config = TypographyConfig(
            min_font_size=min_font_size,
            max_font_size=max_font_size,
            preferred_font_size=base_font_size
        )
        return self.calculate_optimal_font_size(text, box, config)
    
    def _text_fits(self, text: str, box: BoundingBox, font_size: float, 
                   line_spacing: float) -> bool:
        """Check if text fits in box at given font size."""
        # Check width (single line fit)
        text_width = FontMetrics.calculate_text_width(text, font_size)
        
        # If single line fits width, check height
        if text_width <= box.width:
            line_height = (font_size * line_spacing) / 72
            return line_height <= box.height
        
        # Need multiple lines - estimate height
        estimator = TextHeightEstimator(line_spacing)
        estimated_height = estimator.estimate(text, font_size, box.width)
        return estimated_height <= box.height
    
    def _find_optimal_size(self, text: str, box: BoundingBox, 
                          config: TypographyConfig) -> float:
        """Binary search for optimal font size."""
        low = config.min_font_size
        high = config.preferred_font_size
        best = low
        
        while low <= high:
            mid = (low + high) / 2
            if self._text_fits(text, box, mid, config.line_spacing):
                best = mid
                low = mid + 0.5
            else:
                high = mid - 0.5
        
        return best
    
    def _count_lines(self, text: str, width: float, font_size: float) -> int:
        """Count number of lines text will wrap to."""
        if not text:
            return 0
        
        text_width = FontMetrics.calculate_text_width(text, font_size)
        if text_width <= width:
            return 1
        
        # Estimate lines
        estimator = TextHeightEstimator()
        lines = estimator._simulate_wrap(text, font_size, width)
        return len(lines)
    
    def _smart_truncate(self, text: str, box: BoundingBox, 
                       font_size: float, line_spacing: float) -> str:
        """Truncate text intelligently to fit in box."""
        estimator = TextHeightEstimator(line_spacing)
        
        # Binary search for max length that fits
        left, right = 0, len(text)
        while left < right:
            mid = (left + right + 1) // 2
            candidate = text[:mid].rstrip() + '...'
            if estimator.estimate(candidate, font_size, box.width) <= box.height:
                left = mid
            else:
                right = mid - 1
        
        if left > 3:
            return text[:left].rstrip() + '...'
        return text[:20] + '...'


class AdaptiveFontSizer:
    """
    Automatically sizes fonts based on content density and importance.
    """
    
    def __init__(self):
        self.typography = SmartTypographyEngine()
    
    def size_for_title(self, text: str, box: BoundingBox, is_hero: bool = False) -> Dict[str, Any]:
        """Get optimal size for title text."""
        preset = 'hero_title' if is_hero else 'slide_title'
        return self.typography.calculate_optimal_font_size(text, box, preset=preset)
    
    def size_for_body(self, text: str, box: BoundingBox, dense: bool = False) -> Dict[str, Any]:
        """Get optimal size for body text."""
        config = TYPOGRAPHY_PRESETS['body'].copy() if not dense else TypographyConfig(
            min_font_size=12, max_font_size=18, preferred_font_size=14,
            line_spacing=1.3, min_chars_per_line=35, max_chars_per_line=90
        )
        return self.typography.calculate_optimal_font_size(text, box, config)
    
    def size_for_bullets(self, items: List[str], box: BoundingBox) -> Dict[str, Any]:
        """
        Calculate optimal font size for a list of bullet points.
        All bullets should use the same size for consistency.
        """
        if not items:
            return {'font_size': 18, 'items': [], 'strategy': 'empty'}
        
        # Combine all text to estimate total space needed
        total_text = '\n'.join(items)
        num_items = len(items)
        
        # Adjust config based on number of items
        if num_items <= 3:
            config = TypographyConfig(
                min_font_size=16, max_font_size=24, preferred_font_size=20,
                line_spacing=1.6
            )
        elif num_items <= 5:
            config = TypographyConfig(
                min_font_size=14, max_font_size=20, preferred_font_size=18,
                line_spacing=1.5
            )
        else:
            config = TypographyConfig(
                min_font_size=12, max_font_size=18, preferred_font_size=16,
                line_spacing=1.4
            )
        
        result = self.typography.calculate_optimal_font_size(total_text, box, config)
        return {
            'font_size': result['font_size'],
            'items': items,
            'strategy': result['strategy']
        }


# Singleton instances for easy access
smart_typography = SmartTypographyEngine()
adaptive_sizer = AdaptiveFontSizer()


def fit_text_to_box(text: str, box: BoundingBox, 
                    base_size: float = 24.0, 
                    min_size: float = 14.0) -> Dict[str, Any]:
    """
    Convenience function to fit text to a box.
    
    Returns dict with 'text', 'font_size', and 'strategy'.
    """
    return smart_typography.fit_text_smart(
        text, box, 
        base_font_size=base_size, 
        min_font_size=min_size
    )


__all__ = [
    'TypographyConfig', 'TYPOGRAPHY_PRESETS',
    'SmartTypographyEngine', 'AdaptiveFontSizer',
    'smart_typography', 'adaptive_sizer', 'fit_text_to_box'
]

