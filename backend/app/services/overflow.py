"""文本溢出处理引擎"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re


@dataclass
class BoundingBox:
    """边界框（英寸）"""
    left: float
    top: float
    width: float
    height: float
    
    def to_emu(self) -> Tuple[int, int, int, int]:
        EMU = 914400
        return (int(self.left * EMU), int(self.top * EMU),
                int(self.width * EMU), int(self.height * EMU))
    
    @property
    def area(self) -> float:
        return self.width * self.height


class FontMetrics:
    """字体度量计算器"""
    
    CHAR_WIDTH = {'narrow': 0.30, 'normal': 0.55, 'wide': 0.70, 'cjk': 1.00, 'space': 0.28}
    NARROW_CHARS = set('iljI1!|.,:;\'\"')
    WIDE_CHARS = set('mwMWABCDEGHKNOPQRSUVXYZ')
    
    @classmethod
    def _is_cjk(cls, char: str) -> bool:
        code = ord(char)
        return (0x4E00 <= code <= 0x9FFF or 0x3000 <= code <= 0x303F or
                0x3040 <= code <= 0x309F or 0x30A0 <= code <= 0x30FF)
    
    @classmethod
    def calculate_text_width(cls, text: str, font_size: float) -> float:
        if not text:
            return 0.0
        em = font_size / 72
        total = 0
        for c in text:
            if c == ' ':
                total += cls.CHAR_WIDTH['space']
            elif cls._is_cjk(c):
                total += cls.CHAR_WIDTH['cjk']
            elif c in cls.NARROW_CHARS:
                total += cls.CHAR_WIDTH['narrow']
            elif c in cls.WIDE_CHARS:
                total += cls.CHAR_WIDTH['wide']
            else:
                total += cls.CHAR_WIDTH['normal']
        return total * em


class TextHeightEstimator:
    """文本高度估算器"""
    
    def __init__(self, line_spacing: float = 1.15):
        self.line_spacing = line_spacing
    
    def estimate(self, text: str, font_size: float, box_width: float) -> float:
        if not text:
            return 0.0
        lines = self._simulate_wrap(text, font_size, box_width)
        line_height = (font_size * self.line_spacing) / 72
        return len(lines) * line_height
    
    def _simulate_wrap(self, text: str, font_size: float, width: float) -> List[str]:
        lines = []
        for para in text.split('\n'):
            if not para:
                lines.append('')
                continue
            current, current_w = '', 0.0
            for word in para.split(' '):
                word_w = FontMetrics.calculate_text_width(word + ' ', font_size)
                if current_w + word_w <= width:
                    current += word + ' '
                    current_w += word_w
                else:
                    if current:
                        lines.append(current.strip())
                    current, current_w = word + ' ', word_w
            if current:
                lines.append(current.strip())
        return lines or ['']


class IOverflowStrategy(ABC):
    """溢出策略接口"""
    
    @abstractmethod
    def can_handle(self, text: str, box: BoundingBox, font_size: float) -> bool:
        pass
    
    @abstractmethod
    def apply(self, text: str, box: BoundingBox, font_size: float) -> Dict[str, Any]:
        pass
    
    @property
    @abstractmethod
    def priority(self) -> int:
        pass


class FontReductionStrategy(IOverflowStrategy):
    """策略1: 字号缩减"""
    
    def __init__(self, min_font: float = 12.0, step: float = 2.0):
        self.min_font = min_font
        self.step = step
        self.estimator = TextHeightEstimator()
    
    @property
    def priority(self) -> int:
        return 1
    
    def can_handle(self, text: str, box: BoundingBox, font_size: float) -> bool:
        for f in range(int(font_size - self.step), int(self.min_font) - 1, -int(self.step)):
            if self.estimator.estimate(text, f, box.width) <= box.height:
                return True
        return False
    
    def apply(self, text: str, box: BoundingBox, font_size: float) -> Dict[str, Any]:
        for f in range(int(font_size - self.step), int(self.min_font) - 1, -int(self.step)):
            if self.estimator.estimate(text, f, box.width) <= box.height:
                return {'text': text, 'font_size': float(f), 'strategy': 'font_reduction'}
        return {'text': text, 'font_size': self.min_font, 'strategy': 'font_reduction_max'}


class SmartTruncationStrategy(IOverflowStrategy):
    """策略2: 智能截断"""
    
    def __init__(self, min_retention: float = 0.3):
        self.min_retention = min_retention
        self.estimator = TextHeightEstimator()
    
    @property
    def priority(self) -> int:
        return 2
    
    def can_handle(self, text: str, box: BoundingBox, font_size: float) -> bool:
        sentences = re.split(r'(?<=[.!?。！？])\s*', text)
        if len(sentences) <= 1:
            return False
        selected = []
        for s in sentences:
            candidate = ' '.join(selected + [s]) + '...'
            if self.estimator.estimate(candidate, font_size, box.width) <= box.height:
                selected.append(s)
        return len(selected) / len(sentences) >= self.min_retention
    
    def apply(self, text: str, box: BoundingBox, font_size: float) -> Dict[str, Any]:
        sentences = re.split(r'(?<=[.!?。！？])\s*', text)
        selected = []
        for s in sentences:
            candidate = ' '.join(selected + [s]) + '...'
            if self.estimator.estimate(candidate, font_size, box.width) <= box.height:
                selected.append(s)
            else:
                break
        truncated = ' '.join(selected) + '...' if selected else text[:50] + '...'
        return {'text': truncated, 'font_size': font_size, 'strategy': 'smart_truncation'}


class TextOverflowEngine:
    """文本溢出处理引擎"""
    
    def __init__(self, strategies: Optional[List[IOverflowStrategy]] = None):
        self.estimator = TextHeightEstimator()
        self.strategies = strategies or [FontReductionStrategy(), SmartTruncationStrategy()]
        self.strategies.sort(key=lambda s: s.priority)
    
    def fit_text(self, text: str, box: BoundingBox, font_size: float = 18.0) -> Dict[str, Any]:
        if not text:
            return {'text': '', 'font_size': font_size, 'strategy': 'empty'}
        
        if self.estimator.estimate(text, font_size, box.width) <= box.height:
            return {'text': text, 'font_size': font_size, 'strategy': 'direct_fit'}
        
        for strategy in self.strategies:
            if strategy.can_handle(text, box, font_size):
                return strategy.apply(text, box, font_size)
        
        return self._force_truncate(text, box)
    
    def _force_truncate(self, text: str, box: BoundingBox) -> Dict[str, Any]:
        min_font = 12.0
        left, right = 0, len(text)
        while left < right:
            mid = (left + right + 1) // 2
            if self.estimator.estimate(text[:mid] + '...', min_font, box.width) <= box.height:
                left = mid
            else:
                right = mid - 1
        return {'text': text[:left] + '...' if left > 0 else '...', 
                'font_size': min_font, 'strategy': 'force_truncate'}


__all__ = ['BoundingBox', 'FontMetrics', 'TextHeightEstimator', 
           'IOverflowStrategy', 'FontReductionStrategy', 
           'SmartTruncationStrategy', 'TextOverflowEngine']