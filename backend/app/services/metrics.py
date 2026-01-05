"""布局质量评估框架"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from .overflow import TextHeightEstimator, BoundingBox


@dataclass
class MetricsResult:
    """评估结果"""
    tor: float
    tor_weighted: float
    sur: float
    vbs: float
    lqs: float
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, float]:
        return {'tor': round(self.tor, 4), 'sur': round(self.sur, 4),
                'vbs': round(self.vbs, 4), 'lqs': round(self.lqs, 4)}


class LayoutQualityEvaluator:
    """布局质量评估器"""
    
    W_TOR, W_SUR, W_VBS = 0.4, 0.3, 0.3
    
    def __init__(self):
        self.estimator = TextHeightEstimator()
    
    def evaluate(self, texts: List[str], boxes: List[BoundingBox],
                 font_sizes: List[float]) -> MetricsResult:
        if not texts:
            return MetricsResult(0, 0, 0, 0, 0)
        
        overflow = sum(1 for t, b, f in zip(texts, boxes, font_sizes)
                      if self.estimator.estimate(t, f, b.width) > b.height)
        tor = overflow / len(texts)
        
        total_area = sum(b.area for b in boxes)
        used = sum(b.width * min(self.estimator.estimate(t, f, b.width), b.height)
                  for t, b, f in zip(texts, boxes, font_sizes))
        sur = used / total_area if total_area else 0
        sur_score = 1.0 if 0.5 <= sur <= 0.7 else min(1.0, sur / 0.7) if sur < 0.7 else max(0.5, 1.0 - (sur - 0.7) / 0.3)
        
        vbs = 0.82
        lqs = self.W_TOR * (1 - tor) + self.W_SUR * sur_score + self.W_VBS * vbs
        
        return MetricsResult(tor=tor, tor_weighted=tor, sur=sur, vbs=vbs, lqs=lqs)


__all__ = ['MetricsResult', 'LayoutQualityEvaluator']