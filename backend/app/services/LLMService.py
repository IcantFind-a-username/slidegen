"""
LLM Service - Content Generation

Handles OpenAI GPT calls for generating presentation content.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def truncate(text, max_len):
    if len(text) <= max_len:
        return text
    return text[:max_len]


from openai import OpenAI

client = OpenAI()

def call_llm(prompt, temperature=0.3):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You generate structured presentation slides."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    return response.choices[0].message.content



# JSON parsing with error recovery
import json
import re

def repair_json_with_llm(bad_json):
    prompt = f"""
Fix the following JSON. Output valid JSON only.

{bad_json}
"""
    fixed = call_llm(prompt, temperature=0)
    return json.loads(fixed)

def safe_json_parse(text):
    try:
        return json.loads(text)
    except Exception:
        cleaned = re.sub(r"```json|```", "", text).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return repair_json_with_llm(cleaned)



# Semantic text compression
def shorten_text_semantically(text, max_len):
    if len(text) <= max_len:
        return text

    prompt = f"""
Rewrite the following text to be <= {max_len} characters
while preserving its original meaning.

Text:
{text}

Output JSON only:
{{ "text": "..." }}
"""
    try:
        result = safe_json_parse(call_llm(prompt, temperature=0))
        rewritten = result["text"]
        if len(rewritten) <= max_len:
            return rewritten
    except Exception:
        pass

    # Final fallback
    return text[:max_len - 3] + "..."



# Extract slide count from user request
def extract_slide_count_fallback(text):
    match = re.search(
        r'(\d+)\s*(slide|slides|page|pages)',
        text,
        re.I
    )
    if match:
        return int(match.group(1))
    return None



# Parse user intent
def parse_user_intent(user_request):
    prompt = f"""
Extract presentation intent.

Output JSON only:
{{
  "presentation_type": "pitch|academic|corporate|general",
  "target_audience": "string",
  "slide_count": number or null,
  "tone": "concise|business|academic"
}}

User request:
{user_request}
"""
    intent = safe_json_parse(call_llm(prompt))

    # Fallback: parse slide count from request
    if intent.get("slide_count") is None:
        fallback = extract_slide_count_fallback(user_request)
        if fallback:
            intent["slide_count"] = fallback
    # =============================

    return intent



#metadata(title+theme)
def generate_metadata(user_request):
    prompt = f"""
Generate presentation metadata.

Rules:
- title ≤ 50 characters
- theme ∈ [corporate_blue, modern_green, elegant_purple, warm_orange, tech_dark]

Output JSON only:
{{
  "title": "...",
  "theme": "..."
}}

User request:
{user_request}
"""
    return safe_json_parse(call_llm(prompt))



# Generate outline draft
def generate_outline_with_llm(intent):
    topic = intent.get("topic") or intent.get("title") or "Presentation Topic"
    tone = intent.get("tone", "neutral")

    target_slides = intent.get("slide_count")

    prompt = f"""
You are planning the structure of a presentation.

Topic:
{topic}

Rules:
- Target slide count: {target_slides if target_slides else "flexible"}
- Must include:
  - exactly 1 title slide
  - at least 2 section slides
  - at least 1 two_column slide
  - exactly 1 closing slide
- Other slides should be content slides

Output JSON only:
{{
  "outline": [
    {{ "slide_type": "title", "title": "..." }},
    {{ "slide_type": "section", "title": "..." }},
    {{ "slide_type": "content", "title": "..." }}
  ]
}}
"""
    response = call_llm(prompt, temperature=0.3)
    parsed = safe_json_parse(response)

    return parsed["outline"]


# Normalize outline structure
ALLOWED_SLIDE_TYPES = {
    "title", "section", "content", "two_column", "closing"
}

def normalize_outline(outline, target_slides=None):
    normalized = []

    for item in outline:
        slide_type = item.get("slide_type", "content")
        title = item.get("title", "Untitled")

        if slide_type not in ALLOWED_SLIDE_TYPES:
            slide_type = "content"

        normalized.append((slide_type, title))

    # Enforce structure rules
    
    # 1. Ensure single title slide
    titles = [i for i, s in enumerate(normalized) if s[0] == "title"]
    if not titles:
        normalized.insert(0, ("title", "Presentation Title"))
    elif len(titles) > 1:
        first = titles[0]
        normalized = [
            s if i == first else ("content", s[1])
            for i, s in enumerate(normalized)
        ]

    # 2. Ensure closing slide
    if not any(s[0] == "closing" for s in normalized):
        normalized.append(("closing", "Conclusion"))

    # 3. Ensure at least one two_column slide (if enough space)
    if target_slides is None or target_slides >= 4:
        if not any(s[0] == "two_column" for s in normalized):
            for i, (t, _) in enumerate(normalized):
                if t == "closing":
                    normalized.insert(i, ("two_column", "Comparison"))
                    break
            else:
                normalized.append(("two_column", "Comparison"))

    # 4. Control total slide count (order: title -> content -> closing)
    if target_slides is not None:
        fixed = []
        title_slides = [s for s in normalized if s[0] == "title"]
        section_slides = [s for s in normalized if s[0] == "section"]
        two_column_slides = [s for s in normalized if s[0] == "two_column"]
        closing_slides = [s for s in normalized if s[0] == "closing"]
        content_slides = [
            s for s in normalized
            if s[0] not in ("title", "section", "two_column", "closing")
        ]

        # Title slide first
        fixed.extend(title_slides)

        # Calculate remaining slots
        remaining_slots = target_slides - len(title_slides) - len(closing_slides)
        if remaining_slots < 0:
            remaining_slots = 0

        # Add section, two_column, content slides
        if section_slides and remaining_slots > 0:
            fixed.extend(section_slides[:remaining_slots])
            remaining_slots -= len(section_slides[:remaining_slots])
        if two_column_slides and remaining_slots > 0:
            fixed.extend(two_column_slides[:remaining_slots])
            remaining_slots -= len(two_column_slides[:remaining_slots])
        if content_slides and remaining_slots > 0:
            fixed.extend(content_slides[:remaining_slots])
        # Fill remaining with content slides
        while len(fixed) < target_slides - len(closing_slides):
            fixed.append(("content", "Additional Content"))

        # Closing slide last
        fixed.extend(closing_slides)

        normalized = fixed

    return normalized


##outline(slide_type+title)
def generate_outline(intent):
    raw_outline = generate_outline_with_llm(intent)
    outline = normalize_outline(raw_outline, intent.get("slide_count"))

    print("USER NUM_SLIDES:", intent.get("slide_count"))
    print("RAW OUTLINE LEN:", len(raw_outline))
    print("FINAL OUTLINE LEN:", len(outline))
    print("DEBUG slide_count:", intent.get("slide_count"))


    return outline






# Generate body points for content slides
ROLE_TO_LEVEL = {
    "main": 0,
    "support": 1,
    "detail": 2
}

ROLE_TO_PRIORITY = {
    "main": "critical",
    "support": "high",
    "detail": "normal"
}
def enforce_body_point_count(points, title, tone, min_n=4, max_n=6):
    if len(points) >= min_n and len(points) <= max_n:
        return points[:max_n]

    if len(points) > max_n:
        return points[:max_n]

    # If not enough, generate more with LLM
    need = min_n - len(points)

    prompt = f"""
Generate {need} additional body points for this slide.

Rules:
- Each ≤ 100 characters
- Do NOT repeat existing points
- Tone: {tone}

Slide title:
{title}

Existing points:
{[p["text"] for p in points]}

Output JSON only:
{{ "points": [{{"text": "...", "role": "support"}}] }}
"""

    parsed = safe_json_parse(call_llm(prompt))
    new_points = []

    for p in parsed["points"]:
        new_points.append({
            "text": truncate(p["text"], 100),
            "level": 1,
            "priority": "high"
        })

    return (points + new_points)[:max_n]



def generate_body_points(title, content_text, tone):
    prompt = f"""
Generate 4–6 body points for a presentation slide.

Rules:
- Each text ≤ 100 characters
- Assign a semantic role to each point:
  - main: core takeaway of the slide
  - support: explanation or reasoning
  - detail: example or detail
- Use provided content if available
- Tone: {tone}

Slide title:
{title}

Content:
{content_text or "N/A"}

Output JSON only:
{{
  "points": [
    {{ "text": "...", "role": "main" }}
  ]
}}
"""
    parsed = safe_json_parse(call_llm(prompt))
    raw_points = parsed["points"]

    body_points = []
    for p in raw_points:
        role = p.get("role", "support")

        body_points.append({
            "text": shorten_text_semantically(p["text"], 100),
            "level": ROLE_TO_LEVEL.get(role, 1),
            "priority": ROLE_TO_PRIORITY.get(role, "normal")
        })
    body_points = enforce_body_point_count(body_points,title,tone)

    return body_points



# Generate title/section/closing slides
def generate_subtitle(title, hint):
    prompt = f"""
Generate a subtitle.

Rules:
- ≤ 80 characters

Title:
{title}

Hint:
{hint}

Output JSON only:
{{"subtitle": "..."}}
"""
    return safe_json_parse(call_llm(prompt))["subtitle"]




# Generate two_column slides
def generate_two_column(title, content_text):
    prompt = f"""
Generate a two-column slide.

Rules:
- Each column 2–3 bullets
- Each bullet ≤ 100 characters

Title:
{title}

Content:
{content_text or "N/A"}

Output JSON only:
{{
  "left_column": ["...", "..."],
  "right_column": ["...", "..."]
}}
"""
    return safe_json_parse(call_llm(prompt))




#pipeline
def generate_presentation(user_request, content_text=None):
    intent = parse_user_intent(user_request)
    metadata = generate_metadata(user_request)
    outline = generate_outline(intent)

    slides = []

    for slide_type, title in outline:
        if slide_type == "title":
            raw_title = metadata["title"]
            raw_subtitle = generate_subtitle(metadata["title"], "Opening")

            slides.append({
                "slide_type": "title",
                "title": shorten_text_semantically(raw_title, 50),
                "subtitle": shorten_text_semantically(raw_subtitle, 80)
            })

        elif slide_type == "section":
            raw_subtitle = generate_subtitle(title, "Section Overview")
            slides.append({
                "slide_type": "section",
                "title": shorten_text_semantically(title, 50),
                "subtitle": shorten_text_semantically(raw_subtitle, 80)
            })
            # =====================

        elif slide_type == "content":
            slides.append({
                "slide_type": "content",
                "title": shorten_text_semantically(title, 50),
                "body_points": generate_body_points(title, content_text, intent["tone"])
            })

        elif slide_type == "two_column":
            cols = generate_two_column(title, content_text)
            slides.append({
                "slide_type": "two_column",
                "title": shorten_text_semantically(title, 50),
                "left_column": cols["left_column"],
                "right_column": cols["right_column"]
            })

        elif slide_type == "closing":
            raw_subtitle = generate_subtitle(title, "Wrap-up")
            slides.append({
                "slide_type": "closing",
                "title": shorten_text_semantically(title, 50),
                "subtitle": shorten_text_semantically(raw_subtitle, 80)
            })

    return {
        "metadata": metadata,
        "slides": slides
    }


if __name__ == "__main__":
    #test1
    generate_presentation(
        user_request="Create a 8-slide to introduce blockchain"
    )

    #test2
    generate_presentation(
        user_request="Create a slide to introduce blockchain"
    )

    #test3
    generate_presentation(
        user_request="Create a 3-slide investor pitch deck",
        content_text="""
    We are building an LLM-based slide generation system.
    Target users are consultants and students.
    Key value: time saving and structure consistency.
    """)