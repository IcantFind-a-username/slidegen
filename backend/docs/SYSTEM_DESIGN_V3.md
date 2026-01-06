# SlideGen V3 - System Design Document

## Executive Summary

SlideGen V3 treats presentation generation as a **layout-constrained, design-aware rendering problem**, not simple text output. The system enforces strict structural rules, intelligent typography, and consistent visual identity.

---

## 1. Diagnosis of Current Problems

### 1.1 Structural Problems
| Problem | Root Cause | Impact |
|---------|-----------|--------|
| Duplicate ending slides | No uniqueness constraint on closing intents | Unprofessional, redundant |
| Missing cover slide | No mandatory section enforcement | Poor first impression |
| Random slide order | No narrative flow validation | Confusing, hard to follow |

### 1.2 Layout & Typography Problems
| Problem | Root Cause | Impact |
|---------|-----------|--------|
| Static font sizes | No content-aware sizing | Text overflow or too sparse |
| Inconsistent density | No limits on bullets/words | Some slides overloaded |
| No visual emphasis | All text treated equally | Key points get lost |
| Monotonous layouts | Same template for all intents | Boring, "machine-generated" feel |

### 1.3 Visual Design Problems
| Problem | Root Cause | Impact |
|---------|-----------|--------|
| No images | Image integration not designed | Text-heavy, dull slides |
| Rigid style | No theme system | Looks like "default PowerPoint" |
| No visual identity | Colors/fonts not coordinated | Inconsistent, unprofessional |

---

## 2. System-Level Design Principles

### 2.1 Constraint-First Architecture
```
Every design decision is CONSTRAINED by explicit rules:
- Structural constraints → Deck must have cover, body, closing
- Uniqueness constraints → No duplicate singleton intents
- Density constraints → Max bullets, max words per bullet
- Layout constraints → Each intent maps to specific layout
```

### 2.2 Intent-Driven Rendering
```
Each slide has a COMMUNICATIVE INTENT:
- Intent determines WHAT to render (content type)
- Intent determines HOW to render (layout, typography, images)
- Intent prevents REPETITION (tracked globally)
```

### 2.3 Design System Integration
```
Visual decisions are SYSTEMATIC, not ad-hoc:
- Color palette defined per theme
- Typography scale with clear hierarchy
- Spacing system for consistent alignment
- Image roles mapped to intents
```

---

## 3. Deck Structure & Repetition Control

### 3.1 Mandatory Deck Structure

```python
DECK_STRUCTURE = {
    "opening": {
        "required": True,
        "allowed_intents": ["cover"],
        "min_slides": 1,
        "max_slides": 1,
        "order": 0
    },
    "framing": {
        "required": True,
        "allowed_intents": ["agenda", "vision", "context"],
        "min_slides": 1,
        "max_slides": 2,
        "order": 1
    },
    "core_content": {
        "required": True,
        "allowed_intents": ["concept", "framework", "comparison", 
                          "case_study", "data_insight", "key_points"],
        "min_slides": 2,
        "max_slides": 8,
        "order": 2
    },
    "analysis": {
        "required": False,
        "allowed_intents": ["implications", "benefits", "risks"],
        "min_slides": 0,
        "max_slides": 3,
        "order": 3
    },
    "forward_looking": {
        "required": False,
        "allowed_intents": ["future", "recommendations"],
        "min_slides": 0,
        "max_slides": 2,
        "order": 4
    },
    "closing": {
        "required": True,
        "allowed_intents": ["summary", "call_to_action", "closing"],
        "min_slides": 1,
        "max_slides": 2,
        "order": 5
    }
}
```

### 3.2 Uniqueness Constraints

```python
# These intents can appear AT MOST ONCE
SINGLETON_INTENTS = {
    "cover",        # Only one title slide
    "agenda",       # Only one roadmap
    "summary",      # Only one recap
    "call_to_action",  # Only one CTA
    "closing"       # Only one thank-you
}

# These intents CANNOT appear consecutively
NO_CONSECUTIVE_INTENTS = {
    "data_insight",  # Data needs variety
    "case_study",    # Cases need context between them
    "comparison"     # Comparisons need setup
}
```

### 3.3 Why This Prevents Repetition

| Constraint | What It Prevents | How It Works |
|------------|------------------|--------------|
| Singleton intents | Duplicate conclusions | System tracks which singletons are used |
| Section structure | Random ordering | Each section has defined position |
| No-consecutive rule | Back-to-back same slides | Validator flags violations |
| Unique claims | Duplicate titles | Title hashing detects near-duplicates |

---

## 4. Typography & Font Adaptation Strategy

### 4.1 Font Size Calculation Algorithm

```python
def calculate_title_size(title: str, intent: SlideIntent) -> int:
    """
    Title font adapts based on character count.
    
    Algorithm:
    - Short (< 30 chars): Use maximum size
    - Medium (30-50 chars): Linear interpolation
    - Long (> 50 chars): Use minimum size
    """
    config = INTENT_LAYOUT_CONFIG[intent]
    min_size, max_size = config.title_font_range
    
    if len(title) < 30:
        return max_size
    elif len(title) < 50:
        ratio = (len(title) - 30) / 20
        return int(max_size - ratio * (max_size - min_size))
    else:
        return min_size


def calculate_body_size(items: List, intent: SlideIntent) -> int:
    """
    Body font adapts based on:
    1. Number of items
    2. Average words per item
    
    Algorithm combines two factors:
    - item_factor: Fewer items → larger font
    - word_factor: Shorter bullets → larger font
    """
    config = INTENT_LAYOUT_CONFIG[intent]
    min_size, max_size = config.body_font_range
    
    # Factor 1: Item count
    if len(items) <= 2:
        item_factor = 1.0
    elif len(items) <= 4:
        item_factor = 0.7
    else:
        item_factor = 0.4
    
    # Factor 2: Word count
    avg_words = sum(len(item.text.split()) for item in items) / len(items)
    if avg_words <= 6:
        word_factor = 1.0
    elif avg_words <= 10:
        word_factor = 0.8
    else:
        word_factor = 0.6
    
    # Combined
    combined = (item_factor + word_factor) / 2
    return int(min_size + combined * (max_size - min_size))
```

### 4.2 Automatic Slide Splitting Rules

```python
def should_split_slide(items: List, config: LayoutConfig) -> bool:
    """
    Split when:
    1. Item count exceeds max + 2 (hard limit)
    2. Total word count exceeds 1.5x maximum
    """
    if len(items) > config.max_bullets + 2:
        return True
    
    total_words = sum(len(item.text.split()) for item in items)
    max_words = config.max_bullets * config.max_words_per_bullet
    
    if total_words > max_words * 1.5:
        return True
    
    return False
```

### 4.3 Intent-Specific Limits

| Intent | Max Bullets | Max Words/Bullet | Title Range | Body Range |
|--------|-------------|------------------|-------------|------------|
| cover | 0 | 0 | 40-56pt | 18-24pt |
| vision | 2 | 12 | 36-48pt | 18-24pt |
| concept | 4 | 12 | 24-32pt | 16-20pt |
| framework | 5 | 10 | 22-28pt | 14-18pt |
| comparison | 4 | 8 | 22-28pt | 14-18pt |
| data_insight | 3 | 8 | 22-28pt | 14-18pt |
| closing | 0 | 0 | 36-48pt | 18-24pt |

---

## 5. Image Integration Strategy

### 5.1 Intent to Image Role Mapping

```python
INTENT_IMAGE_ROLE = {
    # Hero images (large, impactful)
    "cover": "hero",
    "vision": "hero",
    "future": "hero",
    "call_to_action": "hero",
    
    # Illustrative (explains concept)
    "concept": "illustrative",
    "case_study": "illustrative",
    "context": "illustrative",
    
    # Decorative (adds visual interest)
    "agenda": "decorative",
    "implications": "decorative",
    "summary": "decorative",
    "closing": "decorative",
    
    # Icons (small symbolic)
    "framework": "icon",
    "comparison": "icon",
    "key_points": "icon",
    "benefits": "icon",
    "risks": "icon",
    
    # Data visualization (generated)
    "data_insight": "data_viz",
}
```

### 5.2 Image Placement Rules

```python
IMAGE_POSITIONS = {
    "background": {
        "left": 0, "top": 0,
        "width": 13.33, "height": 7.5,
        "opacity": 0.3  # Dimmed for readability
    },
    "right": {
        "left": 8.0, "top": 1.5,
        "width": 4.5, "height": 5.0,
        "opacity": 1.0
    },
    "left": {
        "left": 0.5, "top": 1.5,
        "width": 4.5, "height": 5.0,
        "opacity": 1.0
    },
    "corner": {
        "left": 11.0, "top": 0.3,
        "width": 2.0, "height": 1.5,
        "opacity": 0.8
    }
}
```

### 5.3 Keyword Generation for Search

```python
def get_image_keywords(intent: SlideIntent, slide_title: str) -> List[str]:
    """
    Keywords combine:
    1. Intent-specific base keywords
    2. Topic keywords from title
    """
    base_keywords = INTENT_IMAGE_KEYWORDS[intent]  # e.g., ["vision", "future"]
    topic_keywords = extract_nouns(slide_title)[:2]  # e.g., ["AI", "healthcare"]
    
    return base_keywords[:3] + topic_keywords
```

---

## 6. Style & Theme System

### 6.1 Theme Color Palettes

```python
THEME_PALETTES = {
    "corporate_blue": {
        "primary": "#1e3a5f",      # Dark blue - headers
        "secondary": "#2d5a87",    # Medium blue - backgrounds
        "accent": "#e07b39",       # Orange - CTAs, emphasis
        "background": "#ffffff",   # White
        "surface": "#f8fafc",      # Light gray - cards
        "text_primary": "#1e293b", # Dark - main text
        "text_secondary": "#64748b", # Gray - captions
        "text_on_primary": "#ffffff",
        "text_on_accent": "#ffffff",
    },
    "modern_dark": {
        "primary": "#0f172a",
        "secondary": "#1e293b",
        "accent": "#38bdf8",       # Cyan accent
        "background": "#0f172a",
        "surface": "#1e293b",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "text_on_primary": "#ffffff",
        "text_on_accent": "#0f172a",
    },
    # ... more themes
}
```

### 6.2 Typography Scale

```python
TYPOGRAPHY_SPEC = {
    "heading_font": "Calibri Light",
    "body_font": "Calibri",
    "mono_font": "Consolas",
    
    "sizes": {
        "hero": 48,     # Title slides
        "h1": 36,       # Section headers
        "h2": 28,       # Slide titles
        "h3": 24,       # Subtitles
        "h4": 20,       # Emphasized body
        "body": 16,     # Normal text
        "caption": 12,  # Small text
    },
    
    "line_height_heading": 1.1,
    "line_height_body": 1.5,
}
```

### 6.3 Visual Hierarchy

| Level | Purpose | Size | Weight | Color |
|-------|---------|------|--------|-------|
| Hero | Main message | 48pt | Bold | Primary |
| Primary | Key claims | 28pt | Bold | Text Primary |
| Secondary | Supporting | 18pt | Regular | Text Primary |
| Tertiary | Captions | 12pt | Regular | Text Secondary |
| Accent | CTAs, emphasis | 16pt | Bold | Accent |

---

## 7. Structured Intermediate Representation

### 7.1 SlideSpec (Single Slide)

```json
{
  "slide_id": "slide_concept_1",
  "slide_number": 3,
  "section": "core_content",
  
  "intent": "concept",
  "claim": "AI transforms healthcare by enabling predictive diagnostics",
  
  "title": "AI Transforms Healthcare Through Predictive Diagnostics",
  "subtitle": "From reactive to proactive patient care",
  "body_points": [
    {
      "text": "Machine learning analyzes patient data patterns",
      "priority": "high",
      "level": 0
    },
    {
      "text": "Early disease detection improves outcomes by 40%",
      "priority": "critical",
      "level": 0
    },
    {
      "text": "Reduces diagnostic errors and healthcare costs",
      "priority": "normal",
      "level": 1
    }
  ],
  "speaker_notes": "Explain the shift from reactive to predictive medicine...",
  
  "layout_type": "standard",
  "title_font_size": 28,
  "body_font_size": 18,
  "density": "balanced",
  
  "image_role": "illustrative",
  "image_keywords": ["AI", "healthcare", "concept", "illustration"],
  "image_url": null,
  "image_position": "right",
  
  "transition_hint": "This leads us to examine the framework...",
  "estimated_speaking_time": 90
}
```

### 7.2 DeckSpec (Full Presentation)

```json
{
  "deck_id": "d8f3a2b1-4c5e-6f7a-8b9c-0d1e2f3a4b5c",
  "title": "The Impact of AI on Healthcare",
  "subtitle": "A Strategic Overview",
  "author": "SlideGen",
  "created_at": "2024-01-15T10:30:00Z",
  
  "theme": {
    "name": "corporate_blue",
    "primary_color": "#1e3a5f",
    "secondary_color": "#2d5a87",
    "accent_color": "#e07b39"
  },
  
  "core_message": "AI is revolutionizing healthcare delivery",
  "presentation_type": "explanatory",
  "target_audience": "Healthcare executives",
  
  "slides": [
    { "slide_id": "slide_cover_1", "intent": "cover", "..." },
    { "slide_id": "slide_vision_1", "intent": "vision", "..." },
    { "slide_id": "slide_concept_1", "intent": "concept", "..." },
    { "slide_id": "slide_framework_1", "intent": "framework", "..." },
    { "slide_id": "slide_case_study_1", "intent": "case_study", "..." },
    { "slide_id": "slide_data_insight_1", "intent": "data_insight", "..." },
    { "slide_id": "slide_risks_1", "intent": "risks", "..." },
    { "slide_id": "slide_summary_1", "intent": "summary", "..." },
    { "slide_id": "slide_closing_1", "intent": "closing", "..." }
  ],
  
  "is_valid": true,
  "validation_errors": []
}
```

---

## 8. Before vs After Comparison

### Example: "Benefits" Slide

#### BEFORE (Naive Version)
```
Title: Benefits
Bullets:
- There are many benefits to using AI in healthcare
- It can help doctors make better decisions
- Costs may be reduced in the long run
- Patient outcomes could potentially improve
- Technology is advancing rapidly in this field
- Many hospitals are starting to adopt these systems
- The future looks promising for AI healthcare applications

Font: All 16pt, same weight
Layout: Standard bullet list
Visual: None
```

**Problems:**
- ❌ Title is a label, not a claim
- ❌ 7 bullets (exceeds density limits)
- ❌ Bullets are vague ("could potentially")
- ❌ No visual hierarchy
- ❌ No visual elements

#### AFTER (System-Designed Version)
```
Title: Three Measurable Benefits Justify Immediate Adoption
Subtitle: Proven ROI across 500+ hospital implementations

Bullets:
★ 40% reduction in diagnostic errors [critical]
  Evidence from Mayo Clinic pilot program
● 25% decrease in operational costs [high]
● 3x faster patient throughput [high]

Font: Title 28pt bold, Body 18pt
Layout: Standard with accent indicators
Visual: Stats highlight boxes + relevant icon
```

**Improvements:**
- ✅ Title is a specific claim with number
- ✅ 3 bullets (within limits)
- ✅ Concrete metrics ("40%", "25%", "3x")
- ✅ Priority hierarchy (★ vs ●)
- ✅ Supporting evidence included

### Why the Improved Version is Better

| Aspect | Naive | Improved | Reason |
|--------|-------|----------|--------|
| **Title** | Label | Claim | Audience knows takeaway immediately |
| **Density** | 7 items | 3 items | Scannable in 3 seconds |
| **Specificity** | Vague | Metrics | Credible, memorable |
| **Hierarchy** | None | Priority markers | Eye knows where to focus |
| **Typography** | Uniform | Scaled | Important stands out |

---

## 9. Implementation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER REQUEST                                │
│              "Create presentation about AI in healthcare"       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  1. OUTLINE GENERATION                          │
│  - Analyze user intent                                          │
│  - Generate narrative arc                                       │
│  - Assign intents to each slide                                 │
│  - Validate against DECK_STRUCTURE                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  2. CONTENT GENERATION                          │
│  - For each slide:                                              │
│    - Get intent-specific guidance                               │
│    - Get density limits from config                             │
│    - Generate content with LLM                                  │
│    - Enforce word/bullet limits                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  3. DECK BUILDING                               │
│  - Create SlideSpec for each slide                              │
│  - Calculate font sizes                                         │
│  - Determine layout type                                        │
│  - Validate uniqueness constraints                              │
│  - Add cover if missing                                         │
│  - Add closing if missing                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  4. IMAGE PROCESSING (optional)                 │
│  - For each slide:                                              │
│    - Determine image role from intent                           │
│    - Generate search keywords                                   │
│    - Search/download images                                     │
│    - Determine placement position                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  5. RENDERING                                   │
│  - Load theme (colors, fonts, spacing)                          │
│  - For each SlideSpec:                                          │
│    - Select layout template                                     │
│    - Apply typography (calculated sizes)                        │
│    - Place content in regions                                   │
│    - Add images/shapes                                          │
│    - Add visual hierarchy elements                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OUTPUT: .PPTX FILE                          │
│  - Validated structure                                          │
│  - Professional typography                                      │
│  - Consistent theme                                             │
│  - Optional images                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Key Files

| File | Purpose |
|------|---------|
| `deck_architect.py` | Structure validation, intent classification, font calculation |
| `design_system.py` | Themes, colors, typography, spacing rules |
| `image_service.py` | Image search, caching, placement |
| `smart_typography.py` | Content-aware font sizing |
| `presentation_pipeline.py` | Integrated generation workflow |
| `renderer_pro.py` | PPTX rendering with layout templates |

---

## Summary

SlideGen V3 transforms presentation generation from "text output" to "intelligent design system" through:

1. **Mandatory Structure** - Every deck follows a validated narrative arc
2. **Intent-Driven Rendering** - Each slide's purpose determines its layout
3. **Adaptive Typography** - Font sizes respond to content density
4. **Design System** - Consistent colors, fonts, spacing across all slides
5. **Image Integration** - Semantically aligned visuals (when enabled)
6. **Validation** - Structural rules prevent common generation errors

The result: Presentations that look **designed** rather than **generated**.

