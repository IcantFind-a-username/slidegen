"""PPTX Engine - 主入口"""

import time
from typing import Dict, Any, List
from pptx import Presentation
from pptx.util import Inches
from .renderer import SlideRenderer
from .metrics import LayoutQualityEvaluator, MetricsResult
from .themes import COLOR_SCHEMES, get_theme, list_themes
from .overflow import BoundingBox


class PPTXEngine:
    """PPTX生成引擎"""
    
    def __init__(self, theme: str = "corporate_blue"):
        self.theme = get_theme(theme)
        self.renderer = SlideRenderer(self.theme)
        self.evaluator = LayoutQualityEvaluator()
    
    def generate(self, slidedeck: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        start = time.time()
        try:
            prs = Presentation()
            prs.slide_width = Inches(self.renderer.WIDTH)
            prs.slide_height = Inches(self.renderer.HEIGHT)
            
            slides = slidedeck.get('slides', [])
            for slide_data in slides:
                self.renderer.render(prs, slide_data)
            
            prs.save(output_path)
            metrics = self._evaluate(slides)
            
            return {
                'success': True,
                'output_path': output_path,
                'num_slides': len(slides),
                'elapsed_time': round(time.time() - start, 3),
                'metrics': metrics.to_dict(),
                'warnings': []
            }
        except Exception as e:
            return {'success': False, 'error_message': str(e), 'warnings': []}
    
    def _evaluate(self, slides: List[Dict]) -> MetricsResult:
        texts, boxes, sizes = [], [], []
        for s in slides:
            layout = self.renderer.get_layout(s.get('slide_type', 'content'))
            if s.get('title'):
                texts.append(s['title'])
                boxes.append(layout['title'])
                sizes.append(28)
            points = s.get('body_points', [])
            if points:
                body = '\n'.join(p.get('text', '') if isinstance(p, dict) else str(p) for p in points)
                texts.append(body)
                boxes.append(layout.get('content', layout['title']))
                sizes.append(18)
        return self.evaluator.evaluate(texts, boxes, sizes)
    
    @staticmethod
    def get_available_themes() -> List[str]:
        return list_themes()


def generate_pptx(slidedeck_json: Dict, output_path: str,
                  theme: str = "corporate_blue") -> Dict[str, Any]:
    """便捷函数"""
    engine = PPTXEngine(theme=theme)
    return engine.generate(slidedeck_json, output_path)


__all__ = ['PPTXEngine', 'generate_pptx']