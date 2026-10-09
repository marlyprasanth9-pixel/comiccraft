from typing import List

from .schemas import StoryPanel


def build_comic_layout(
    panels: List[StoryPanel],
    image_paths: List[str],
):

    if len(panels) != len(image_paths):
        raise ValueError(
            "Number of panels and images must match."
        )

    layout = []

    for panel, image_path in zip(
        panels,
        image_paths,
    ):
        layout.append(
            {
                "panel_number": panel.panel_number,
                "title": panel.title,
                "image_path": image_path,
                "scene_description": panel.scene_description,
                "caption": panel.caption,
                "narration": panel.narration,
                "dialogue": panel.dialogue,
                "image_prompt": panel.image_prompt,
            }
        )

    return layout