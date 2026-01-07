"""主题配色系统"""

from dataclasses import dataclass
from typing import Dict, List
from pptx.dml.color import RGBColor


@dataclass
class ThemeColorScheme:
    """主题配色方案"""
    name: str
    primary: str
    secondary: str
    accent: str
    background: str
    text_dark: str
    text_light: str
    
    def get_rgb(self, color_name: str) -> RGBColor:
        hex_color = getattr(self, color_name, self.text_dark).lstrip('#')
        return RGBColor(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )


COLOR_SCHEMES: Dict[str, ThemeColorScheme] = {
    'corporate_blue': ThemeColorScheme(
        name='Corporate Blue',
        primary='#1E3A5F',
        secondary='#4A90A4',
        accent='#F5A623',
        background='#FFFFFF',
        text_dark='#1A1A1A',
        text_light='#FFFFFF'
    ),
    'modern_green': ThemeColorScheme(
        name='Modern Green',
        primary='#2D5A27',
        secondary='#7CB342',
        accent='#FFB300',
        background='#FAFAFA',
        text_dark='#212121',
        text_light='#FFFFFF'
    ),
    'elegant_purple': ThemeColorScheme(
        name='Elegant Purple',
        primary='#4A148C',
        secondary='#7B1FA2',
        accent='#E91E63',
        background='#FFFFFF',
        text_dark='#1A1A1A',
        text_light='#FFFFFF'
    ),
    'warm_orange': ThemeColorScheme(
        name='Warm Orange',
        primary='#E65100',
        secondary='#FF9800',
        accent='#795548',
        background='#FFF8E1',
        text_dark='#3E2723',
        text_light='#FFFFFF'
    ),
    'tech_dark': ThemeColorScheme(
        name='Tech Dark',
        primary='#1A237E',
        secondary='#3949AB',
        accent='#00BCD4',
        background='#ECEFF1',
        text_dark='#263238',
        text_light='#FFFFFF'
    ),
}


def get_theme(theme_name: str) -> ThemeColorScheme:
    if theme_name not in COLOR_SCHEMES:
        raise KeyError(f"Theme '{theme_name}' not found")
    return COLOR_SCHEMES[theme_name]


def list_themes() -> List[str]:
    return list(COLOR_SCHEMES.keys())


__all__ = ['ThemeColorScheme', 'COLOR_SCHEMES', 'get_theme', 'list_themes']