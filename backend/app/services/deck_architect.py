"""
Deck Architect - System-Level Presentation Structure Control

This module enforces strict deck structure, prevents repetition, and ensures
every presentation follows a professional narrative arc.

Design Philosophy:
- PPT generation is a LAYOUT-CONSTRAINED, DESIGN-AWARE rendering problem
- Every slide has a unique purpose (intent) and position in the narrative
- Repetition is a bug, not a feature

Author: SlideGen Team
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# =============================================================================
# SLIDE INTENT CLASSIFICATION (Extended)
# =============================================================================

class SlideIntent(str, Enum):
    """
    Comprehensive slide intent classification.
    Each intent has specific structural and visual requirements.
    """
    # === OPENING SECTION ===
    COVER = "cover"                          # Title slide, always exactly ONE
    AGENDA = "agenda"                        # Optional roadmap
    
    # === FRAMING SECTION ===
    VISION = "vision"                        # Why this matters, big picture
    CONTEXT = "context"                      # Background, setting the stage
    
    # === CORE CONTENT SECTION ===
    CONCEPT = "concept"                      # Definition, "What is X?"
    FRAMEWORK = "framework"                  # Methodology, process, how it works
    COMPARISON = "comparison"                # A vs B, trade-offs
    CASE_STUDY = "case_study"               # Real-world example with depth
    DATA_INSIGHT = "data_insight"           # Statistics, metrics, findings
    KEY_POINTS = "key_points"               # Main arguments or features
    
    # === ANALYSIS SECTION ===
    IMPLICATIONS = "implications"            # So what? Consequences
    BENEFITS = "benefits"                    # Advantages, value proposition
    RISKS = "risks"                          # Challenges, limitations
    
    # === FORWARD-LOOKING SECTION ===
    FUTURE = "future"                        # Predictions, roadmap
    RECOMMENDATIONS = "recommendations"      # Suggested actions
    
    # === CLOSING SECTION ===
    SUMMARY = "summary"                      # Key takeaways (exactly ONE)
    CALL_TO_ACTION = "call_to_action"       # What to do next (exactly ONE)
    CLOSING = "closing"                      # Thank you, Q&A (exactly ONE)


# =============================================================================
# DECK STRUCTURE TEMPLATES
# =============================================================================

@dataclass
class SectionDefinition:
    """Defines a section in the deck structure."""
    name: str
    required: bool
    allowed_intents: List[SlideIntent]
    min_slides: int
    max_slides: int
    order: int  # Position in the deck


# Mandatory deck structure - enforced for every presentation
DECK_STRUCTURE = {
    "opening": SectionDefinition(
        name="Opening",
        required=True,
        allowed_intents=[SlideIntent.COVER],
        min_slides=1,
        max_slides=1,
        order=0
    ),
    "framing": SectionDefinition(
        name="Framing",
        required=True,
        allowed_intents=[SlideIntent.AGENDA, SlideIntent.VISION, SlideIntent.CONTEXT],
        min_slides=1,
        max_slides=2,
        order=1
    ),
    "core_content": SectionDefinition(
        name="Core Content",
        required=True,
        allowed_intents=[
            SlideIntent.CONCEPT, SlideIntent.FRAMEWORK, SlideIntent.COMPARISON,
            SlideIntent.CASE_STUDY, SlideIntent.DATA_INSIGHT, SlideIntent.KEY_POINTS
        ],
        min_slides=2,
        max_slides=8,
        order=2
    ),
    "analysis": SectionDefinition(
        name="Analysis",
        required=False,
        allowed_intents=[SlideIntent.IMPLICATIONS, SlideIntent.BENEFITS, SlideIntent.RISKS],
        min_slides=0,
        max_slides=3,
        order=3
    ),
    "forward_looking": SectionDefinition(
        name="Forward Looking",
        required=False,
        allowed_intents=[SlideIntent.FUTURE, SlideIntent.RECOMMENDATIONS],
        min_slides=0,
        max_slides=2,
        order=4
    ),
    "closing": SectionDefinition(
        name="Closing",
        required=True,
        allowed_intents=[SlideIntent.SUMMARY, SlideIntent.CALL_TO_ACTION, SlideIntent.CLOSING],
        min_slides=1,
        max_slides=2,
        order=5
    )
}


# =============================================================================
# UNIQUENESS CONSTRAINTS
# =============================================================================

# Intents that can only appear ONCE in a deck
SINGLETON_INTENTS = {
    SlideIntent.COVER,
    SlideIntent.AGENDA,
    SlideIntent.SUMMARY,
    SlideIntent.CALL_TO_ACTION,
    SlideIntent.CLOSING
}

# Intents that cannot appear consecutively
NO_CONSECUTIVE_INTENTS = {
    SlideIntent.DATA_INSIGHT,  # Data slides need variety between them
    SlideIntent.CASE_STUDY,    # Case studies should be interspersed
    SlideIntent.COMPARISON,    # Comparisons need setup
}

# Recommended flow patterns (intent A should be followed by intent B)
RECOMMENDED_TRANSITIONS = {
    SlideIntent.COVER: [SlideIntent.AGENDA, SlideIntent.VISION],
    SlideIntent.AGENDA: [SlideIntent.VISION, SlideIntent.CONTEXT, SlideIntent.CONCEPT],
    SlideIntent.VISION: [SlideIntent.AGENDA, SlideIntent.CONTEXT, SlideIntent.CONCEPT],
    SlideIntent.CONCEPT: [SlideIntent.FRAMEWORK, SlideIntent.KEY_POINTS, SlideIntent.COMPARISON],
    SlideIntent.FRAMEWORK: [SlideIntent.CASE_STUDY, SlideIntent.DATA_INSIGHT, SlideIntent.BENEFITS],
    SlideIntent.CASE_STUDY: [SlideIntent.IMPLICATIONS, SlideIntent.DATA_INSIGHT, SlideIntent.KEY_POINTS],
    SlideIntent.DATA_INSIGHT: [SlideIntent.IMPLICATIONS, SlideIntent.COMPARISON, SlideIntent.RECOMMENDATIONS],
    SlideIntent.RISKS: [SlideIntent.FUTURE, SlideIntent.RECOMMENDATIONS, SlideIntent.SUMMARY],
    SlideIntent.FUTURE: [SlideIntent.RECOMMENDATIONS, SlideIntent.CALL_TO_ACTION, SlideIntent.SUMMARY],
    SlideIntent.SUMMARY: [SlideIntent.CALL_TO_ACTION, SlideIntent.CLOSING],
    SlideIntent.CALL_TO_ACTION: [SlideIntent.CLOSING],
}


# =============================================================================
# IMAGE ROLE MAPPING
# =============================================================================

class ImageRole(str, Enum):
    """Semantic role of images for each slide type."""
    HERO = "hero"                    # Large, impactful, fills significant space
    ILLUSTRATIVE = "illustrative"    # Explains a concept visually
    DECORATIVE = "decorative"        # Adds visual interest, smaller
    ICON = "icon"                    # Small symbolic representation
    DATA_VIZ = "data_visualization"  # Charts, graphs (generated, not fetched)
    NONE = "none"                    # Text-only slide


# Intent to image role mapping
INTENT_IMAGE_ROLE = {
    SlideIntent.COVER: ImageRole.HERO,
    SlideIntent.VISION: ImageRole.HERO,
    SlideIntent.AGENDA: ImageRole.DECORATIVE,
    SlideIntent.CONTEXT: ImageRole.ILLUSTRATIVE,
    SlideIntent.CONCEPT: ImageRole.ILLUSTRATIVE,
    SlideIntent.FRAMEWORK: ImageRole.ICON,
    SlideIntent.COMPARISON: ImageRole.ICON,
    SlideIntent.CASE_STUDY: ImageRole.ILLUSTRATIVE,
    SlideIntent.DATA_INSIGHT: ImageRole.DATA_VIZ,
    SlideIntent.KEY_POINTS: ImageRole.ICON,
    SlideIntent.IMPLICATIONS: ImageRole.DECORATIVE,
    SlideIntent.BENEFITS: ImageRole.ICON,
    SlideIntent.RISKS: ImageRole.ICON,
    SlideIntent.FUTURE: ImageRole.HERO,
    SlideIntent.RECOMMENDATIONS: ImageRole.ICON,
    SlideIntent.SUMMARY: ImageRole.DECORATIVE,
    SlideIntent.CALL_TO_ACTION: ImageRole.HERO,
    SlideIntent.CLOSING: ImageRole.DECORATIVE,
}

# Image search keywords by intent
INTENT_IMAGE_KEYWORDS = {
    SlideIntent.COVER: ["abstract", "professional", "modern", "technology", "innovation"],
    SlideIntent.VISION: ["vision", "future", "horizon", "opportunity", "growth"],
    SlideIntent.CONTEXT: ["background", "foundation", "history", "landscape"],
    SlideIntent.CONCEPT: ["concept", "idea", "diagram", "illustration"],
    SlideIntent.FRAMEWORK: ["process", "methodology", "workflow", "system"],
    SlideIntent.CASE_STUDY: ["case study", "example", "real world", "application"],
    SlideIntent.DATA_INSIGHT: ["data", "analytics", "statistics", "metrics"],
    SlideIntent.RISKS: ["challenge", "risk", "warning", "caution"],
    SlideIntent.FUTURE: ["future", "tomorrow", "innovation", "aspirational"],
    SlideIntent.CLOSING: ["thank you", "questions", "discussion", "team"],
}


# =============================================================================
# LAYOUT CONFIGURATION
# =============================================================================

@dataclass
class LayoutConfig:
    """Layout configuration for a slide."""
    layout_type: str
    title_font_range: Tuple[int, int]  # (min, max) font size
    body_font_range: Tuple[int, int]
    max_bullets: int
    max_words_per_bullet: int
    image_role: ImageRole
    image_position: Optional[str]  # "left", "right", "background", "bottom"
    emphasis: str  # What to emphasize: "title", "content", "visual"


# Intent to layout configuration
INTENT_LAYOUT_CONFIG = {
    SlideIntent.COVER: LayoutConfig(
        layout_type="hero",
        title_font_range=(40, 56),
        body_font_range=(18, 24),
        max_bullets=0,
        max_words_per_bullet=0,
        image_role=ImageRole.HERO,
        image_position="background",
        emphasis="title"
    ),
    SlideIntent.AGENDA: LayoutConfig(
        layout_type="agenda",
        title_font_range=(24, 32),
        body_font_range=(16, 20),
        max_bullets=6,
        max_words_per_bullet=6,
        image_role=ImageRole.DECORATIVE,
        image_position=None,
        emphasis="content"
    ),
    SlideIntent.VISION: LayoutConfig(
        layout_type="hero",
        title_font_range=(36, 48),
        body_font_range=(18, 24),
        max_bullets=2,
        max_words_per_bullet=12,
        image_role=ImageRole.HERO,
        image_position="background",
        emphasis="title"
    ),
    SlideIntent.CONCEPT: LayoutConfig(
        layout_type="standard",
        title_font_range=(24, 32),
        body_font_range=(16, 20),
        max_bullets=4,
        max_words_per_bullet=12,
        image_role=ImageRole.ILLUSTRATIVE,
        image_position="right",
        emphasis="content"
    ),
    SlideIntent.FRAMEWORK: LayoutConfig(
        layout_type="process",
        title_font_range=(22, 28),
        body_font_range=(14, 18),
        max_bullets=5,
        max_words_per_bullet=10,
        image_role=ImageRole.ICON,
        image_position=None,
        emphasis="content"
    ),
    SlideIntent.COMPARISON: LayoutConfig(
        layout_type="comparison",
        title_font_range=(22, 28),
        body_font_range=(14, 18),
        max_bullets=4,
        max_words_per_bullet=8,
        image_role=ImageRole.ICON,
        image_position=None,
        emphasis="content"
    ),
    SlideIntent.CASE_STUDY: LayoutConfig(
        layout_type="case_study",
        title_font_range=(24, 30),
        body_font_range=(16, 20),
        max_bullets=4,
        max_words_per_bullet=12,
        image_role=ImageRole.ILLUSTRATIVE,
        image_position="left",
        emphasis="visual"
    ),
    SlideIntent.DATA_INSIGHT: LayoutConfig(
        layout_type="metrics",
        title_font_range=(22, 28),
        body_font_range=(14, 18),
        max_bullets=3,
        max_words_per_bullet=8,
        image_role=ImageRole.DATA_VIZ,
        image_position=None,
        emphasis="visual"
    ),
    SlideIntent.KEY_POINTS: LayoutConfig(
        layout_type="cards",
        title_font_range=(24, 30),
        body_font_range=(14, 18),
        max_bullets=4,
        max_words_per_bullet=10,
        image_role=ImageRole.ICON,
        image_position=None,
        emphasis="content"
    ),
    SlideIntent.CONTEXT: LayoutConfig(
        layout_type="standard",
        title_font_range=(24, 30),
        body_font_range=(16, 20),
        max_bullets=4,
        max_words_per_bullet=12,
        image_role=ImageRole.ILLUSTRATIVE,
        image_position="right",
        emphasis="content"
    ),
    SlideIntent.IMPLICATIONS: LayoutConfig(
        layout_type="standard",
        title_font_range=(24, 30),
        body_font_range=(16, 20),
        max_bullets=4,
        max_words_per_bullet=10,
        image_role=ImageRole.DECORATIVE,
        image_position=None,
        emphasis="content"
    ),
    SlideIntent.BENEFITS: LayoutConfig(
        layout_type="cards",
        title_font_range=(24, 30),
        body_font_range=(14, 18),
        max_bullets=4,
        max_words_per_bullet=10,
        image_role=ImageRole.ICON,
        image_position=None,
        emphasis="content"
    ),
    SlideIntent.RISKS: LayoutConfig(
        layout_type="standard",
        title_font_range=(24, 30),
        body_font_range=(16, 20),
        max_bullets=4,
        max_words_per_bullet=10,
        image_role=ImageRole.ICON,
        image_position=None,
        emphasis="content"
    ),
    SlideIntent.RECOMMENDATIONS: LayoutConfig(
        layout_type="standard",
        title_font_range=(24, 30),
        body_font_range=(16, 20),
        max_bullets=4,
        max_words_per_bullet=10,
        image_role=ImageRole.ICON,
        image_position=None,
        emphasis="content"
    ),
    SlideIntent.FUTURE: LayoutConfig(
        layout_type="hero",
        title_font_range=(32, 44),
        body_font_range=(18, 22),
        max_bullets=3,
        max_words_per_bullet=10,
        image_role=ImageRole.HERO,
        image_position="background",
        emphasis="title"
    ),
    SlideIntent.SUMMARY: LayoutConfig(
        layout_type="standard",
        title_font_range=(24, 30),
        body_font_range=(16, 20),
        max_bullets=5,
        max_words_per_bullet=8,
        image_role=ImageRole.DECORATIVE,
        image_position=None,
        emphasis="content"
    ),
    SlideIntent.CALL_TO_ACTION: LayoutConfig(
        layout_type="hero",
        title_font_range=(32, 44),
        body_font_range=(18, 24),
        max_bullets=3,
        max_words_per_bullet=8,
        image_role=ImageRole.HERO,
        image_position="background",
        emphasis="title"
    ),
    SlideIntent.CLOSING: LayoutConfig(
        layout_type="closing",
        title_font_range=(36, 48),
        body_font_range=(18, 24),
        max_bullets=0,
        max_words_per_bullet=0,
        image_role=ImageRole.DECORATIVE,
        image_position=None,
        emphasis="title"
    ),
}


# =============================================================================
# STRUCTURED INTERMEDIATE REPRESENTATION
# =============================================================================

@dataclass
class SlideSpec:
    """
    Complete specification for a single slide.
    This is the intermediate representation passed to the renderer.
    """
    # Identity
    slide_id: str
    slide_number: int
    section: str
    
    # Intent & purpose
    intent: SlideIntent
    claim: str  # The main message (becomes title)
    
    # Content
    title: str
    subtitle: Optional[str]
    body_points: List[Dict[str, Any]]
    speaker_notes: Optional[str]
    
    # Layout hints
    layout_type: str
    title_font_size: int
    body_font_size: int
    density: str  # "sparse", "balanced", "dense"
    
    # Visual elements
    image_role: ImageRole
    image_keywords: List[str]
    image_url: Optional[str]
    accent_color: Optional[str]
    
    # Metadata
    transition_hint: Optional[str]
    estimated_speaking_time: int  # seconds
    
    # Extra content for special layouts (comparison, etc.)
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "slide_id": self.slide_id,
            "slide_number": self.slide_number,
            "section": self.section,
            "intent": self.intent.value,
            "claim": self.claim,
            "title": self.title,
            "subtitle": self.subtitle,
            "body_points": self.body_points,
            "speaker_notes": self.speaker_notes,
            "layout_type": self.layout_type,
            "title_font_size": self.title_font_size,
            "body_font_size": self.body_font_size,
            "density": self.density,
            "image_role": self.image_role.value,
            "image_keywords": self.image_keywords,
            "image_url": self.image_url,
            "accent_color": self.accent_color,
            "transition_hint": self.transition_hint,
            "estimated_speaking_time": self.estimated_speaking_time,
        }
        # Merge extra_data (for comparison slides, etc.)
        result.update(self.extra_data)
        return result


@dataclass 
class DeckSpec:
    """
    Complete specification for an entire presentation.
    """
    # Metadata
    deck_id: str
    title: str
    subtitle: Optional[str]
    author: Optional[str]
    created_at: str
    
    # Theme
    theme_name: str
    primary_color: str
    secondary_color: str
    accent_color: str
    
    # Structure
    core_message: str
    presentation_type: str  # "explanatory", "persuasive", "analytical", "pitch"
    target_audience: str
    
    # Content
    slides: List[SlideSpec]
    
    # Validation
    is_valid: bool
    validation_errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "deck_id": self.deck_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "author": self.author,
            "created_at": self.created_at,
            "theme": {
                "name": self.theme_name,
                "primary_color": self.primary_color,
                "secondary_color": self.secondary_color,
                "accent_color": self.accent_color,
            },
            "core_message": self.core_message,
            "presentation_type": self.presentation_type,
            "target_audience": self.target_audience,
            "slides": [s.to_dict() for s in self.slides],
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
        }


# =============================================================================
# DECK VALIDATOR
# =============================================================================

class DeckValidator:
    """
    Validates deck structure and enforces constraints.
    """
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, slides: List[SlideSpec]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a list of slides against all constraints.
        Returns: (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        if not slides:
            self.errors.append("Deck has no slides")
            return False, self.errors, self.warnings
        
        # Check singleton constraints
        self._check_singletons(slides)
        
        # Check required sections
        self._check_required_sections(slides)
        
        # Check consecutiveness
        self._check_consecutive_intents(slides)
        
        # Check opening and closing
        self._check_opening_closing(slides)
        
        # Check for duplicate content
        self._check_duplicates(slides)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _check_singletons(self, slides: List[SlideSpec]):
        """Check that singleton intents appear only once."""
        intent_counts = {}
        for slide in slides:
            intent_counts[slide.intent] = intent_counts.get(slide.intent, 0) + 1
        
        for intent in SINGLETON_INTENTS:
            count = intent_counts.get(intent, 0)
            if count > 1:
                self.errors.append(
                    f"Intent '{intent.value}' appears {count} times but should appear at most once"
                )
    
    def _check_required_sections(self, slides: List[SlideSpec]):
        """Check that required sections are present."""
        section_intents = {s.section: set() for s in slides}
        for slide in slides:
            section_intents.setdefault(slide.section, set()).add(slide.intent)
        
        for section_name, section_def in DECK_STRUCTURE.items():
            if section_def.required:
                found_intents = section_intents.get(section_name, set())
                allowed = set(section_def.allowed_intents)
                if not found_intents.intersection(allowed):
                    self.errors.append(
                        f"Required section '{section_name}' is missing or has no valid slides"
                    )
    
    def _check_consecutive_intents(self, slides: List[SlideSpec]):
        """Check that certain intents don't appear consecutively."""
        for i in range(len(slides) - 1):
            current = slides[i].intent
            next_intent = slides[i + 1].intent
            
            if current in NO_CONSECUTIVE_INTENTS and current == next_intent:
                self.warnings.append(
                    f"Intent '{current.value}' appears consecutively at slides {i+1} and {i+2}. "
                    "Consider adding variety."
                )
    
    def _check_opening_closing(self, slides: List[SlideSpec]):
        """Check opening and closing constraints."""
        if slides[0].intent != SlideIntent.COVER:
            self.errors.append("First slide must be a COVER slide")
        
        # Check closing is near the end
        closing_intents = {SlideIntent.SUMMARY, SlideIntent.CALL_TO_ACTION, SlideIntent.CLOSING}
        last_two = [s.intent for s in slides[-2:]]
        if not any(intent in closing_intents for intent in last_two):
            self.warnings.append("No summary, call-to-action, or closing slide near the end")
    
    def _check_duplicates(self, slides: List[SlideSpec]):
        """Check for near-duplicate titles or claims."""
        titles = [s.title.lower().strip() for s in slides]
        seen = set()
        for i, title in enumerate(titles):
            # Simple similarity: exact match after normalization
            normalized = ' '.join(title.split())
            if normalized in seen:
                self.warnings.append(
                    f"Slide {i+1} has a title similar to a previous slide: '{title[:50]}...'"
                )
            seen.add(normalized)


# =============================================================================
# FONT SIZE CALCULATOR
# =============================================================================

class FontSizeCalculator:
    """
    Calculates optimal font sizes based on content density.
    
    Algorithm:
    1. Determine base size from intent's layout config
    2. Adjust based on text length (title) or item count/length (body)
    3. Ensure within min/max bounds
    4. Return recommended size
    """
    
    @staticmethod
    def calculate_title_size(
        title: str,
        intent: SlideIntent,
        config: LayoutConfig = None
    ) -> int:
        """
        Calculate optimal title font size.
        
        Rules:
        - Short titles (< 30 chars): Use max size
        - Medium titles (30-50 chars): Use mid-range
        - Long titles (> 50 chars): Use min size
        """
        if config is None:
            config = INTENT_LAYOUT_CONFIG.get(intent, INTENT_LAYOUT_CONFIG[SlideIntent.CONCEPT])
        
        min_size, max_size = config.title_font_range
        title_len = len(title)
        
        if title_len < 30:
            return max_size
        elif title_len < 50:
            # Linear interpolation
            ratio = (title_len - 30) / 20
            return int(max_size - ratio * (max_size - min_size))
        else:
            return min_size
    
    @staticmethod
    def calculate_body_size(
        items: List[Dict[str, Any]],
        intent: SlideIntent,
        config: LayoutConfig = None
    ) -> int:
        """
        Calculate optimal body font size.
        
        Rules:
        - Few items (1-2): Use max size
        - Medium items (3-4): Use mid-range
        - Many items (5+): Use min size
        - Also considers average word count per item
        """
        if config is None:
            config = INTENT_LAYOUT_CONFIG.get(intent, INTENT_LAYOUT_CONFIG[SlideIntent.CONCEPT])
        
        min_size, max_size = config.body_font_range
        
        if not items:
            return max_size
        
        num_items = len(items)
        avg_words = sum(len(str(item.get('text', '')).split()) for item in items) / num_items
        
        # Factor 1: Number of items
        if num_items <= 2:
            item_factor = 1.0
        elif num_items <= 4:
            item_factor = 0.7
        else:
            item_factor = 0.4
        
        # Factor 2: Average word count
        if avg_words <= 6:
            word_factor = 1.0
        elif avg_words <= 10:
            word_factor = 0.8
        else:
            word_factor = 0.6
        
        # Combined factor
        combined = (item_factor + word_factor) / 2
        return int(min_size + combined * (max_size - min_size))
    
    @staticmethod
    def determine_density(items: List[Dict[str, Any]], config: LayoutConfig) -> str:
        """Determine content density classification."""
        if not items:
            return "sparse"
        
        num_items = len(items)
        max_allowed = config.max_bullets
        
        if num_items <= max_allowed * 0.5:
            return "sparse"
        elif num_items <= max_allowed * 0.8:
            return "balanced"
        else:
            return "dense"
    
    @staticmethod
    def should_split_slide(items: List[Dict[str, Any]], config: LayoutConfig) -> bool:
        """Determine if slide content should be split into multiple slides."""
        if not items:
            return False
        
        # Too many items
        if len(items) > config.max_bullets + 2:
            return True
        
        # Total word count too high
        total_words = sum(len(str(item.get('text', '')).split()) for item in items)
        if total_words > config.max_bullets * config.max_words_per_bullet * 1.5:
            return True
        
        return False


# =============================================================================
# DECK BUILDER
# =============================================================================

class DeckBuilder:
    """
    Constructs a validated DeckSpec from raw LLM output.
    Ensures all constraints are satisfied.
    """
    
    def __init__(self, theme_name: str = "corporate_blue"):
        self.validator = DeckValidator()
        self.font_calculator = FontSizeCalculator()
        self.theme_name = theme_name
        self._slide_ids: Set[str] = set()
        self._intent_counts: Dict[SlideIntent, int] = {}
    
    def build(
        self,
        raw_outline: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> DeckSpec:
        """
        Build a complete DeckSpec from raw LLM outline.
        """
        self._slide_ids.clear()
        self._intent_counts.clear()
        
        slides = []
        
        # Ensure we have a cover slide
        if not self._has_cover(raw_outline):
            cover_slide = self._create_cover_slide(metadata)
            slides.append(cover_slide)
            # Mark COVER as used to prevent duplicates
            self._intent_counts[SlideIntent.COVER] = 1
        
        # Process each raw slide
        for i, raw_slide in enumerate(raw_outline):
            slide_spec = self._process_slide(raw_slide, i, metadata)
            if slide_spec:
                slides.append(slide_spec)
        
        # Ensure we have exactly ONE closing slide (Thank You style)
        # Remove any extra closing-type slides first
        closing_count = sum(1 for s in slides if s.intent == SlideIntent.CLOSING)
        if closing_count > 1:
            # Keep only the last closing slide
            first_closing_found = False
            filtered = []
            for s in slides:
                if s.intent == SlideIntent.CLOSING:
                    if not first_closing_found:
                        first_closing_found = True
                        # Skip first one, keep for later
                        continue
                filtered.append(s)
            slides = filtered
        
        # Add closing if missing
        if not self._has_closing(slides):
            closing_slide = self._create_closing_slide(metadata, len(slides))
            slides.append(closing_slide)
            self._intent_counts[SlideIntent.CLOSING] = 1
        
        # Validate and fix
        is_valid, errors, warnings = self.validator.validate(slides)
        
        # Renumber slides
        for i, slide in enumerate(slides):
            slide.slide_number = i + 1
        
        return DeckSpec(
            deck_id=str(uuid.uuid4()),
            title=metadata.get('title', 'Presentation'),
            subtitle=metadata.get('subtitle'),
            author=metadata.get('author'),
            created_at=datetime.now().isoformat(),
            theme_name=self.theme_name,
            primary_color=metadata.get('primary_color', '#1e3a5f'),
            secondary_color=metadata.get('secondary_color', '#2d5a87'),
            accent_color=metadata.get('accent_color', '#e07b39'),
            core_message=metadata.get('core_message', ''),
            presentation_type=metadata.get('presentation_type', 'explanatory'),
            target_audience=metadata.get('target_audience', 'general'),
            slides=slides,
            is_valid=is_valid,
            validation_errors=errors + warnings,
        )
    
    def _process_slide(
        self,
        raw: Dict[str, Any],
        index: int,
        metadata: Dict[str, Any]
    ) -> Optional[SlideSpec]:
        """Process a single raw slide into a SlideSpec."""
        
        # Determine intent
        intent_str = raw.get('intent', 'concept')
        try:
            intent = SlideIntent(intent_str)
        except ValueError:
            intent = SlideIntent.KEY_POINTS
        
        # Check singleton constraint
        if intent in SINGLETON_INTENTS and intent in self._intent_counts:
            # Skip duplicate singleton
            return None
        
        self._intent_counts[intent] = self._intent_counts.get(intent, 0) + 1
        
        # Get layout config
        config = INTENT_LAYOUT_CONFIG.get(intent, INTENT_LAYOUT_CONFIG[SlideIntent.CONCEPT])
        
        # Process content
        title = raw.get('title', raw.get('claim', f'Slide {index + 1}'))
        subtitle = raw.get('subtitle')
        body_points = self._process_body_points(raw.get('body_points', []), config)
        
        # Calculate font sizes
        title_font_size = self.font_calculator.calculate_title_size(title, intent, config)
        body_font_size = self.font_calculator.calculate_body_size(body_points, intent, config)
        
        # Determine density
        density = self.font_calculator.determine_density(body_points, config)
        
        # Determine section
        section = self._determine_section(intent)
        
        # Generate unique ID
        slide_id = self._generate_slide_id(intent)
        
        # Get image keywords - prioritize title content over generic intent keywords
        title_keywords = self._extract_keywords_from_title(title)
        topic_keywords = metadata.get('keywords', [])[:2]
        base_keywords = INTENT_IMAGE_KEYWORDS.get(intent, ["business", "professional"])
        # Title keywords first, then topic, then base
        image_keywords = title_keywords[:3] + topic_keywords[:2] + base_keywords[:2]
        image_keywords = list(dict.fromkeys(image_keywords))[:5]  # Remove duplicates, limit to 5
        
        # Extract extra data for special layouts (comparison, etc.)
        extra_data = {}
        if intent == SlideIntent.COMPARISON:
            # Extract comparison-specific fields
            extra_data['left_header'] = raw.get('left_header')
            extra_data['right_header'] = raw.get('right_header')
            extra_data['left_column'] = raw.get('left_column', [])
            extra_data['right_column'] = raw.get('right_column', [])
        
        # Preserve any additional fields from LLM
        for key in ['metrics', 'statistics', 'quote', 'source', 'highlights']:
            if key in raw:
                extra_data[key] = raw[key]
        
        return SlideSpec(
            slide_id=slide_id,
            slide_number=index + 1,
            section=section,
            intent=intent,
            claim=raw.get('claim', title),
            title=title[:100],
            subtitle=subtitle[:150] if subtitle else None,
            body_points=body_points,
            speaker_notes=raw.get('speaker_notes', raw.get('speaker_note')),
            layout_type=config.layout_type,
            title_font_size=title_font_size,
            body_font_size=body_font_size,
            density=density,
            image_role=config.image_role,
            image_keywords=image_keywords,
            image_url=None,  # To be filled by image service
            accent_color=None,  # Use theme default
            transition_hint=raw.get('transition_to_next'),
            estimated_speaking_time=self._estimate_speaking_time(title, body_points),
            extra_data=extra_data,
        )
    
    def _process_body_points(
        self,
        raw_points: List,
        config: LayoutConfig
    ) -> List[Dict[str, Any]]:
        """Process and validate body points."""
        processed = []
        
        # Ensure raw_points is a list
        if raw_points is None:
            raw_points = []
        
        for i, point in enumerate(raw_points[:config.max_bullets + 2]):
            if isinstance(point, dict):
                text = point.get('text', '')
                priority = point.get('priority', 'normal')
                level = point.get('level', 0)
            else:
                text = str(point)
                priority = 'normal'
                level = 0
            
            # Enforce word limit
            words = text.split()
            if len(words) > config.max_words_per_bullet:
                text = ' '.join(words[:config.max_words_per_bullet])
            
            processed.append({
                'text': text,
                'priority': priority,
                'level': min(level, 1),  # Max 1 level of nesting
            })
        
        return processed
    
    def _determine_section(self, intent: SlideIntent) -> str:
        """Determine which section a slide belongs to."""
        for section_name, section_def in DECK_STRUCTURE.items():
            if intent in section_def.allowed_intents:
                return section_name
        return "core_content"
    
    def _generate_slide_id(self, intent: SlideIntent) -> str:
        """Generate a unique slide ID."""
        base_id = f"slide_{intent.value}_{self._intent_counts[intent]}"
        while base_id in self._slide_ids:
            base_id += "_" + str(uuid.uuid4())[:4]
        self._slide_ids.add(base_id)
        return base_id
    
    def _has_cover(self, raw_outline: List[Dict]) -> bool:
        """Check if outline already has a cover slide."""
        for raw in raw_outline[:2]:  # Only check first 2
            intent = raw.get('intent', '')
            if intent in ['cover', 'title', 'hero']:
                return True
        return False
    
    def _has_closing(self, slides: List[SlideSpec]) -> bool:
        """Check if slides have a proper closing slide (Thank You style)."""
        # Only CLOSING intent counts as true closing
        # SUMMARY and CALL_TO_ACTION are content slides, not Thank You slides
        for slide in slides[-3:]:  # Check last 3 slides
            if slide.intent == SlideIntent.CLOSING:
                return True
        return False
    
    def _create_cover_slide(self, metadata: Dict[str, Any]) -> SlideSpec:
        """Create a cover slide."""
        config = INTENT_LAYOUT_CONFIG[SlideIntent.COVER]
        title = metadata.get('title', 'Presentation')
        
        return SlideSpec(
            slide_id="slide_cover_1",
            slide_number=1,
            section="opening",
            intent=SlideIntent.COVER,
            claim=title,
            title=title,
            subtitle=metadata.get('subtitle'),
            body_points=[],
            speaker_notes="Welcome and introduce the topic.",
            layout_type="hero",
            title_font_size=config.title_font_range[1],
            body_font_size=config.body_font_range[1],
            density="sparse",
            image_role=ImageRole.HERO,
            image_keywords=["professional", "modern", "abstract"],
            image_url=None,
            accent_color=None,
            transition_hint="Begin with impact",
            estimated_speaking_time=30,
            extra_data={},
        )
    
    def _create_closing_slide(self, metadata: Dict[str, Any], slide_count: int) -> SlideSpec:
        """Create a closing slide."""
        config = INTENT_LAYOUT_CONFIG[SlideIntent.CLOSING]
        
        return SlideSpec(
            slide_id=f"slide_closing_{slide_count + 1}",
            slide_number=slide_count + 1,
            section="closing",
            intent=SlideIntent.CLOSING,
            claim="Thank You",
            title="Thank You",
            subtitle="Questions & Discussion",
            body_points=[],
            speaker_notes="Thank the audience and invite questions.",
            layout_type="closing",
            title_font_size=config.title_font_range[1],
            body_font_size=config.body_font_range[1],
            density="sparse",
            image_role=ImageRole.DECORATIVE,
            image_keywords=["thank you", "questions", "discussion"],
            image_url=None,
            accent_color=None,
            transition_hint="End with appreciation",
            estimated_speaking_time=30,
            extra_data={},
        )
    
    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """Extract meaningful keywords from slide title for image search."""
        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this',
            'that', 'these', 'those', 'it', 'its', 'their', 'your', 'our', 'how',
            'what', 'when', 'where', 'why', 'which', 'who', 'whom', 'whose',
            'across', 'through', 'into', 'over', 'under', 'about', 'between',
            'unlocking', 'transformative', 'key', 'main', 'important', 'critical',
            'exploring', 'understanding', 'leveraging', 'driving', 'enabling',
            'up', 'down', 'out', 'off', 'away', 'back'
        }
        
        # Extract words, filter stop words, and prioritize longer meaningful words
        words = title.lower().split()
        keywords = []
        
        for word in words:
            # Clean punctuation
            clean_word = ''.join(c for c in word if c.isalnum())
            
            # Skip short words and stop words
            if len(clean_word) > 2 and clean_word not in stop_words:
                keywords.append(clean_word)
        
        # Sort by word length (longer words tend to be more specific)
        keywords.sort(key=lambda x: -len(x))
        
        return keywords[:5]  # Return top 5 most meaningful keywords
    
    def _estimate_speaking_time(self, title: str, body_points: List[Dict]) -> int:
        """Estimate speaking time in seconds."""
        # ~150 words per minute = 2.5 words per second
        word_count = len(title.split())
        for point in body_points:
            word_count += len(point.get('text', '').split())
        
        # Add time for transitions and explanation
        base_time = word_count / 2.5
        return max(30, int(base_time * 2))  # Double for explanation


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'SlideIntent',
    'ImageRole',
    'SectionDefinition',
    'LayoutConfig',
    'SlideSpec',
    'DeckSpec',
    'DeckValidator',
    'FontSizeCalculator',
    'DeckBuilder',
    'DECK_STRUCTURE',
    'SINGLETON_INTENTS',
    'INTENT_LAYOUT_CONFIG',
    'INTENT_IMAGE_ROLE',
    'INTENT_IMAGE_KEYWORDS',
]

