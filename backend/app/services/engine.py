"""PPTX Engine - 主入口"""

import time
from typing import Dict, Any, List
from pptx import Presentation
from pptx.util import Inches
from .metrics import LayoutQualityEvaluator, MetricsResult
from .themes import COLOR_SCHEMES, get_theme, list_themes
from .overflow import BoundingBox

# Try Pro renderer first, then V2, then V1
try:
    from .renderer_pro import SlideRendererPro as SlideRenderer
    print("✓ Using Renderer Pro (Meeting-Ready)")
except ImportError:
    try:
        from .renderer_v2 import SlideRendererV2 as SlideRenderer
        print("✓ Using Renderer V2 (Professional)")
    except ImportError:
        from .renderer import SlideRenderer
        print("⚠ Using Renderer V1 (Basic)")


class PPTXEngine:
    """PPTX生成引擎 - V2版本支持更好的视觉效果"""
    
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
            for i, slide_data in enumerate(slides):
                try:
                    self.renderer.render(prs, slide_data)
                except Exception as slide_err:
                    import traceback
                    print(f"Error rendering slide {i+1}:")
                    print(f"  Slide type: {slide_data.get('slide_type', 'unknown')}")
                    print(f"  Intent: {slide_data.get('intent', 'unknown')}")
                    print(f"  Title: {slide_data.get('title', 'N/A')[:50]}")
                    print(f"  Error: {slide_err}")
                    traceback.print_exc()
                    raise
            
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
            import traceback
            traceback.print_exc()
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