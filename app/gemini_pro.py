import json
from typing import List

from google import genai
from google.genai import types

from .config import settings
from .schemas import PanelOutline, StoryPanel


def _get_client():
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    return genai.Client(
        api_key=settings.GEMINI_API_KEY
    )


def generate_story(
    outline: List[PanelOutline],
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> List[StoryPanel]:

    client = _get_client()

    outline_json = json.dumps(
        [
            panel.model_dump()
            for panel in outline
        ],
        indent=2,
    )

    prompt = f"""
You are the professional comic-story writer for ComicCraft.

Create the final narration and dialogue for this comic.

ORIGINAL STORY:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

PANEL OUTLINE:
{outline_json}

For every panel create:

- panel_number
- title
- scene_description
- caption
- narration
- dialogue
- image_prompt

Writing requirements:

1. Create exactly {settings.NUM_PANELS} panels.
2. Keep the story coherent from beginning to ending.
3. Maintain character consistency.
4. Make dialogue natural.
5. Keep captions short.
6. Keep narration suitable for a comic.
7. Do not create additional panels.
8. Keep the image prompt visually descriptive.
9. Return only the requested structured JSON.
"""

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_STORY_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[StoryPanel],
            ),
        )
    except Exception as exc:
        raise RuntimeError(
            f"Gemini story generation failed: {exc}"
        ) from exc

    # Use Gemini SDK's structured response when available.
    if getattr(response, "parsed", None):
        try:
            parsed = response.parsed

            panels = []

            for item in parsed:
                if isinstance(item, StoryPanel):
                    panels.append(item)
                else:
                    panels.append(
                        StoryPanel.model_validate(item)
                    )

            if not panels:
                raise RuntimeError(
                    "Gemini returned an empty comic story."
                )

            # Ensure sequential panel numbering.
            for index, panel in enumerate(panels, start=1):
                panel.panel_number = index

            return panels

        except Exception as exc:
            raise RuntimeError(
                f"Could not process Gemini's structured story: {exc}"
            ) from exc

    # Fallback for SDK responses where .parsed is unavailable.
    text = getattr(response, "text", None)

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response for the comic story."
        )

    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned invalid JSON for the comic story."
        ) from exc

    if not isinstance(data, list):
        raise RuntimeError(
            "Gemini story response was not a list."
        )

    panels = []

    for item in data:
        panels.append(
            StoryPanel.model_validate(item)
        )

    if not panels:
        raise RuntimeError(
            "Gemini returned an empty comic story."
        )

    # Ensure sequential panel numbering.
    for index, panel in enumerate(panels, start=1):
        panel.panel_number = index

    return panels