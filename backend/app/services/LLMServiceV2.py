"""
LLMService V2 - Production-Grade PPT Generation

This module implements a sophisticated slide generation system that treats
PPT creation as a layout-constrained, narrative-driven rendering problem.

Key Improvements:
1. Slide Intent Classification - Every slide has explicit communicative intent
2. Strong Claims - Each slide conveys one clear message with supporting evidence
3. Strict Text Density Control - Enforced limits for professional presentations
4. Narrative Flow - Logical story progression across slides
5. Visual Structure - Layout-aware content generation

Author: SlideGen Team
"""

import os
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from enum import Enum

# Load environment variables
load_dotenv()

client = OpenAI()


# =============================================================================
# SLIDE INTENT CLASSIFICATION
# =============================================================================

class SlideIntent(str, Enum):
    """
    Slide Intent defines the communicative purpose of each slide.
    Each intent maps to specific structural patterns and layouts.
    """
    VISION = "vision"                    # Big idea, framing, why this matters
    AGENDA = "agenda"                    # Overview of presentation structure
    CONCEPT_OVERVIEW = "concept_overview" # What is X? Core definition
    FRAMEWORK = "framework"              # How it works, process, methodology
    COMPARISON = "comparison"            # A vs B, pros/cons, trade-offs
    CASE_EXAMPLE = "case_example"        # Real-world application, evidence
    DATA_INSIGHT = "data_insight"        # Key statistics, metrics, findings
    IMPLICATIONS = "implications"        # So what? Impact and consequences
    RISKS_CHALLENGES = "risks_challenges" # Obstacles, limitations, concerns
    FUTURE_DIRECTIONS = "future_directions" # What's next, roadmap, predictions
    SUMMARY_TAKEAWAYS = "summary_takeaways" # Key points to remember
    CALL_TO_ACTION = "call_to_action"    # What should audience do?


# Intent to Layout mapping
INTENT_LAYOUT_MAP = {
    SlideIntent.VISION: "title_emphasis",
    SlideIntent.AGENDA: "numbered_list",
    SlideIntent.CONCEPT_OVERVIEW: "content_focus",
    SlideIntent.FRAMEWORK: "structured_blocks",
    SlideIntent.COMPARISON: "two_column",
    SlideIntent.CASE_EXAMPLE: "content_focus",
    SlideIntent.DATA_INSIGHT: "data_highlight",
    SlideIntent.IMPLICATIONS: "content_focus",
    SlideIntent.RISKS_CHALLENGES: "content_focus",
    SlideIntent.FUTURE_DIRECTIONS: "content_focus",
    SlideIntent.SUMMARY_TAKEAWAYS: "numbered_list",
    SlideIntent.CALL_TO_ACTION: "title_emphasis",
}

# Text density limits per intent
INTENT_DENSITY_LIMITS = {
    SlideIntent.VISION: {"max_bullets": 0, "max_words_per_bullet": 0, "emphasis": "title"},
    SlideIntent.AGENDA: {"max_bullets": 6, "max_words_per_bullet": 6, "emphasis": "list"},
    SlideIntent.CONCEPT_OVERVIEW: {"max_bullets": 4, "max_words_per_bullet": 10, "emphasis": "definition"},
    SlideIntent.FRAMEWORK: {"max_bullets": 5, "max_words_per_bullet": 8, "emphasis": "structure"},
    SlideIntent.COMPARISON: {"max_bullets": 3, "max_words_per_bullet": 8, "emphasis": "contrast"},
    SlideIntent.CASE_EXAMPLE: {"max_bullets": 4, "max_words_per_bullet": 10, "emphasis": "evidence"},
    SlideIntent.DATA_INSIGHT: {"max_bullets": 3, "max_words_per_bullet": 8, "emphasis": "numbers"},
    SlideIntent.IMPLICATIONS: {"max_bullets": 4, "max_words_per_bullet": 10, "emphasis": "consequence"},
    SlideIntent.RISKS_CHALLENGES: {"max_bullets": 4, "max_words_per_bullet": 10, "emphasis": "warning"},
    SlideIntent.FUTURE_DIRECTIONS: {"max_bullets": 4, "max_words_per_bullet": 10, "emphasis": "prediction"},
    SlideIntent.SUMMARY_TAKEAWAYS: {"max_bullets": 5, "max_words_per_bullet": 8, "emphasis": "recap"},
    SlideIntent.CALL_TO_ACTION: {"max_bullets": 3, "max_words_per_bullet": 8, "emphasis": "action"},
}


# =============================================================================
# LLM UTILITIES
# =============================================================================

def call_llm(prompt: str, system_prompt: str = None, temperature: float = 0.3) -> str:
    """Call OpenAI API with robust error handling."""
    if system_prompt is None:
        system_prompt = """You are an expert presentation designer and communication strategist.
You create slides that are clear, impactful, and professionally structured.
You understand that great presentations tell stories, not just convey information.
Every slide must have ONE clear message and support that message with evidence."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    return response.choices[0].message.content


def safe_json_parse(text: str) -> Dict[str, Any]:
    """Parse JSON with fallback cleaning."""
    try:
        return json.loads(text)
    except Exception:
        # Remove markdown code blocks
        cleaned = re.sub(r"```json\s*|```\s*", "", text).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            # Last resort: extract JSON object
            match = re.search(r'\{[\s\S]*\}', cleaned)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Could not parse JSON: {text[:200]}")


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def enforce_word_limit(text: str, max_words: int) -> str:
    """Truncate text to word limit while preserving meaning."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


# =============================================================================
# NARRATIVE STRUCTURE
# =============================================================================

NARRATIVE_TEMPLATES = {
    "explanatory": [
        SlideIntent.VISION,
        SlideIntent.AGENDA,
        SlideIntent.CONCEPT_OVERVIEW,
        SlideIntent.FRAMEWORK,
        SlideIntent.CASE_EXAMPLE,
        SlideIntent.IMPLICATIONS,
        SlideIntent.SUMMARY_TAKEAWAYS,
    ],
    "persuasive": [
        SlideIntent.VISION,
        SlideIntent.CONCEPT_OVERVIEW,
        SlideIntent.DATA_INSIGHT,
        SlideIntent.CASE_EXAMPLE,
        SlideIntent.COMPARISON,
        SlideIntent.CALL_TO_ACTION,
    ],
    "analytical": [
        SlideIntent.VISION,
        SlideIntent.AGENDA,
        SlideIntent.CONCEPT_OVERVIEW,
        SlideIntent.DATA_INSIGHT,
        SlideIntent.COMPARISON,
        SlideIntent.RISKS_CHALLENGES,
        SlideIntent.FUTURE_DIRECTIONS,
        SlideIntent.SUMMARY_TAKEAWAYS,
    ],
    "pitch": [
        SlideIntent.VISION,
        SlideIntent.CONCEPT_OVERVIEW,
        SlideIntent.FRAMEWORK,
        SlideIntent.DATA_INSIGHT,
        SlideIntent.CASE_EXAMPLE,
        SlideIntent.CALL_TO_ACTION,
    ],
}


# =============================================================================
# PRODUCTION-GRADE PROMPTS
# =============================================================================

MASTER_OUTLINE_PROMPT = """You are an expert presentation architect designing a high-impact slide deck.

## TOPIC
{topic}

## USER CONTEXT
{user_context}

## TARGET SLIDE COUNT
{slide_count} slides

## YOUR TASK
Design a presentation outline that follows a compelling NARRATIVE ARC.

## CRITICAL REQUIREMENTS

1. **STORY STRUCTURE**: Your presentation must tell a story:
   - Opening: Hook the audience, establish WHY this matters
   - Middle: Build understanding through logical progression
   - Closing: Synthesize insights and leave lasting impression

2. **SLIDE INTENTS**: Each slide MUST have one of these intents:
   - vision: Big idea that frames everything (use for opening)
   - agenda: Roadmap of what's coming (optional, for longer decks)
   - concept_overview: Core definition, "What is X?"
   - framework: How it works, process, methodology
   - comparison: A vs B, pros/cons analysis
   - case_example: Real-world evidence, application
   - data_insight: Key statistics or findings
   - implications: "So what?" - impact and consequences
   - risks_challenges: Obstacles and limitations
   - future_directions: What's next, predictions
   - summary_takeaways: Key points to remember
   - call_to_action: What should audience do?

3. **STRONG CLAIMS**: Every slide title must be a CLAIM, not a label.
   - BAD: "Artificial Intelligence" (label)
   - GOOD: "AI is reshaping every industry faster than any previous technology"
   - BAD: "Benefits" (generic)
   - GOOD: "Three benefits that justify immediate adoption"

4. **NARRATIVE FLOW**: Slides must connect logically:
   - Each slide should answer a question raised by the previous one
   - Avoid random jumps between topics
   - Build toward your conclusion

## OUTPUT FORMAT
Output valid JSON only:
{{
  "presentation_type": "explanatory|persuasive|analytical|pitch",
  "core_message": "The ONE thing you want audience to remember",
  "outline": [
    {{
      "slide_number": 1,
      "intent": "vision",
      "claim": "Strong statement that captures the main message",
      "supporting_question": "What question does this slide answer?",
      "transition_to_next": "How this leads to the next slide"
    }}
  ]
}}
"""


SLIDE_CONTENT_PROMPT = """You are crafting content for a single presentation slide.

## SLIDE CONTEXT
- Slide Number: {slide_number} of {total_slides}
- Intent: {intent}
- Claim/Title: {claim}
- Previous Slide: {previous_context}
- Presentation Topic: {topic}

## INTENT-SPECIFIC GUIDANCE
{intent_guidance}

## STRICT FORMATTING RULES

1. **ONE MESSAGE PER SLIDE**: Everything on this slide supports the claim in the title.

2. **TEXT DENSITY LIMITS**:
   - Maximum {max_bullets} bullet points
   - Maximum {max_words} words per bullet
   - Title must be under 12 words
   - Subtitle (if any) under 15 words

3. **BULLET STRUCTURE**:
   - Each bullet = ONE complete thought
   - Start with action verbs or strong nouns
   - NO sub-bullets (keep it flat)
   - Bullets should be scannable in 3 seconds

4. **LANGUAGE QUALITY**:
   - Specific > Generic
   - Active > Passive
   - Concrete > Abstract
   - "Reduces costs by 40%" > "Significantly reduces costs"

## OUTPUT FORMAT
Output valid JSON only:
{{
  "title": "The claim (under 12 words)",
  "subtitle": "Optional clarification (under 15 words, null if not needed)",
  "body_points": [
    {{
      "text": "Concise, impactful point",
      "role": "main|support|evidence",
      "priority": "critical|high|normal"
    }}
  ],
  "speaker_note": "What to SAY about this slide (not shown on slide)"
}}
"""


TWO_COLUMN_PROMPT = """Generate content for a COMPARISON slide with two columns.

## CONTEXT
- Topic: {topic}
- Claim/Title: {claim}
- Comparison Type: {comparison_type}

## STRICT RULES
1. Each column: 2-4 bullets maximum
2. Each bullet: 8 words maximum
3. Columns should be PARALLEL in structure
4. Contrast should be CLEAR and MEANINGFUL

## OUTPUT FORMAT
Output valid JSON only:
{{
  "title": "Comparison claim (under 12 words)",
  "left_header": "Left column label (2-3 words)",
  "right_header": "Right column label (2-3 words)",
  "left_column": ["Point 1", "Point 2", "Point 3"],
  "right_column": ["Point 1", "Point 2", "Point 3"],
  "key_insight": "The main takeaway from this comparison"
}}
"""


INTENT_GUIDANCE = {
    SlideIntent.VISION: """
This is a VISION slide - it sets the stage and captures attention.
- Focus on the BIG PICTURE, not details
- Create emotional resonance
- Make the audience care about what follows
- Can be a powerful question or bold statement
- Minimal text, maximum impact
""",
    SlideIntent.AGENDA: """
This is an AGENDA slide - it provides a roadmap.
- List 3-5 main sections/topics
- Keep items parallel in structure
- Each item should be intriguing, not generic
- Help audience anticipate the journey
""",
    SlideIntent.CONCEPT_OVERVIEW: """
This is a CONCEPT OVERVIEW slide - it defines the core idea.
- Answer "What is X?" clearly
- Provide a memorable definition
- Distinguish from similar concepts
- Set foundation for deeper discussion
""",
    SlideIntent.FRAMEWORK: """
This is a FRAMEWORK slide - it shows how things work.
- Present a clear structure or process
- Use numbered steps or named components
- Make relationships explicit
- Help audience build mental model
""",
    SlideIntent.COMPARISON: """
This is a COMPARISON slide - it contrasts two things.
- Make the contrast crystal clear
- Use parallel structure
- Highlight key differences
- Drive toward a conclusion about which/when/why
""",
    SlideIntent.CASE_EXAMPLE: """
This is a CASE EXAMPLE slide - it provides evidence.
- Use specific, real examples
- Include concrete details (names, numbers, outcomes)
- Connect example to main argument
- Make abstract concepts tangible
""",
    SlideIntent.DATA_INSIGHT: """
This is a DATA INSIGHT slide - it highlights key findings.
- Lead with the most surprising/important number
- Provide context for the data
- Explain what the data MEANS
- Less data, more insight
""",
    SlideIntent.IMPLICATIONS: """
This is an IMPLICATIONS slide - it answers "So what?"
- Connect findings to audience concerns
- Show practical consequences
- Make impact concrete and relevant
- Bridge from analysis to action
""",
    SlideIntent.RISKS_CHALLENGES: """
This is a RISKS/CHALLENGES slide - it addresses obstacles.
- Be honest but not alarmist
- Prioritize by importance
- Suggest how challenges can be addressed
- Build credibility through transparency
""",
    SlideIntent.FUTURE_DIRECTIONS: """
This is a FUTURE DIRECTIONS slide - it looks ahead.
- Be specific about timeline if possible
- Ground predictions in current trends
- Distinguish certain from uncertain
- Create sense of possibility
""",
    SlideIntent.SUMMARY_TAKEAWAYS: """
This is a SUMMARY slide - it reinforces key messages.
- Recap 3-5 most important points
- Use exact language from earlier slides if memorable
- Focus on what to REMEMBER, not everything covered
- Create sense of completeness
""",
    SlideIntent.CALL_TO_ACTION: """
This is a CALL TO ACTION slide - it drives action.
- Be specific about what to do
- Make action achievable
- Provide clear next step
- Create urgency without pressure
""",
}


# =============================================================================
# CORE GENERATION FUNCTIONS
# =============================================================================

def analyze_user_intent(user_request: str) -> Dict[str, Any]:
    """Analyze user request to understand presentation needs."""
    prompt = f"""Analyze this presentation request and extract key information.

User Request: {user_request}

Output JSON only:
{{
  "topic": "Main topic of the presentation",
  "presentation_type": "explanatory|persuasive|analytical|pitch",
  "target_audience": "Who will view this",
  "desired_slide_count": number or null,
  "tone": "formal|conversational|technical|inspirational",
  "key_constraints": ["any specific requirements mentioned"],
  "implicit_goals": ["what the user probably wants to achieve"]
}}
"""
    return safe_json_parse(call_llm(prompt))


def generate_narrative_outline(
    topic: str,
    user_context: str,
    slide_count: int,
    presentation_type: str = "explanatory"
) -> List[Dict[str, Any]]:
    """Generate a narrative-driven presentation outline."""
    
    prompt = MASTER_OUTLINE_PROMPT.format(
        topic=topic,
        user_context=user_context,
        slide_count=slide_count
    )
    
    result = safe_json_parse(call_llm(prompt, temperature=0.4))
    return result.get("outline", []), result.get("core_message", "")


def generate_slide_content(
    slide_info: Dict[str, Any],
    slide_number: int,
    total_slides: int,
    topic: str,
    previous_context: str = ""
) -> Dict[str, Any]:
    """Generate content for a single slide based on its intent."""
    
    intent = slide_info.get("intent", "concept_overview")
    claim = slide_info.get("claim", "Untitled Slide")
    
    # Get intent-specific limits and guidance
    try:
        intent_enum = SlideIntent(intent)
    except ValueError:
        intent_enum = SlideIntent.CONCEPT_OVERVIEW
    
    limits = INTENT_DENSITY_LIMITS.get(intent_enum, {"max_bullets": 5, "max_words_per_bullet": 10})
    guidance = INTENT_GUIDANCE.get(intent_enum, "")
    
    # Handle special slide types
    if intent_enum == SlideIntent.VISION:
        return generate_vision_slide(claim, topic)
    
    if intent_enum == SlideIntent.COMPARISON:
        return generate_comparison_slide(claim, topic)
    
    if intent_enum == SlideIntent.AGENDA:
        return generate_agenda_slide(claim, topic, total_slides)
    
    # Standard content slide
    prompt = SLIDE_CONTENT_PROMPT.format(
        slide_number=slide_number,
        total_slides=total_slides,
        intent=intent,
        claim=claim,
        previous_context=previous_context or "This is the first content slide",
        topic=topic,
        intent_guidance=guidance,
        max_bullets=limits["max_bullets"],
        max_words=limits["max_words_per_bullet"]
    )
    
    content = safe_json_parse(call_llm(prompt))
    
    # Enforce limits
    content = enforce_content_limits(content, limits)
    
    # Map to slide schema
    return {
        "slide_type": map_intent_to_slide_type(intent_enum),
        "intent": intent,
        "title": content.get("title", claim)[:80],
        "subtitle": content.get("subtitle"),
        "body_points": format_body_points(content.get("body_points", [])),
        "speaker_notes": content.get("speaker_note")
    }


def generate_vision_slide(claim: str, topic: str) -> Dict[str, Any]:
    """Generate a high-impact vision/title slide."""
    prompt = f"""Create an impactful opening slide for a presentation.

Topic: {topic}
Initial Claim: {claim}

Requirements:
- Title: A bold, memorable statement (under 10 words)
- Subtitle: Provides context or intrigue (under 12 words)
- This slide sets the tone for everything that follows
- Should create curiosity and establish stakes

Output JSON only:
{{
  "title": "Bold statement",
  "subtitle": "Context or intrigue"
}}
"""
    content = safe_json_parse(call_llm(prompt))
    return {
        "slide_type": "title",
        "intent": "vision",
        "title": content.get("title", claim)[:80],
        "subtitle": content.get("subtitle", "")[:120]
    }


def generate_comparison_slide(claim: str, topic: str) -> Dict[str, Any]:
    """Generate a two-column comparison slide."""
    prompt = TWO_COLUMN_PROMPT.format(
        topic=topic,
        claim=claim,
        comparison_type="contrast or trade-off analysis"
    )
    
    content = safe_json_parse(call_llm(prompt))
    
    # Format columns
    left_col = [{"text": enforce_word_limit(p, 8), "level": 0} for p in content.get("left_column", [])][:4]
    right_col = [{"text": enforce_word_limit(p, 8), "level": 0} for p in content.get("right_column", [])][:4]
    
    return {
        "slide_type": "two_column",
        "intent": "comparison",
        "title": content.get("title", claim)[:80],
        "left_header": content.get("left_header", "Option A"),
        "right_header": content.get("right_header", "Option B"),
        "left_column": left_col,
        "right_column": right_col
    }


def generate_agenda_slide(claim: str, topic: str, total_slides: int) -> Dict[str, Any]:
    """Generate an agenda/roadmap slide."""
    prompt = f"""Create an agenda slide for a {total_slides}-slide presentation.

Topic: {topic}

Requirements:
- List 3-5 main sections (not individual slides)
- Each item should be intriguing, not generic
- Use parallel structure
- Maximum 6 words per item

Output JSON only:
{{
  "title": "What We'll Cover (or similar)",
  "items": ["Section 1", "Section 2", "Section 3"]
}}
"""
    content = safe_json_parse(call_llm(prompt))
    
    items = content.get("items", [])[:6]
    body_points = [
        {"text": enforce_word_limit(item, 6), "level": 0, "priority": "high"}
        for item in items
    ]
    
    return {
        "slide_type": "content",
        "intent": "agenda",
        "title": content.get("title", "Today's Agenda")[:80],
        "body_points": body_points
    }


def generate_closing_slide(topic: str, core_message: str) -> Dict[str, Any]:
    """Generate a strong closing slide."""
    prompt = f"""Create a memorable closing slide.

Topic: {topic}
Core Message: {core_message}

Requirements:
- Title: Reinforce the core message or call to action
- Subtitle: Leave a lasting impression
- Should feel conclusive, not abrupt

Output JSON only:
{{
  "title": "Closing statement",
  "subtitle": "Final thought or call to action"
}}
"""
    content = safe_json_parse(call_llm(prompt))
    return {
        "slide_type": "closing",
        "intent": "call_to_action",
        "title": content.get("title", "Thank You")[:80],
        "subtitle": content.get("subtitle", "Questions & Discussion")[:120]
    }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def map_intent_to_slide_type(intent: SlideIntent) -> str:
    """Map slide intent to rendering slide type."""
    mapping = {
        SlideIntent.VISION: "title",
        SlideIntent.AGENDA: "content",
        SlideIntent.CONCEPT_OVERVIEW: "content",
        SlideIntent.FRAMEWORK: "content",
        SlideIntent.COMPARISON: "two_column",
        SlideIntent.CASE_EXAMPLE: "content",
        SlideIntent.DATA_INSIGHT: "content",
        SlideIntent.IMPLICATIONS: "content",
        SlideIntent.RISKS_CHALLENGES: "content",
        SlideIntent.FUTURE_DIRECTIONS: "content",
        SlideIntent.SUMMARY_TAKEAWAYS: "content",
        SlideIntent.CALL_TO_ACTION: "closing",
    }
    return mapping.get(intent, "content")


def enforce_content_limits(content: Dict[str, Any], limits: Dict[str, Any]) -> Dict[str, Any]:
    """Enforce text density limits on slide content."""
    max_bullets = limits.get("max_bullets", 5)
    max_words = limits.get("max_words_per_bullet", 10)
    
    # Limit bullet count
    if "body_points" in content:
        content["body_points"] = content["body_points"][:max_bullets]
        
        # Enforce word limit per bullet
        for point in content["body_points"]:
            if "text" in point:
                point["text"] = enforce_word_limit(point["text"], max_words)
    
    # Limit title length
    if "title" in content:
        content["title"] = enforce_word_limit(content["title"], 12)
    
    return content


def format_body_points(raw_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format body points to schema-compatible structure."""
    formatted = []
    
    role_to_level = {"main": 0, "support": 1, "evidence": 1, "detail": 2}
    role_to_priority = {"main": "critical", "support": "high", "evidence": "high", "detail": "normal"}
    
    for point in raw_points:
        role = point.get("role", "support")
        formatted.append({
            "text": point.get("text", "")[:100],
            "level": role_to_level.get(role, 1),
            "priority": point.get("priority", role_to_priority.get(role, "normal"))
        })
    
    return formatted


# =============================================================================
# MAIN GENERATION PIPELINE
# =============================================================================

def generate_presentation_v2(user_request: str, content_text: str = None) -> Dict[str, Any]:
    """
    Generate a high-quality presentation using the V2 pipeline.
    
    This function implements:
    1. Intent analysis to understand user needs
    2. Narrative-driven outline generation
    3. Intent-specific slide content generation
    4. Strict text density enforcement
    
    Args:
        user_request: User's description of desired presentation
        content_text: Optional additional content to incorporate
    
    Returns:
        Complete slidedeck JSON matching the schema
    """
    
    print("=" * 60)
    print("SLIDEGEN V2 - Production-Grade Generation")
    print("=" * 60)
    
    # Step 1: Analyze user intent
    print("\n[1/4] Analyzing user intent...")
    intent = analyze_user_intent(user_request)
    
    topic = intent.get("topic", user_request)
    presentation_type = intent.get("presentation_type", "explanatory")
    slide_count = intent.get("desired_slide_count") or 8
    
    # Enforce reasonable limits
    slide_count = max(4, min(slide_count, 15))
    
    print(f"  Topic: {topic}")
    print(f"  Type: {presentation_type}")
    print(f"  Target slides: {slide_count}")
    
    # Step 2: Generate narrative outline
    print("\n[2/4] Generating narrative outline...")
    user_context = f"""
User Request: {user_request}
Additional Content: {content_text or 'None provided'}
Target Audience: {intent.get('target_audience', 'General')}
Tone: {intent.get('tone', 'professional')}
"""
    
    outline, core_message = generate_narrative_outline(
        topic=topic,
        user_context=user_context,
        slide_count=slide_count,
        presentation_type=presentation_type
    )
    
    print(f"  Core message: {core_message}")
    print(f"  Outline slides: {len(outline)}")
    
    # Step 3: Generate slide content
    print("\n[3/4] Generating slide content...")
    slides = []
    previous_context = ""
    
    for i, slide_info in enumerate(outline):
        slide_num = i + 1
        print(f"  Slide {slide_num}: {slide_info.get('intent', 'content')} - {slide_info.get('claim', '')[:40]}...")
        
        slide_content = generate_slide_content(
            slide_info=slide_info,
            slide_number=slide_num,
            total_slides=len(outline),
            topic=topic,
            previous_context=previous_context
        )
        
        slides.append(slide_content)
        previous_context = f"Previous slide: {slide_content.get('title', '')}"
    
    # Ensure we have a closing slide
    if slides and slides[-1].get("slide_type") != "closing":
        print("  Adding closing slide...")
        closing = generate_closing_slide(topic, core_message)
        slides.append(closing)
    
    # Step 4: Generate metadata
    print("\n[4/4] Finalizing presentation...")
    metadata = {
        "title": topic[:50],
        "theme": "corporate_blue",
        "language": "en",
        "core_message": core_message,
        "presentation_type": presentation_type
    }
    
    result = {
        "metadata": metadata,
        "slides": slides
    }
    
    print(f"\n✓ Generated {len(slides)} slides successfully")
    print("=" * 60)
    
    return result


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

def generate_presentation(user_request: str, content_text: str = None) -> Dict[str, Any]:
    """
    Backward-compatible wrapper for generate_presentation_v2.
    
    This function maintains the same interface as the original LLMService
    while using the improved V2 generation pipeline.
    """
    return generate_presentation_v2(user_request, content_text)


# =============================================================================
# EXAMPLE & TESTING
# =============================================================================

if __name__ == "__main__":
    # Example usage
    test_request = "Create a 6-slide presentation about the impact of artificial intelligence on healthcare"
    
    result = generate_presentation_v2(test_request)
    
    print("\n" + "=" * 60)
    print("GENERATED PRESENTATION")
    print("=" * 60)
    print(json.dumps(result, indent=2))

