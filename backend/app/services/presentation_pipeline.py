"""
Presentation Pipeline - Integrated Generation System

This module integrates all components:
1. LLM Content Generation (LLMServiceV2)
2. Deck Architecture (deck_architect)
3. Design System (design_system)
4. Image Integration (image_service)
5. Smart Typography (smart_typography)
6. Rendering (renderer_pro)

This is the main entry point for generating professional presentations.

Author: SlideGen Team
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Local imports
from .deck_architect import (
    SlideIntent, ImageRole, DeckBuilder, DeckValidator,
    FontSizeCalculator, SlideSpec, DeckSpec,
    INTENT_LAYOUT_CONFIG, SINGLETON_INTENTS
)
from .design_system import (
    DesignSystem, ThemePreset, VisualHierarchy, LayoutTemplate
)
from .image_service import ImageService, BatchImageProcessor


# =============================================================================
# ENHANCED OUTLINE PROMPT
# =============================================================================

ENHANCED_OUTLINE_PROMPT = """You are an expert presentation architect.

## TOPIC
{topic}

## REQUIREMENTS
- {slide_count} slides total
- Presentation type: {presentation_type}

## MANDATORY DECK STRUCTURE
Your deck MUST follow this structure:

1. **OPENING** (exactly 1 slide):
   - intent: "cover" - Title slide with main topic and subtitle

2. **FRAMING** (1-2 slides):
   - intent: "agenda" OR "vision" - Set context and roadmap

3. **CORE CONTENT** (2-8 slides):
   - Use intents: "concept", "framework", "comparison", "case_study", "data_insight", "key_points"
   - Each slide must have a UNIQUE claim
   - NO duplicate intents in a row

4. **ANALYSIS** (0-3 slides):
   - Use intents: "implications", "benefits", "risks"
   
5. **FORWARD-LOOKING** (0-2 slides):
   - Use intents: "future", "recommendations"

6. **CLOSING** (1-2 slides):
   - intent: "summary" or "call_to_action" - ONE only
   - intent: "closing" - Thank you slide

## RULES
1. "cover" intent: EXACTLY ONCE, always first
2. "closing" intent: EXACTLY ONCE, always last
3. "summary", "call_to_action": AT MOST ONE each
4. NO duplicate slide titles
5. Every title must be a CLAIM (statement), not a label

## VALID INTENTS
- cover, agenda, vision, context
- concept, framework, comparison, case_study, data_insight, key_points
- implications, benefits, risks
- future, recommendations
- summary, call_to_action, closing

## OUTPUT FORMAT
{{
  "core_message": "The ONE thing audience should remember",
  "presentation_type": "{presentation_type}",
  "outline": [
    {{
      "slide_number": 1,
      "intent": "cover",
      "claim": "Main title of presentation",
      "subtitle": "Optional subtitle"
    }},
    {{
      "slide_number": 2,
      "intent": "vision",
      "claim": "Why this topic matters now",
      "key_points": ["Point 1", "Point 2"]
    }}
  ]
}}

Output ONLY valid JSON.
"""


ENHANCED_SLIDE_PROMPT = """Generate content for slide {slide_number} of {total_slides}.

## SLIDE SPEC
- Intent: {intent}
- Claim: {claim}
- Previous: {previous}

## CONTENT LIMITS (STRICT)
- Title: max 12 words
- Subtitle: max 15 words (optional)
- Bullets: max {max_bullets} items
- Words per bullet: max {max_words} words

## INTENT GUIDANCE
{intent_guidance}

## OUTPUT FORMAT
{{
  "title": "Strong claim (max 12 words)",
  "subtitle": "Optional clarification or null",
  "body_points": [
    {{
      "text": "Concise point (max {max_words} words)",
      "priority": "critical|high|normal"
    }}
  ],
  "speaker_notes": "What to say about this slide",
  "left_header": "For comparison slides only",
  "right_header": "For comparison slides only",
  "left_column": ["Items for left column"],
  "right_column": ["Items for right column"]
}}

Output ONLY valid JSON.
"""


# =============================================================================
# INTENT GUIDANCE TEMPLATES
# =============================================================================

INTENT_GUIDANCE = {
    "cover": """
    This is the title slide. Focus on:
    - A compelling, memorable title
    - An optional subtitle that adds context
    - NO bullet points
    """,
    
    "vision": """
    Frame why this topic matters. Focus on:
    - Big picture impact
    - Relevance to audience
    - Emotional hook
    - 2-3 key points maximum
    """,
    
    "agenda": """
    Provide a roadmap. Focus on:
    - Clear section previews
    - What audience will learn
    - Numbered or sequential items
    """,
    
    "concept": """
    Define and explain. Focus on:
    - Clear definition
    - Key characteristics
    - Concrete examples
    - Why it matters
    """,
    
    "framework": """
    Explain methodology/process. Focus on:
    - Step-by-step breakdown
    - How components connect
    - Practical application
    """,
    
    "comparison": """
    Contrast two options. Focus on:
    - Clear criteria
    - Objective differences  
    - Balanced presentation
    
    REQUIRED FOR COMPARISON SLIDES:
    - "left_header": Name of first option (e.g., "Traditional Approach")
    - "right_header": Name of second option (e.g., "AI-Powered Method")
    - "left_column": ["Point 1 about option A", "Point 2 about option A", "Point 3"]
    - "right_column": ["Point 1 about option B", "Point 2 about option B", "Point 3"]
    
    Each column should have 3-4 parallel comparison points.
    """,
    
    "case_study": """
    Present real-world evidence. Focus on:
    - Specific example
    - Context and challenge
    - Solution and outcome
    - Lessons learned
    """,
    
    "data_insight": """
    Present key metrics. Focus on:
    - Specific numbers
    - Trend or comparison
    - Business impact
    - Visual potential
    """,
    
    "context": """
    Set the stage. Focus on:
    - Background information
    - Current state or situation
    - Why this matters now
    - Audience relevance
    """,
    
    "key_points": """
    Highlight main arguments. Focus on:
    - 3-4 core points
    - Clear, memorable statements
    - Supporting evidence
    - Logical ordering
    """,
    
    "implications": """
    Explain consequences. Focus on:
    - Direct impacts
    - Indirect effects
    - Stakeholder considerations
    - Action implications
    """,
    
    "benefits": """
    Present advantages. Focus on:
    - Specific benefits
    - Quantified value where possible
    - Stakeholder impact
    - Competitive advantage
    """,
    
    "risks": """
    Address challenges. Focus on:
    - Specific risks
    - Mitigation strategies
    - Realistic assessment
    """,
    
    "recommendations": """
    Suggest actions. Focus on:
    - Clear, actionable steps
    - Prioritized list
    - Timeline if applicable
    - Resource requirements
    """,
    
    "future": """
    Look ahead. Focus on:
    - Trends and predictions
    - Opportunities
    - Call to preparation
    """,
    
    "summary": """
    Synthesize key points. Focus on:
    - 3-5 key takeaways
    - Reinforce core message
    - Memorable phrasing
    """,
    
    "call_to_action": """
    Drive action. Focus on:
    - Clear next steps
    - Specific asks
    - Urgency or motivation
    """,
    
    "closing": """
    Thank and conclude. Focus on:
    - Appreciation
    - Contact info or Q&A invitation
    - Final thought
    """,
}


# =============================================================================
# PRESENTATION PIPELINE
# =============================================================================

class PresentationPipeline:
    """
    Integrated pipeline for professional presentation generation.
    
    Workflow:
    1. Analyze user request
    2. Generate structured outline (with deck architecture constraints)
    3. Generate slide content (with typography hints)
    4. Process images (optional)
    5. Build validated DeckSpec
    6. Return for rendering
    """
    
    def __init__(
        self,
        theme: ThemePreset = ThemePreset.CORPORATE_BLUE,
        enable_images: bool = False
    ):
        self.theme = theme
        self.design = DesignSystem(theme)
        self.deck_builder = DeckBuilder(theme.value)
        self.validator = DeckValidator()
        self.font_calculator = FontSizeCalculator()
        self.enable_images = enable_images
        
        if enable_images:
            self.image_service = ImageService(enable_web_search=True)
            self.image_processor = BatchImageProcessor(self.image_service)
        else:
            self.image_service = None
            self.image_processor = None
    
    def generate(
        self,
        user_request: str,
        slide_count: int = 8,
        presentation_type: str = "explanatory"
    ) -> DeckSpec:
        """
        Generate a complete, validated presentation.
        
        Args:
            user_request: User's description of desired presentation
            slide_count: Target number of slides
            presentation_type: "explanatory", "persuasive", "analytical", "pitch"
        
        Returns:
            Complete DeckSpec ready for rendering
        """
        print("=" * 60)
        print("SLIDEGEN V3 - Integrated Pipeline")
        print("=" * 60)
        
        # Enforce limits
        slide_count = max(4, min(slide_count, 15))
        
        # Step 1: Generate outline
        print("\n[1/4] Generating structured outline...")
        outline, metadata = self._generate_outline(
            user_request, slide_count, presentation_type
        )
        print(f"  Generated {len(outline)} slide outlines")
        
        # Step 2: Generate slide content
        print("\n[2/4] Generating slide content...")
        slides_raw = self._generate_all_slides(outline, metadata)
        print(f"  Generated {len(slides_raw)} slides")
        
        # Step 3: Build deck with validation
        print("\n[3/4] Building and validating deck...")
        deck_spec = self.deck_builder.build(slides_raw, metadata)
        
        if deck_spec.validation_errors:
            print(f"  Warnings: {len(deck_spec.validation_errors)}")
            for err in deck_spec.validation_errors[:3]:
                print(f"    - {err}")
        
        # Step 4: Process images (if enabled)
        if self.enable_images and self.image_processor:
            print("\n[4/4] Processing images...")
            image_specs = self.image_processor.process_deck(
                [s.to_dict() for s in deck_spec.slides]
            )
            print(f"  Processed {len(image_specs)} images")
            
            # Attach images to slides
            for slide in deck_spec.slides:
                if slide.slide_id in image_specs:
                    slide.image_url = image_specs[slide.slide_id].url
        else:
            print("\n[4/4] Skipping image processing (disabled)")
        
        print(f"\n✓ Generated {len(deck_spec.slides)} slides")
        print("=" * 60)
        
        return deck_spec
    
    def _generate_outline(
        self,
        user_request: str,
        slide_count: int,
        presentation_type: str
    ) -> Tuple[List[Dict], Dict]:
        """Generate structured outline using LLM."""
        from .LLMServiceV2 import call_llm, safe_json_parse
        
        prompt = ENHANCED_OUTLINE_PROMPT.format(
            topic=user_request,
            slide_count=slide_count,
            presentation_type=presentation_type
        )
        
        response = call_llm(prompt)
        data = safe_json_parse(response)
        
        outline = data.get('outline', [])
        metadata = {
            'title': user_request[:50],
            'subtitle': None,
            'core_message': data.get('core_message', ''),
            'presentation_type': data.get('presentation_type', presentation_type),
            'keywords': self._extract_keywords(user_request),
        }
        
        return outline, metadata
    
    def _generate_all_slides(
        self,
        outline: List[Dict],
        metadata: Dict
    ) -> List[Dict]:
        """Generate content for all slides."""
        from .LLMServiceV2 import call_llm, safe_json_parse
        
        slides = []
        previous = "None"
        
        for i, item in enumerate(outline):
            intent = item.get('intent', 'concept')
            claim = item.get('claim', f'Slide {i+1}')
            
            # Get layout config for this intent
            try:
                intent_enum = SlideIntent(intent)
                config = INTENT_LAYOUT_CONFIG.get(intent_enum)
            except ValueError:
                intent_enum = SlideIntent.KEY_POINTS
                config = INTENT_LAYOUT_CONFIG[SlideIntent.KEY_POINTS]
            
            if config is None:
                config = INTENT_LAYOUT_CONFIG[SlideIntent.KEY_POINTS]
            
            # Generate content
            prompt = ENHANCED_SLIDE_PROMPT.format(
                slide_number=i + 1,
                total_slides=len(outline),
                intent=intent,
                claim=claim,
                previous=previous,
                max_bullets=config.max_bullets,
                max_words=config.max_words_per_bullet,
                intent_guidance=INTENT_GUIDANCE.get(intent, "Create compelling content.")
            )
            
            try:
                response = call_llm(prompt)
                content = safe_json_parse(response)
            except Exception as e:
                print(f"    Warning: Slide {i+1} generation failed: {e}")
                content = self._create_fallback_slide(intent, claim)
            
            # Merge outline data with generated content
            slide_data = {
                **item,
                **content,
                'intent': intent,
            }
            
            slides.append(slide_data)
            previous = content.get('title', claim)[:50]
        
        return slides
    
    def _create_fallback_slide(self, intent: str, claim: str) -> Dict:
        """Create fallback slide when generation fails."""
        return {
            'title': claim[:60],
            'subtitle': None,
            'body_points': [
                {'text': 'Key point to be developed', 'priority': 'high'}
            ],
            'speaker_notes': 'Elaborate on this topic.',
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from user request."""
        # Simple extraction - could be enhanced with NLP
        words = text.lower().split()
        stop_words = {'a', 'an', 'the', 'is', 'are', 'about', 'for', 'on', 'in', 'to', 'of', 'and', 'or'}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return keywords[:5]
    
    def to_renderer_format(self, deck_spec: DeckSpec) -> Dict[str, Any]:
        """
        Convert DeckSpec to format expected by renderer.
        
        This maintains backward compatibility with existing renderer.
        """
        slides = []
        
        for slide in deck_spec.slides:
            # Map intent to slide_type
            slide_type = self._intent_to_slide_type(slide.intent)
            
            # Get extra data (for comparison slides, etc.)
            extra = slide.extra_data if hasattr(slide, 'extra_data') else {}
            
            slide_data = {
                'slide_type': slide_type,
                'title': slide.title or '',
                'subtitle': slide.subtitle,
                'intent': slide.intent.value,
                'body_points': slide.body_points if slide.body_points else [],
                'speaker_notes': slide.speaker_notes,
                
                # Layout hints
                'layout_type': slide.layout_type,
                'title_font_size': slide.title_font_size,
                'body_font_size': slide.body_font_size,
                'density': slide.density,
                
                # Image data
                'image_role': slide.image_role.value if slide.image_role else 'none',
                'image_url': slide.image_url,
                
                # For comparison slides - get from extra_data
                'left_header': extra.get('left_header'),
                'right_header': extra.get('right_header'),
                'left_column': extra.get('left_column', []),
                'right_column': extra.get('right_column', []),
                
                # For metrics/data slides
                'metrics': extra.get('metrics'),
                'statistics': extra.get('statistics'),
            }
            
            slides.append(slide_data)
        
        return {
            'metadata': {
                'title': deck_spec.title,
                'subtitle': deck_spec.subtitle,
                'theme': deck_spec.theme_name,
                'language': 'en',
            },
            'slides': slides,
        }
    
    def _intent_to_slide_type(self, intent: SlideIntent) -> str:
        """Map SlideIntent to renderer slide_type."""
        mapping = {
            SlideIntent.COVER: 'title',
            SlideIntent.AGENDA: 'content',
            SlideIntent.VISION: 'title',
            SlideIntent.CONTEXT: 'content',
            SlideIntent.CONCEPT: 'content',
            SlideIntent.FRAMEWORK: 'content',
            SlideIntent.COMPARISON: 'comparison',
            SlideIntent.CASE_STUDY: 'content',
            SlideIntent.DATA_INSIGHT: 'content',
            SlideIntent.KEY_POINTS: 'content',
            SlideIntent.IMPLICATIONS: 'content',
            SlideIntent.BENEFITS: 'content',
            SlideIntent.RISKS: 'content',
            SlideIntent.FUTURE: 'content',
            SlideIntent.RECOMMENDATIONS: 'content',
            SlideIntent.SUMMARY: 'content',
            SlideIntent.CALL_TO_ACTION: 'title',
            SlideIntent.CLOSING: 'closing',
        }
        return mapping.get(intent, 'content')


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def generate_professional_presentation(
    user_request: str,
    slide_count: int = 8,
    theme: str = "corporate_blue",
    enable_images: bool = False
) -> Dict[str, Any]:
    """
    Convenience function for generating professional presentations.
    
    Args:
        user_request: User's description of desired presentation
        slide_count: Target number of slides (4-15)
        theme: Theme name ("corporate_blue", "modern_dark", etc.)
        enable_images: Whether to fetch images from web
    
    Returns:
        Presentation data ready for rendering
    """
    try:
        theme_preset = ThemePreset(theme)
    except ValueError:
        theme_preset = ThemePreset.CORPORATE_BLUE
    
    pipeline = PresentationPipeline(
        theme=theme_preset,
        enable_images=enable_images
    )
    
    deck_spec = pipeline.generate(
        user_request=user_request,
        slide_count=slide_count,
        presentation_type="explanatory"
    )
    
    return pipeline.to_renderer_format(deck_spec)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'PresentationPipeline',
    'generate_professional_presentation',
    'INTENT_GUIDANCE',
]

