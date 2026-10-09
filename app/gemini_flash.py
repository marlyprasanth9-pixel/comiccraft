import json
from typing import List

from google import genai

from .config import settings
from .schemas import PanelOutline


def _get_client():
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    return genai.Client(
        api_key=settings.GEMINI_API_KEY
    )


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> List[PanelOutline]:

    client = _get_client()

    prompt = f"""
You are the story-outline engine for an AI comic creator.

Create exactly {settings.NUM_PANELS} comic panels.

USER STORY:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

Requirements:

1. Create a coherent beginning, middle, and ending.
2. Keep the same main character throughout.
3. Each panel must advance the story.
4. Make the visual descriptions detailed enough for an image generator.
5. Do not include image-generation parameters.
6. Do not use markdown.
7. Return valid JSON only.

Return this exact JSON structure:

[
  {{
    "panel_number": 1,
    "title": "...",
    "scene_description": "...",
    "image_prompt": "..."
  }}
]
"""

    response = client.models.generate_content(
        model=settings.GEMINI_OUTLINE_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
    )

    text = response.text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned invalid JSON for the comic outline."
        ) from exc

    if not isinstance(data, list):
        raise RuntimeError(
            "Gemini outline response was not a list."
        )

    panels = []

    for item in data:
        panels.append(
            PanelOutline.model_validate(item)
        )

    # Ensure sequential numbering
    for index, panel in enumerate(panels, start=1):
        panel.panel_number = index

    return panels
