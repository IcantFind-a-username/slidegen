"""
Design System - Visual Identity and Style Consistency

This module defines the complete visual design system for presentations.
It ensures every slide feels "designed" rather than "generated".

Design Philosophy:
1. CONSISTENCY over variety - Same rules applied everywhere
2. HIERARCHY through typography and color
3. WHITESPACE as a design element
4. ACCENT for emphasis, not decoration

Author: SlideGen Team
"""

from typing import Dict, Any, Tuple, List
from dataclasses import dataclass
from enum import Enum
from pptx.dml.color import RGBColor


# =============================================================================
# THEME DEFINITIONS
# =============================================================================

@dataclass
class ColorPalette:
    """Complete color palette for a theme."""
    # Core colors
    primary: str          # Main brand color, used for headers/emphasis
    secondary: str        # Supporting color, backgrounds
    accent: str           # Highlight color, CTAs, important elements
    
    # Neutrals
    background: str       # Slide background
    surface: str          # Card/container backgrounds
    border: str           # Subtle borders
    
    # Text colors
    text_primary: str     # Main text
    text_secondary: str   # Muted text
    text_on_primary: str  # Text on primary color
    text_on_accent: str   # Text on accent color
    
    # Status colors (optional)
    success: str = "#22c55e"
    warning: str = "#f59e0b"
    error: str = "#ef4444"
    info: str = "#3b82f6"
    
    def get_rgb(self, color_name: str) -> RGBColor:
        """Get RGBColor for a named color."""
        hex_color = getattr(self, color_name, self.primary)
        return self._hex_to_rgb(hex_color)
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> RGBColor:
        """Convert hex color to RGBColor."""
        hex_color = hex_color.lstrip('#')
        return RGBColor(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )


@dataclass
class TypographySpec:
    """Typography specifications for a theme."""
    # Font families
    heading_font: str
    body_font: str
    mono_font: str
    
    # Size scale (in points)
    size_hero: int = 48
    size_h1: int = 36
    size_h2: int = 28
    size_h3: int = 24
    size_h4: int = 20
    size_body: int = 16
    size_body_large: int = 18
    size_caption: int = 12
    size_small: int = 10
    
    # Line heights
    line_height_heading: float = 1.1
    line_height_body: float = 1.5
    
    # Letter spacing
    letter_spacing_heading: float = -0.02
    letter_spacing_body: float = 0


@dataclass
class SpacingSpec:
    """Spacing specifications for consistent layout."""
    # Page margins (inches)
    margin_x: float = 0.5
    margin_y: float = 0.4
    
    # Content spacing (inches)
    gap_small: float = 0.15
    gap_medium: float = 0.3
    gap_large: float = 0.5
    gap_xl: float = 0.8
    
    # Section padding
    section_padding: float = 0.4
    
    # Card padding
    card_padding: float = 0.25


# =============================================================================
# PREDEFINED THEMES
# =============================================================================

class ThemePreset(str, Enum):
    """Available theme presets."""
    CORPORATE_BLUE = "corporate_blue"
    MODERN_DARK = "modern_dark"
    ELEGANT_LIGHT = "elegant_light"
    TECH_GRADIENT = "tech_gradient"
    WARM_PROFESSIONAL = "warm_professional"
    MINIMAL_MONO = "minimal_mono"


THEME_PALETTES = {
    ThemePreset.CORPORATE_BLUE: ColorPalette(
        primary="#1e3a5f",
        secondary="#2d5a87",
        accent="#e07b39",
        background="#ffffff",
        surface="#f8fafc",
        border="#e2e8f0",
        text_primary="#1e293b",
        text_secondary="#64748b",
        text_on_primary="#ffffff",
        text_on_accent="#ffffff",
    ),
    ThemePreset.MODERN_DARK: ColorPalette(
        primary="#0f172a",
        secondary="#1e293b",
        accent="#38bdf8",
        background="#0f172a",
        surface="#1e293b",
        border="#334155",
        text_primary="#f8fafc",
        text_secondary="#94a3b8",
        text_on_primary="#ffffff",
        text_on_accent="#0f172a",
    ),
    ThemePreset.ELEGANT_LIGHT: ColorPalette(
        primary="#18181b",
        secondary="#3f3f46",
        accent="#a855f7",
        background="#fafafa",
        surface="#ffffff",
        border="#e4e4e7",
        text_primary="#18181b",
        text_secondary="#71717a",
        text_on_primary="#ffffff",
        text_on_accent="#ffffff",
    ),
    ThemePreset.TECH_GRADIENT: ColorPalette(
        primary="#4f46e5",
        secondary="#7c3aed",
        accent="#22d3ee",
        background="#ffffff",
        surface="#f5f3ff",
        border="#e0e7ff",
        text_primary="#1e1b4b",
        text_secondary="#6366f1",
        text_on_primary="#ffffff",
        text_on_accent="#1e1b4b",
    ),
    ThemePreset.WARM_PROFESSIONAL: ColorPalette(
        primary="#7c2d12",
        secondary="#9a3412",
        accent="#f59e0b",
        background="#fffbeb",
        surface="#fef3c7",
        border="#fcd34d",
        text_primary="#451a03",
        text_secondary="#92400e",
        text_on_primary="#ffffff",
        text_on_accent="#451a03",
    ),
    ThemePreset.MINIMAL_MONO: ColorPalette(
        primary="#171717",
        secondary="#404040",
        accent="#171717",
        background="#ffffff",
        surface="#fafafa",
        border="#e5e5e5",
        text_primary="#171717",
        text_secondary="#737373",
        text_on_primary="#ffffff",
        text_on_accent="#ffffff",
    ),
}

THEME_TYPOGRAPHY = {
    ThemePreset.CORPORATE_BLUE: TypographySpec(
        heading_font="Calibri Light",
        body_font="Calibri",
        mono_font="Consolas",
    ),
    ThemePreset.MODERN_DARK: TypographySpec(
        heading_font="Segoe UI Light",
        body_font="Segoe UI",
        mono_font="Cascadia Code",
    ),
    ThemePreset.ELEGANT_LIGHT: TypographySpec(
        heading_font="Georgia",
        body_font="Arial",
        mono_font="Courier New",
    ),
    ThemePreset.TECH_GRADIENT: TypographySpec(
        heading_font="Segoe UI Semibold",
        body_font="Segoe UI",
        mono_font="Consolas",
    ),
    ThemePreset.WARM_PROFESSIONAL: TypographySpec(
        heading_font="Cambria",
        body_font="Calibri",
        mono_font="Consolas",
    ),
    ThemePreset.MINIMAL_MONO: TypographySpec(
        heading_font="Arial",
        body_font="Arial",
        mono_font="Courier New",
    ),
}


# =============================================================================
# DESIGN SYSTEM CLASS
# =============================================================================

class DesignSystem:
    """
    Complete design system for presentations.
    Provides consistent styling rules across all slides.
    """
    
    def __init__(self, theme: ThemePreset = ThemePreset.CORPORATE_BLUE):
        self.theme = theme
        self.palette = THEME_PALETTES.get(theme, THEME_PALETTES[ThemePreset.CORPORATE_BLUE])
        self.typography = THEME_TYPOGRAPHY.get(theme, THEME_TYPOGRAPHY[ThemePreset.CORPORATE_BLUE])
        self.spacing = SpacingSpec()
    
    # -------------------------------------------------------------------------
    # Color Utilities
    # -------------------------------------------------------------------------
    
    def get_color(self, name: str) -> RGBColor:
        """Get a named color as RGBColor."""
        return self.palette.get_rgb(name)
    
    def lighten(self, color: RGBColor, amount: float = 0.2) -> RGBColor:
        """Lighten a color by mixing with white."""
        return RGBColor(
            min(255, int(color[0] + (255 - color[0]) * amount)),
            min(255, int(color[1] + (255 - color[1]) * amount)),
            min(255, int(color[2] + (255 - color[2]) * amount))
        )
    
    def darken(self, color: RGBColor, amount: float = 0.2) -> RGBColor:
        """Darken a color by mixing with black."""
        return RGBColor(
            int(color[0] * (1 - amount)),
            int(color[1] * (1 - amount)),
            int(color[2] * (1 - amount))
        )
    
    def with_opacity(self, color: RGBColor, opacity: float) -> RGBColor:
        """Simulate opacity by blending with background."""
        bg = self.palette.get_rgb('background')
        return RGBColor(
            int(color[0] * opacity + bg[0] * (1 - opacity)),
            int(color[1] * opacity + bg[1] * (1 - opacity)),
            int(color[2] * opacity + bg[2] * (1 - opacity))
        )
    
    # -------------------------------------------------------------------------
    # Typography Utilities
    # -------------------------------------------------------------------------
    
    def get_font_size(self, element: str) -> int:
        """Get font size for an element type."""
        sizes = {
            'hero': self.typography.size_hero,
            'h1': self.typography.size_h1,
            'h2': self.typography.size_h2,
            'h3': self.typography.size_h3,
            'h4': self.typography.size_h4,
            'body': self.typography.size_body,
            'body_large': self.typography.size_body_large,
            'caption': self.typography.size_caption,
            'small': self.typography.size_small,
        }
        return sizes.get(element, self.typography.size_body)
    
    def get_heading_font(self) -> str:
        """Get heading font family."""
        return self.typography.heading_font
    
    def get_body_font(self) -> str:
        """Get body font family."""
        return self.typography.body_font
    
    # -------------------------------------------------------------------------
    # Layout Utilities
    # -------------------------------------------------------------------------
    
    def get_content_bounds(self, slide_width: float, slide_height: float) -> Dict[str, float]:
        """Get content area bounds (inside margins)."""
        return {
            'left': self.spacing.margin_x,
            'top': self.spacing.margin_y,
            'width': slide_width - 2 * self.spacing.margin_x,
            'height': slide_height - 2 * self.spacing.margin_y,
        }
    
    def get_title_area(self, slide_width: float) -> Dict[str, float]:
        """Get title area bounds."""
        return {
            'left': self.spacing.margin_x,
            'top': self.spacing.margin_y,
            'width': slide_width - 2 * self.spacing.margin_x,
            'height': 1.2,  # Standard title height
        }
    
    def get_body_area(self, slide_width: float, slide_height: float) -> Dict[str, float]:
        """Get body content area bounds."""
        title_height = 1.2
        return {
            'left': self.spacing.margin_x,
            'top': self.spacing.margin_y + title_height + self.spacing.gap_large,
            'width': slide_width - 2 * self.spacing.margin_x,
            'height': slide_height - self.spacing.margin_y - title_height - self.spacing.gap_large - 0.5,
        }


# =============================================================================
# VISUAL HIERARCHY RULES
# =============================================================================

class VisualHierarchy:
    """
    Defines visual hierarchy rules for content emphasis.
    
    Hierarchy Levels:
    1. HERO: Title/main message (largest, boldest)
    2. PRIMARY: Section headers, key points
    3. SECONDARY: Supporting content, details
    4. TERTIARY: Captions, metadata
    """
    
    @staticmethod
    def get_emphasis_style(level: str, design: DesignSystem) -> Dict[str, Any]:
        """Get style for an emphasis level."""
        
        styles = {
            'hero': {
                'font_size': design.typography.size_hero,
                'font_name': design.typography.heading_font,
                'color': design.get_color('primary'),
                'bold': True,
                'line_spacing': design.typography.line_height_heading,
            },
            'primary': {
                'font_size': design.typography.size_h2,
                'font_name': design.typography.heading_font,
                'color': design.get_color('text_primary'),
                'bold': True,
                'line_spacing': design.typography.line_height_heading,
            },
            'secondary': {
                'font_size': design.typography.size_body_large,
                'font_name': design.typography.body_font,
                'color': design.get_color('text_primary'),
                'bold': False,
                'line_spacing': design.typography.line_height_body,
            },
            'tertiary': {
                'font_size': design.typography.size_caption,
                'font_name': design.typography.body_font,
                'color': design.get_color('text_secondary'),
                'bold': False,
                'line_spacing': design.typography.line_height_body,
            },
            'accent': {
                'font_size': design.typography.size_body,
                'font_name': design.typography.heading_font,
                'color': design.get_color('accent'),
                'bold': True,
                'line_spacing': design.typography.line_height_body,
            },
        }
        
        return styles.get(level, styles['secondary'])


# =============================================================================
# LAYOUT TEMPLATES
# =============================================================================

class LayoutTemplate:
    """
    Predefined layout templates for different slide types.
    Each template defines regions where content can be placed.
    """
    
    SLIDE_WIDTH = 13.333  # inches
    SLIDE_HEIGHT = 7.5    # inches
    
    @classmethod
    def hero(cls, design: DesignSystem) -> Dict[str, Dict[str, float]]:
        """Full-width hero layout for impact."""
        return {
            'header': {
                'left': 0, 'top': 0,
                'width': cls.SLIDE_WIDTH, 'height': 3.5,
            },
            'title': {
                'left': design.spacing.margin_x,
                'top': 0.8,
                'width': cls.SLIDE_WIDTH - 2 * design.spacing.margin_x,
                'height': 2.0,
            },
            'subtitle': {
                'left': design.spacing.margin_x,
                'top': 4.0,
                'width': cls.SLIDE_WIDTH - 2 * design.spacing.margin_x,
                'height': 1.0,
            },
        }
    
    @classmethod
    def standard(cls, design: DesignSystem) -> Dict[str, Dict[str, float]]:
        """Standard content layout with title and body."""
        return {
            'title_bar': {
                'left': 0, 'top': 0,
                'width': cls.SLIDE_WIDTH, 'height': 1.3,
            },
            'title': {
                'left': design.spacing.margin_x + 0.7,
                'top': 0.25,
                'width': cls.SLIDE_WIDTH - 2 * design.spacing.margin_x - 0.7,
                'height': 0.9,
            },
            'body': {
                'left': design.spacing.margin_x,
                'top': 1.5,
                'width': cls.SLIDE_WIDTH - 2 * design.spacing.margin_x,
                'height': 5.5,
            },
        }
    
    @classmethod
    def two_column(cls, design: DesignSystem) -> Dict[str, Dict[str, float]]:
        """Two-column layout for comparison."""
        col_width = (cls.SLIDE_WIDTH - 2 * design.spacing.margin_x - design.spacing.gap_large) / 2
        return {
            'title': {
                'left': design.spacing.margin_x,
                'top': design.spacing.margin_y,
                'width': cls.SLIDE_WIDTH - 2 * design.spacing.margin_x,
                'height': 1.0,
            },
            'left_column': {
                'left': design.spacing.margin_x,
                'top': 1.7,
                'width': col_width,
                'height': 5.3,
            },
            'right_column': {
                'left': design.spacing.margin_x + col_width + design.spacing.gap_large,
                'top': 1.7,
                'width': col_width,
                'height': 5.3,
            },
        }
    
    @classmethod
    def content_with_image(cls, design: DesignSystem, image_position: str = "right") -> Dict[str, Dict[str, float]]:
        """Content layout with image area."""
        content_width = (cls.SLIDE_WIDTH - 2 * design.spacing.margin_x) * 0.55
        image_width = (cls.SLIDE_WIDTH - 2 * design.spacing.margin_x) * 0.4
        
        if image_position == "right":
            content_left = design.spacing.margin_x
            image_left = cls.SLIDE_WIDTH - design.spacing.margin_x - image_width
        else:
            content_left = design.spacing.margin_x + image_width + design.spacing.gap_large
            image_left = design.spacing.margin_x
        
        return {
            'title': {
                'left': design.spacing.margin_x,
                'top': design.spacing.margin_y,
                'width': cls.SLIDE_WIDTH - 2 * design.spacing.margin_x,
                'height': 1.0,
            },
            'content': {
                'left': content_left,
                'top': 1.5,
                'width': content_width,
                'height': 5.5,
            },
            'image': {
                'left': image_left,
                'top': 1.5,
                'width': image_width,
                'height': 5.0,
            },
        }
    
    @classmethod
    def cards_grid(cls, design: DesignSystem, num_cards: int = 4) -> Dict[str, Dict[str, float]]:
        """Grid layout for card-style content."""
        cols = 2
        rows = (num_cards + 1) // 2
        
        total_width = cls.SLIDE_WIDTH - 2 * design.spacing.margin_x
        total_height = 4.8
        card_width = (total_width - design.spacing.gap_medium) / cols
        card_height = (total_height - design.spacing.gap_medium * (rows - 1)) / rows
        
        regions = {
            'title': {
                'left': design.spacing.margin_x,
                'top': design.spacing.margin_y,
                'width': total_width,
                'height': 1.0,
            },
        }
        
        for i in range(num_cards):
            row = i // cols
            col = i % cols
            regions[f'card_{i}'] = {
                'left': design.spacing.margin_x + col * (card_width + design.spacing.gap_medium),
                'top': 1.7 + row * (card_height + design.spacing.gap_medium),
                'width': card_width,
                'height': card_height,
            }
        
        return regions
    
    @classmethod
    def metrics(cls, design: DesignSystem, num_metrics: int = 4) -> Dict[str, Dict[str, float]]:
        """Layout for data/metrics display."""
        total_width = cls.SLIDE_WIDTH - 2 * design.spacing.margin_x
        metric_width = (total_width - design.spacing.gap_medium * (num_metrics - 1)) / num_metrics
        
        regions = {
            'title': {
                'left': design.spacing.margin_x,
                'top': design.spacing.margin_y,
                'width': total_width,
                'height': 1.0,
            },
        }
        
        for i in range(num_metrics):
            regions[f'metric_{i}'] = {
                'left': design.spacing.margin_x + i * (metric_width + design.spacing.gap_medium),
                'top': 1.8,
                'width': metric_width,
                'height': 2.5,
            }
        
        regions['detail'] = {
            'left': design.spacing.margin_x,
            'top': 4.5,
            'width': total_width,
            'height': 2.5,
        }
        
        return regions


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'ColorPalette',
    'TypographySpec',
    'SpacingSpec',
    'ThemePreset',
    'DesignSystem',
    'VisualHierarchy',
    'LayoutTemplate',
    'THEME_PALETTES',
    'THEME_TYPOGRAPHY',
]

